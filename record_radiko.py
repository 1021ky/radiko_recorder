import argparse
import base64
from datetime import datetime, timedelta, timezone
import ffmpeg
import logging
import m3u8
import os
import requests
from requests.exceptions import Timeout
import sys
import time

class RadikoRecorder(object):
    """Radikoの録音クラス"""

    _PLAYLIST_BASE_URL = 'https://rpaa.smartstream.ne.jp/so/playlist.m3u8'
    _DUMMY_LSID = '11111111111111111111111111111111111111' # Radiko APIの仕様で38桁の文字列が必要。

    def __init__(self, station, record_time, outfile):
        self._headers = self._make_headers()
        self._station = station
        self._record_time = record_time
        self._file = outfile

    def _make_headers(self):
        """HTTPリクエストのヘッダーを作成する"""
        headers = RadikoAuth().get_auththenticated_headers()
        headers['Connection']='keep-alive'
        logging.debug(f'headers: {headers}')
        return headers

    def _make_playlist_url(self):
        """再生情報取得用のPLAYLIST URLを作成する"""
        url = f'{RadikoRecorder._PLAYLIST_BASE_URL}?station_id={self._station}&l=15&lsid={RadikoRecorder._DUMMY_LSID}&type=b'
        logging.debug(f'playlist url:{url}')
        return url

    def _make_audio_headers(self):
        """音声取得用HTTPリクエストのヘッダーを作成する

        requests用のhttpヘッダーをもとにffmpeg用に文字列のHTTPリクエストヘッダーを作る。
        """
        header_list = [f'{k}: {v}'for k, v in self._headers.items()]
        audio_headers = '\r\n'.join(header_list)+'\r\n'
        logging.debug(f'audio headers: {audio_headers}')
        return audio_headers

    def _get_session_url(self):
        u = self._make_playlist_url()
        r = requests.get(url=u, headers=self._headers)
        if r.status_code != 200:
            logging.warning('failed to get session url')
            logging.warning(f'status_code:{r.status_code}')
            logging.warning(f'content:{r.content}')
            raise Exception('failed in radiko get session')
        # TODO use m3u8
        # ----playlist content----
        # b'#EXTM3U\n
        # #EXT-X-VERSION:6\n
        # #EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=52973,CODECS="mp4a.40.5"\n
        # https://rpaa.smartstream.ne.jp/medialist?session=HYcT8XSG58R5qeAhZDQwW6\n'
        session_url = str(r.content.splitlines()[-1].decode('utf-8'))
        logging.debug(f'session_url: {session_url}')
        return session_url

    def record(self):
        """録音する"""
        logging.debug('record start')
        session_url = self._get_session_url()
        end = datetime.now() + timedelta(minutes=self._record_time)
        recorded = set()
        while(datetime.now() <= end):
            query_time = int(datetime.now(tz=JST).timestamp() * 100)
            r = requests.get(url=f'{session_url}&_={query_time}',headers=self._headers)
            print(f'aac url:{session_url}&_={query_time}')
            # m3u8ファイルがとれないときはリトライすると取れるときがあるため待つ
            if r.status_code != 200:
                time.sleep(3.0)
                continue
            m3u8_text = str(r.content.decode('utf-8'))
            m3u8_obj = m3u8.loads(m3u8_text)
            m3u8_obj.segments.reverse() # 時刻昇順にする
            headers = self._make_audio_headers()
            # m3u8ファイルに記述されている音声ファイルを取得する
            for s in m3u8_obj.segments:
                if s.program_date_time in recorded:
                    continue
                recorded.add(s.program_date_time)
                try:
                    ffmpeg\
                    .input(filename=s.uri, f='aac', headers=headers)\
                    .output(filename=f'./tmp/{s.program_date_time}.aac')\
                    .run(capture_stdout=True)
                    # .get_args('-loglevel', 'error')\
                except Exception as e:
                    logging.warning('failed in run ffmpeg')
                    logging.warning(e)
            time.sleep(5.0)
        logging.debug('record end')
        return recorded

