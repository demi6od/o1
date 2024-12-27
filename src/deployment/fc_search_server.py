import sys
import os
import logging

from flask import request
from flask import Flask
from flask_cors import CORS

PROJECT_DIR = os.path.join(os.path.dirname(__file__), '../..')
sys.path.append(PROJECT_DIR)

from src.agent.Agent import Agent
from src.deployment.server_utils import server_pack, format_msg
from src.agent_api.assistants_api import assistants_run

logger = logging.getLogger('fc_search_server')

PORT = 12036
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app)

@app.route('/fc_search', methods=['POST'])
def assistant_server():
    req = request.json
    rsp = server_pack('main_agent', assistants_api, req)
    return rsp

def assistants_api(req):
    messages = req['messages']
    messages = format_msg(messages, agent='fc')

    tools = ['web_search']

    sys_prompt = '你是SenseChat，一个由商汤科技开发的人工智能助手，可利用各种工具来辅助解答各种问题。你可以同时调用多个工具，也可以顺序调用工具，你的答复应尽量使用中文。请尽量优化你的回答，确保信息的准确性和有用性以及简洁性。不依赖工具的问题可以直接回答。你可以采用web_search工具来搜索相关时事新闻和百科知识等。'
    if sys_prompt:
        sys_msg = {
            'role': 'system',
            'content': sys_prompt
        }
        messages = [sys_msg] + messages

    out = assistants_run(agent, messages, tools)
    assistant_out = {
        'new_messages': out['new_messages']
    }
    return assistant_out

def main():
    app.run(host='0.0.0.0', port=PORT)


sys.argv = ['', '../params/fc_search.json']
args = {
    'project_dir': PROJECT_DIR,
    'role': 'open_domain_expert',
    # 'tools': ["web_search", "python_interpreter", "text2image"],
    # 'tools': ["web_search", "code_agent", "text2image"],
}
agent = Agent(args)
logger.info(agent.args)

if __name__ == '__main__':
    main()
