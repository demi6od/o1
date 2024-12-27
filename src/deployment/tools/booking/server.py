import sys
import os
import logging
import time
import traceback

from flask import request
from flask import Flask
from flask_cors import CORS

PROJECT_DIR = os.path.join(os.path.dirname(__file__), '../../../..')
sys.path.append(PROJECT_DIR)

from src.deployment.tools.booking.booking import GetBookings, DeleteBookings, UpdateBooking, CreateBooking, ResetCalendar
from src.utils.utils import read_args, parse_args, log_config

logger = logging.getLogger('booking_server')

PORT = 12025
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app)

@app.route('/get', methods=['POST'])
def get():
    rsp = booking_api('get', request.json)
    return rsp

@app.route('/create', methods=['POST'])
def create():
    rsp = booking_api('create', request.json)
    return rsp

@app.route('/delete', methods=['POST'])
def delete():
    rsp = booking_api('delete', request.json)
    return rsp

@app.route('/update', methods=['POST'])
def update():
    rsp = booking_api('update', request.json)
    return rsp

@app.route('/reset', methods=['POST'])
def reset():
    rsp = booking_api('reset', request.json)
    return rsp

def booking_api(method, args):
    logger.info(f'[+] START, input: {method}, {args}')

    try:
        start_time = time.time()
        out = booking_func_dict[method]._run(**args)
        tot_time = time.time() - start_time

        rsp = {
            'response': str(out),
            'status': 'OK',
            'cost': tot_time,
        }
        return rsp
    except Exception as e:
        message = str(traceback.format_exc())
        logger.error(f'{message}')
        raise Exception(message)

def main():
    app.run(host='0.0.0.0', port=PORT)


booking_func_dict = {
    'get': GetBookings(),
    'create': CreateBooking(),
    'delete': DeleteBookings(),
    'update': UpdateBooking(),
    'reset': ResetCalendar(),
}

sys.argv = ['', '../../../params/tool_server.json']
args = {
    'project_dir': PROJECT_DIR,
}
args = read_args(args)
args = parse_args(args)
log_config(args, 'booking_server')


if __name__ == '__main__':
    main()
