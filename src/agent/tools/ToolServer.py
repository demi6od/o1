import requests
import logging

logger = logging.getLogger('ToolServer')

class ToolServer:
    def __init__(self, args):
        self.args = args

        self.server_url = {
            'knowledge_retrieval': f'http://{self.args.knowledge_retrieval_server_ip}:12009/offline_retrieval',
            'text2image': f'http://{self.args.text2image_server_ip}:12021/text2image',
            'web_search': f'http://{self.args.web_search_server_ip}:12022/web_search',
            'python_interpreter': f'http://{self.args.python_interpreter_server_ip}:12023/python_interpreter',
            'code_agent': f'http://{self.args.code_agent_server_ip}:12024/code_agent',
        }

    def api(self, sample, task, timeout=30):
        try:
            r = requests.post(self.server_url[task], json=sample, timeout=timeout, headers=self.args.headers_info)
            response = r.json()
        except Exception as e:
            err_msg = f'[-] {task} Server error: {str(e)}'
            logger.error(err_msg)
            raise Exception(err_msg)

        if response['status'] != 'OK' or 'response' not in response:
            err_msg = f'[-] {task} Server error: {response["status"]}'
            logger.error(err_msg)
            raise Exception(err_msg)

        resp = response['response']
        return resp

    # def run(self, sample, task, timeout=30):
    #     self.api(sample, task, timeout)
