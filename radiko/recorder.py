from datetime import datetime, timedelta, timezone
import requests
from requests.exceptions import Timeout
import sys
import time
import logging

import ffmpeg
import m3u8

from gcloud.storage import upload_blob
from radiko.authorization import Authorization

JST = timezone(timedelta(hours=+9), 'JST')

class RadikoRecorder(object):
    """Radikoの録音クラス"""

    _MASTER_PLAYLIST_BASE_URL = 'https://rpaa.smartstream.ne.jp/so/playlist.m3u8'
    _DUMMY_LSID = '11111111111111111111111111111111111111' # Radiko APIの仕様で38桁の文字列が必要。

    def __init__(self, station, record_time, outfile):
        self._headers = self._make_headers()
        self._station = station
        self._record_time = record_time
        self._file = outfile

    def _make_headers(self):
        """HTTPリクエストのヘッダーを作成する"""
        headers = Authorization().get_auththenticated_headers()
        headers['Connection']='keep-alive'
        logging.debug(f'headers: {headers}')
        return headers

    def _make_master_playlist_url(self):
        """master playlistのURLを作成する"""
        url = f'{RadikoRecorder._MASTER_PLAYLIST_BASE_URL}?station_id={self._station}&l=15&lsid={RadikoRecorder._DUMMY_LSID}&type=b'
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

    def _get_media_playlist_url(self):
        """media playlistのURLを取得する"""
        u = self._make_master_playlist_url()
        r = requests.get(url=u, headers=self._headers)
        if r.status_code != 200:
            logging.warning('failed to get media playlist url')
            logging.warning(f'status_code:{r.status_code}')
            logging.warning(f'content:{r.content}')
            raise Exception('failed in radiko get media playlist')
        m3u8_obj = m3u8.loads(r.content.decode('utf-8'))
        media_playlist_url = m3u8_obj.playlists[0].uri
        logging.debug(f'media_playlist_url: {media_playlist_url}')
        return media_playlist_url

    def _get_media_url(self, media_playlist_url):
        """音声ファイルのURLをmedia playlistから取得する"""
        query_time = int(datetime.now(tz=JST).timestamp() * 100)
        r = requests.get(url=f'{media_playlist_url}&_={query_time}',headers=self._headers)
        logging.debug(f'aac url:{media_playlist_url}&_={query_time}')
        if r.status_code != 200:
            return None
        m3u8_obj = m3u8.loads(str(r.content.decode('utf-8')))
        m3u8_obj.segments.reverse() # 時刻昇順にする
        return [(s.program_date_time, s.uri) for s in m3u8_obj.segments]

    def record(self):
        """録音する"""
        logging.debug('record start')
        media_playlist_url = self._get_media_playlist_url()
        end = datetime.now() + timedelta(minutes=self._record_time)
        recorded = set()
        while(datetime.now() <= end):
            url_list = self._get_media_url(media_playlist_url)
            if url_list == None:
                # 時間をおいてリトライすると取れるときがあるため待つ
                time.sleep(3.0)
                continue
            headers = self._make_audio_headers()
            # save audio m3u8ファイルに記述されている音声ファイルを取得する
            for dt, url in url_list:
                if dt in recorded:
                    continue
                recorded.add(dt)
                try:
                    ffmpeg\
                    .input(filename=url, f='aac', headers=headers)\
                    .output(filename=f'./tmp/{dt}.aac')\
                    .run(capture_stdout=True)
                except Exception as e:
                    logging.warning('failed in run ffmpeg')
                    logging.warning(e)
            time.sleep(5.0)
        logging.debug('record end')
        return recorded

def record(station, program, rtime):
    res = requests.get('http://ipinfo.io')
    logging.debug(f'ipinfo.io content:{res.content}')
    JST = timezone(timedelta(hours=+9), 'JST')
    current_time = datetime.now(tz=JST).strftime("%Y%m%d_%H%M")
    logging.debug(f'current time: {current_time}, \
        station: {station}, \
        program name: {program}, \
        recording time: {rtime}')
    # 録音保存先を用意する
    outfilename = f'./tmp/{current_time}_{station}_{program}.aac'
    # 録音を実施する
    logging.debug(f'outfilename:{outfilename}')
    recorder = RadikoRecorder(station, rtime, outfilename)
    recorded = recorder.record()
    # mp3ファイルを一つに
    try:
        l = list(recorded)
        l.sort()
        print(l)
        streams = [ffmpeg.input(filename=f'./tmp/{r}.aac') for r in l]
        ffmpeg\
            .concat(*streams,a=1,v=0)\
            .output(filename=outfilename, absf='aac_adtstoasc')\
            .run(capture_stdout=True)
    except Exception as e:
        logging.warning('failed in run ffmpeg concat')
        logging.warning(e)
    upload_blob('radiko-recorder', outfilename, f'{current_time}_{station}_{program}.aac')
