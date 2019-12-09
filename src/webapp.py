from datetime import datetime, timedelta, timezone
import os
import logging
import responder

from gcloud import upload_blob
from radiko.recorder import record

logging.basicConfig(filename=f'/var/log/record_radiko.log', level=logging.DEBUG)

api = responder.API()

@api.route("/record")
async def record(req, resp):

    @api.background.task
    def process_param(params):
        station = params.get('station', '')
        program = params.get('program', '')
        rtime = int(params.get('rtime', 0))
        JST = timezone(timedelta(hours=+9), 'JST')
        current_time = datetime.now(tz=JST).strftime("%Y%m%d_%H%M")
        logging.debug(f'current time: {current_time}, \
            station: {station}, \
            program name: {program}, \
            recording time: {rtime}')
        # 録音保存先を用意する
        outfilename = f'./tmp/{current_time}_{station}_{program}.aac'
        logging.debug(f'outfilename:{outfilename}')
        # 録音してアップロード
        record(station, program, rtime, outfilename)
        upload_blob('radiko-recorder', outfilename, f'{current_time}_{station}_{program}.aac')


    process_param(req.params)
    resp.media = {'success': True}

if __name__ == '__main__':
    api.run()