class RadikoAuth(object):
    """Radiko APIの認証クラス"""
    _AUTH1_URL = 'https://radiko.jp/v2/api/auth1'
    _AUTH2_URL = 'https://radiko.jp/v2/api/auth2'

    _RADIKO_AUTH_KEY = b'bcd151073c03b352e1ef2fd66c32209da9ca0afa'    # radiko apiの仕様で決まっている値 ref http://radiko.jp/apps/js/playerCommon.js

    def __init__(self):
        # RadikoAPIの仕様でheaderのX-Radiko-***の項目は必須
        self._headers = {
            'User-Agent': 'python3.7',
            'Accept': '*/*',
            'X-Radiko-App': 'pc_html5',
            'X-Radiko-App-Version': '0.0.1',
            'X-Radiko-User': 'dummy_user',
            'X-Radiko-Device': 'pc',
            'X-Radiko-AuthToken': '',
            'X-Radiko-Partialkey': '',
            'X-Radiko-AreaId': os.getenv('RADIKO_AREA_ID')
        }
        self._auth()

    def get_auththenticated_headers(self):
        """認証済みのhttp headerを返す"""
        return self._headers

    def _auth(self):
        """RadikoAPIで認証する"""
        # 認証トークンとauth2で必要なpartialkey生成に必要な値を取得する
        res = self._call_auth_api(RadikoAuth._AUTH1_URL)
        self._headers['X-Radiko-AuthToken'] = self._get_auth_token(res)
        self._headers['X-Radiko-Partialkey'] = self._get_partial_key(res)
        res = self._call_auth_api(RadikoAuth._AUTH2_URL)
        logging.debug(f'authenticated headers:{self._headers}')

    def _call_auth_api(self, api_url):
        """Radikoの認証APIを呼ぶ"""
        try:
            res = requests.get(url=api_url, headers=self._headers, timeout=5.0)
        except Timeout as e:
            logging.warning(f'failed in {api_url}.')
            logging.warning('API Timeout')
            logging.warning(e)
            raise Exception(f'failed in {api_url}.')
        if res.status_code != 200:
            logging.warning(f'failed in {api_url}.')
            logging.warning(f'status_code:{res.status_code}')
            logging.warning(f'content:{res.content}')
            raise Exception(f'failed in {api_url}.')
        logging.debug(f'auth in {api_url} is success.')
        return res

    def _get_auth_token(self, response):
        """HTTPレスポンスから認証トークンを取得する"""
        return response.headers['X-Radiko-AUTHTOKEN']

    def _get_partial_key(self, response):
        """HTTPレスポンスから認証用partial keyを取得する

        アルゴリズムはhttp://radiko.jp/apps/js/radikoJSPlayer.js createPartialkey関数を参照している。
        """
        length = int(response.headers['X-Radiko-KeyLength'])
        offset = int(response.headers['X-Radiko-KeyOffset'])
        partial_key = base64.b64encode(RadikoAuth._RADIKO_AUTH_KEY[offset: offset + length])
        return partial_key

def _get_args():
    parser = argparse.ArgumentParser(description='record radiko')
    parser.add_argument('station',
     type=str,
     help='radiko station')
    parser.add_argument('program',
     type=str,
     help='radiko program name')
    parser.add_argument('recordtime',
     type=int,
     help='recording time.(unit:miniutes)')
    args = parser.parse_args()
    return args.station, args.program, args.recordtime

if __name__ == "__main__":
    # ログ設定をする
    logging.basicConfig(filename=f'/var/log/record_radiko.log', level=logging.DEBUG)
    # 実行時パラメータを取得する
    station, program, rtime = _get_args()
    JST = timezone(timedelta(hours=+9), 'JST')
    current_time = datetime.now(tz=JST).strftime("%Y%m%d_%H%M")
    logging.debug(f'current time: {current_time}, \
        station: {station}, \
        program name: {program}, \
        recording time: {rtime}')
    # 録音保存先を用意する
    outfilename = f'./{current_time}_{station}_{program}.mp4'
    # 録音を実施する
    logging.debug(f'outfilename:{outfilename}')
    recorder = RadikoRecorder(station, rtime, outfilename)
    recorded = recorder.record()
    # mp3ファイルを一つに
    try:
        # recorded={'2019-11-20 10:31:25.010000+09:00', '2019-11-20 10:31:30.010000+09:00', '2019-11-20 10:31:35.005000+09:00'}
        l = list(recorded)
        l.sort()
        print(l)
        streams = [ffmpeg.input(filename=f'./tmp/{r}.aac') for r in l]
        ffmpeg\
            .concat(*streams,a=1,v=0)\
            .output(filename=f'./joined.aac' ,absf='aac_adtstoasc')\
            .run(capture_stdout=True)
        #  .get_args('-loglevel', 'error')\
    except Exception as e:
        logging.warning('failed in run ffmpeg concat')
        logging.warning(e)

