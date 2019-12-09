import argparse
from datetime import datetime, timedelta, timezone
import logging

from gcloud.storage import upload_blob
from radiko.recorder import record

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
    parser.add_argument('-u', '--uploadgcloud',
     type=bool,
     help='upload recorded file to gcloud storage')
    args = parser.parse_args()
    return args.station, args.program, args.recordtime, args.uploadgcloud

if __name__ == "__main__":
    # ログ設定をする
    logging.basicConfig(filename=f'/var/log/record_radiko.log', level=logging.DEBUG)
    # 実行時パラメータを取得する
    station, program, rtime, uploads = _get_args()

    JST = timezone(timedelta(hours=+9), 'JST')
    current_time = datetime.now(tz=JST).strftime("%Y%m%d_%H%M")
    logging.debug(f'current time: {current_time}, \
        station: {station}, \
        program name: {program}, \
        recording time: {rtime}, \
        uploads: {uploads}')
    # 録音保存先を用意する
    outfilename = f'./tmp/{current_time}_{station}_{program}.aac'
    logging.debug(f'outfilename:{outfilename}')
    # 録音してアップロード
    record(station, program, rtime, outfilename)
    if uploads:
        upload_blob('radiko-recorder', outfilename, f'{current_time}_{station}_{program}.aac')
