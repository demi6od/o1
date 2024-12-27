import traceback
import logging
import time
import requests

logger = logging.getLogger('InternLM')

from src.agent.llm.base_LLM import LLM

class InternLM(LLM):
    def __init__(self, args):
        super().__init__(args)

        self.name = 'intern'
        self.url = f'http://{self.args.llm_server_ip}:12004/fc'

    def generate(self, inp):
        sample = {
            'input': inp
        }
        succ = False
        while not succ:
            try:
                rsp = None
                time.sleep(1)

                r = requests.post(self.url, json=sample)
                rsp = r.json()

                out = rsp['response']['message']
                succ = True
            except Exception as e:
                err_msg = f'[*] {self.name}_api exception:{str(e)}, input={inp}, rsp={rsp}, traceback={traceback.format_exc()}'
                logger.warning(err_msg)
                out = None
                if 'Please reduce the length of the messages' in err_msg:
                    raise Exception(err_msg)
        return out
