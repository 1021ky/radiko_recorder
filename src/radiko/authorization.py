import base64
import logging
import os
import requests
from requests.exceptions import Timeout

class Authorization(object):
    """Radiko APIの認可クラス"""
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
        """認可済みのhttp headerを返す"""
        return self._headers

    def _auth(self):
        """RadikoAPIで認可する"""
        # 認可トークンとauth2で必要なpartialkey生成に必要な値を取得する
        res = self._call_auth_api(Authorization._AUTH1_URL)
        self._headers['X-Radiko-AuthToken'] = self._get_auth_token(res)
        self._headers['X-Radiko-Partialkey'] = self._get_partial_key(res)
        res = self._call_auth_api(Authorization._AUTH2_URL)
        logging.debug(f'authenticated headers:{self._headers}')
        logging.debug(f'res.headers:{res.headers}')
        for c in res.cookies:
            logging.debug(f'res.cookie:{c}')
        logging.debug(f'res.content:{res.content}')

    def _call_auth_api(self, api_url):
        """Radikoの認可APIを呼ぶ"""
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
        """HTTPレスポンスから認可トークンを取得する"""
        return response.headers['X-Radiko-AUTHTOKEN']

    def _get_partial_key(self, response):
        """HTTPレスポンスから認可用partial keyを取得する

        アルゴリズムはhttp://radiko.jp/apps/js/radikoJSPlayer.js createPartialkey関数を参照している。
        """
        length = int(response.headers['X-Radiko-KeyLength'])
        offset = int(response.headers['X-Radiko-KeyOffset'])
        partial_key = base64.b64encode(Authorization._RADIKO_AUTH_KEY[offset: offset + length])
        return partial_key
