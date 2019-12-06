import argparse
import logging

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
    args = parser.parse_args()
    return args.station, args.program, args.recordtime

if __name__ == "__main__":
    # ログ設定をする
    logging.basicConfig(filename=f'/var/log/record_radiko.log', level=logging.DEBUG)
    # 実行時パラメータを取得する
    station, program, rtime = _get_args()
    record(station, program, rtime)
