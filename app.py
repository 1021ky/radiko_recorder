import os
import logging
import responder
from record_radiko import record as record_radiko

logging.basicConfig(filename=f'/var/log/record_radiko.log', level=logging.DEBUG)

api = responder.API()

@api.route("/record")
async def record(req, resp):

    @api.background.task
    def process_param(params):
        station = params.get('station', '')
        program = params.get('program', '')
        rtime = int(params.get('rtime', 0))

        record_radiko(station, program, rtime)

    process_param(req.params)
    resp.media = {'success': True}

if __name__ == '__main__':
    api.run()
