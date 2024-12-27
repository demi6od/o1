import sys
import os
import logging
import time
import traceback

from flask import request
from flask import Flask
from flask_cors import CORS
import requests

PROJECT_DIR = os.path.join(os.path.dirname(__file__), '../../../..')
sys.path.append(PROJECT_DIR)

from src.utils.utils import read_args, parse_args, log_config
from src.deployment.server_utils import server_pack, format_msg

logger = logging.getLogger('data_agent_server')

PORT = 12034
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app)

@app.route('/data_agent', methods=['POST'])
def get():
    rsp = server_pack('data_agent', data_agent_api, request.json)
    return rsp

def data_agent_api(sample):
    url = 'http://pumpcoder.mtc.sensetime.com/api/sensechat-code-interpreter-excel/'

    messages = format_msg(sample['messages'], agent='data')
    sys_prompt = ''
    if sys_prompt:
        sys_msg = {
            'role': 'system',
            'content': sys_prompt
        }
        messages = [sys_msg] + messages

    parameters = {
        "do_sample": True,
        "top_p": 0.5,
        "temperature": 0.2,
        "repetition_penalty": 1.02,
    }

    payload = {
        "messages": messages,
        "parameters": parameters,
    }

    r = None
    try:
        r = requests.post(url, json=payload, timeout=300)
        rsp = r.json()
        new_messages = rsp['new_messages']
        new_messages = [msg for msg in new_messages if msg['role'] != 'endofmessage']
    except Exception as e:
        new_messages = '[-] data_agent service exception'
        logger.error(f'[-] error = {e}, input = {payload}, output = {r}')

    assistant_out = {
        'new_messages': new_messages
    }
    return assistant_out

def main():
    app.run(host='0.0.0.0', port=PORT)


sys.argv = ['', '../../../params/tool_server.json']
args = {
    'project_dir': PROJECT_DIR,
}
args = read_args(args)
args = parse_args(args)
log_config(args, 'data_agent_server')


if __name__ == '__main__':
    main()
