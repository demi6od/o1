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

logger = logging.getLogger('math_agent_server')

PORT = 12026
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app)

@app.route('/code_agent', methods=['POST'])
def get():
    rsp = server_pack('code_agent', code_agent_api, request.json)
    return rsp

def code_agent_api(sample):
    url = 'http://fc-api.mtc.sensetime.com/fc'

    messages = format_msg(sample['messages'])
    sys_prompt = '你是SenseChat，中文名字叫商量，一个有用无害的人工智能助手'
    if sys_prompt:
        sys_msg = {
            'role': 'system',
            'content': sys_prompt
        }
        messages = [sys_msg] + messages

    parameters = {
        "do_sample": True,
        "ignore_eos": False,
        "max_new_tokens": 1024,
        "stop_sequences": '<|im_end|>',
        "top_k": 40,
        "top_p": 0.8,
        "temperature": 0.0,
        "repetition_penalty": 1.0,
    }

    payload = {
        "model": 'b330k-e29k-sft-s-0413-rlhf',
        "messages": messages,
        "parameters": parameters,
    }

    r = None
    try:
        r = requests.post(url, json=payload, timeout=300)
        rsp = r.json()
        rsp_message = rsp['choices'][0]['message']
        new_messages = [rsp_message]
    except Exception as e:
        new_messages = '[-] code_agent service exception'
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
log_config(args, 'code_agent_server')


if __name__ == '__main__':
    main()
