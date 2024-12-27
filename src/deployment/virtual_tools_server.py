import sys
import os
import logging

from flask import request
from flask import Flask
from flask_cors import CORS

PROJECT_DIR = os.path.join(os.path.dirname(__file__), '../..')
sys.path.append(PROJECT_DIR)

from src.agent.tools.GeneralTool import GeneralTool
from src.agent.tools.ToolServer import ToolServer
from src.deployment.server_utils import virtual_tool_api
from src.utils.utils import read_args, parse_args, log_config

logger = logging.getLogger('virtual_tool_server')

PORT = 12025
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app)

@app.route('/virtual_tools', methods=['POST'])
def tool_server_api():
    rsp = virtual_tool_api(general_tool, request.json)
    return rsp

def main():
    app.run(host='0.0.0.0', port=PORT)


sys.argv = ['', '../params/tool_server.json']
args = {
    'project_dir': PROJECT_DIR,
}
args = read_args(args)
args = parse_args(args)
log_config(args, 'virtual_tools_server')

tool_server = ToolServer(args)
general_tool = GeneralTool(args, tool_server)
logger.info(general_tool.args)

if __name__ == '__main__':
    main()
