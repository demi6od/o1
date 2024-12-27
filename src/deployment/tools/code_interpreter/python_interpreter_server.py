import sys
import os
import logging

from flask import request
from flask import Flask
from flask_cors import CORS

PROJECT_DIR = os.path.join(os.path.dirname(__file__), '../../../..')
sys.path.append(PROJECT_DIR)

from src.agent.tools.PythonInterpreter import PythonInterpreter
from src.agent.tools.ToolServer import ToolServer
from src.deployment.server_utils import tool_api
from src.utils.utils import read_args, parse_args, log_config

logger = logging.getLogger('chat_know_server')

PORT = 12023
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app)

@app.route('/python_interpreter', methods=['POST'])
def tool_server_api():
    rsp = tool_api(python_interpreter, request.json)
    return rsp

def main():
    app.run(host='0.0.0.0', port=PORT)


sys.argv = ['', '../../../params/tool_server.json']
args = {
    'project_dir': PROJECT_DIR,
}
args = read_args(args)
args = parse_args(args)
log_config(args, 'python_interpreter_server')

python_interpreter = PythonInterpreter(args, None)
logger.info(python_interpreter.args)

if __name__ == '__main__':
    main()
