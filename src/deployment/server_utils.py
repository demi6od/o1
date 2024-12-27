import traceback
from datetime import datetime
import json
import logging
import time
import os
import sys

logger = logging.getLogger('server_api')

PROJECT_DIR = os.path.join(os.path.dirname(__file__), '../..')
sys.path.append(PROJECT_DIR)

def tool_virtual_run(inp):
    tool = inp['tool']
    req = inp['req']
    out = tool.simatulate(req)
    return out

def virtual_tool_api(tool, req):
    inp = {
        'tool': tool,
        'req': req,
    }
    rsp = server_pack('virtual_tool', tool_virtual_run, inp)
    return rsp

def tool_run(inp):
    tool = inp['tool']
    req = inp['req']
    out = tool.run(**req)
    return out

def tool_api(tool, req):
    inp = {
        'tool': tool,
        'req': req,
    }
    rsp = server_pack('tool', tool_run, inp)
    return rsp

def server_pack(name, api, req, raw=False):
    try:
        req_str = json.dumps(req, indent=4, ensure_ascii=False)
    except:
        req_str = str(req)
    logger.info(f'[+] {name} received -> {req_str}')

    try:
        start_time = time.time()
        tot_time = time.time() - start_time

        try:
            response = api(req)
        except Exception as e:
            err_msg = f'[-] {name} server error: {str(e)}'
            print(err_msg)
            raise Exception(err_msg)

        if raw:
            rsp = response
        else:
            rsp = {
                'response': response,
                'status': 'OK',
                'cost': tot_time,
            }

        # rsp_str = json.dumps(response, indent=4, ensure_ascii=False)
        # logger.info(f'[+] {name} response -> {rsp_str}')

        current_time = datetime.now()
        current_time_str = current_time.strftime("%Y.%m.%d %H:%M:%S")
        log_data = {
            'req': req,
            'rsp': response,
            'time': current_time_str
        }
        try:
            log_str = json.dumps(log_data, indent=4, ensure_ascii=False)
        except:
            log_str = str(log_data)
        # logger.info(f'[+] {name} response -> {log_str}')
        logger.info(f'[+] {name} <log_start>{log_str}<log_end>')
        return rsp
    except Exception as e:
        message = str(traceback.format_exc())
        logger.error(f'{message}')
        raise Exception(message)

def format_msg(messages, agent=''):
    format_messages = []
    for msg in messages:
        if msg['role'] == 'user':
            format_messages.append(msg)
        elif msg['role'] == 'assistant':
            if agent == 'fc' or 'tool_calls' not in msg:
                format_messages.append(msg)
        elif msg['role'] == 'file' and agent == 'data':
            format_messages.append(msg)

    return format_messages
