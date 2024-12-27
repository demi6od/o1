import sys
import os
import logging

from flask import request
from flask import Flask
from flask_cors import CORS

PROJECT_DIR = os.path.join(os.path.dirname(__file__), '../..')
sys.path.append(PROJECT_DIR)

from src.utils.utils import read_args, parse_args, log_config

logger = logging.getLogger('o1_server')

from src.deployment.server_utils import server_pack
from src.agent_api.o1_api import o1_run

PORT = 12031
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app)

@app.route('/o1', methods=['POST'])
def o1_server():
    rsp = server_pack('o1_api', o1_run, request.json)
    return rsp

def main():
    app.run(host='0.0.0.0', port=PORT)

sys.argv = ['', '../params/agent.json']
args = {
    'project_dir': PROJECT_DIR,
}
args = read_args(args)
args = parse_args(args)
log_config(args, 'o1_server')


if __name__ == '__main__':
    main()
