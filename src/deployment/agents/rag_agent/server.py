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

logger = logging.getLogger('rag_agent_server')

PORT = 12029
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app)

@app.route('/rag_agent', methods=['POST'])
def get():
    rsp = server_pack('rag_agent', rag_agent_api, request.json)
    return rsp

def rag_agent_api(sample):
    url = 'https://api.stage.sensenova.cn/v1/llm/chat-completions'
    # key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIyZTJYTnBtY0RQNzNZMHpQSlNmTEJLS1pNMGgiLCJleHAiOjE3NDI2Mzk3MDksIm5iZiI6MTcxMTEwMzcwNH0.TgkhkcN7jhMw8d1LWV4BMXQ9IwnJqLeQFlj2KSlHVRI'
    # key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIyWTh6aW1Gb2xmaXJscHNuYXhtZ1NwZGNpY3giLCJleHAiOjIwMTUyODIyNDgsIm5iZiI6MTY5OTkyMjI0M30._nj8tS77UIACT6dloUc2C7BzZ8dQ8zIQgO80w7pQUEI'
    key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIyWlFhZFVRQ1J2SGJQN3hLTHJRNVBTQmJWangiLCJleHAiOjE3MzE3NjYzNzUsIm5iZiI6MTcxMzc2NjM3MH0.cP--Did3Nr1QpwUFdQg0rOOWTkUtzMwkx6Yr2nksroE'
    headers = {
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json'
    }

    messages = format_msg(sample['messages'])
    sys_prompt = ''
    if sys_prompt:
        sys_msg = {
            'role': 'system',
            'content': sys_prompt
        }
        messages = [sys_msg] + messages

    know_ids = sample.get('know_ids', [])
    payload = {
        "messages": messages,
        "model": 'SenseChat-32K-stage',
        "temperature": 0.8,
        "do_sample": True,
        "ignore_eos": False,
        "stop_sequences": '<|im_end|>',
        "top_p": 0.8,
        "top_k": 40,
        "max_new_tokens": 1024,
        "repetition_penalty": 1.0,
        "know_ids": know_ids,
        "stream": False,
        "plugins": {
            "web_search": {
                "search_enable": True,
                "result_enable": True
            }
        },
    }

    r = None
    try:
        logger.info(f'[+] rag input={payload}')
        r = requests.post(url, json=payload, headers=headers, timeout=300)
        rsp = r.json()
        if 'data' in rsp:
            content = rsp['data']['choices'][0]['message']
        else:
            content = str(rsp)

        message = {
            'role': 'assistant',
            'content': content,
        }
        new_messages = [message]
    except Exception as e:
        new_messages = '[-] rag_agent service exception'
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
log_config(args, 'rag_agent_server')


if __name__ == '__main__':
    main()
