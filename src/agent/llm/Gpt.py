import traceback
import urllib.parse
import json
import logging
import time
import requests
import os
import openai
import openai_proxy
from openai import AzureOpenAI

logger = logging.getLogger('Gpt')

from src.agent.llm.base_LLM import LLM

class Gpt(LLM):
    def __init__(self, args):
        super().__init__(args)

        self.name = 'gpt'
        self.gpt4 = True

    def generate_ms(self, input_turns):
        tools = None
        fc_api = False
        if isinstance(input_turns, dict):
            fc_api = True
            tools = input_turns['tools']
            input_turns = input_turns['messages']

        if len(str(input_turns)) > self.args.max_llm_input_tokens:
            return None

        # model = 'gpt-4o-2024-08-06'
        model = 'gpt-4o-mini-2024-07-18'

        succ = False
        n_fail = 0
        while not succ:
            try:
                r = None
                resp = None
                client = openai_proxy.GptProxy(api_key=my_key)
                if tools:
                    r = client.generate(
                        messages=input_turns,
                        tools=tools,
                        model=model,
                        transaction_id="o1_fc",  # 同样transaction_id将被归类到同一个任务，一起统计
                        timeout=400,
                    )
                else:
                    r = client.generate(
                        messages=input_turns,
                        model=model,
                        transaction_id="o1_fc",  # 同样transaction_id将被归类到同一个任务，一起统计
                        timeout=400,
                    )
                if r.status_code != 200:
                    err_msg = f'[*] ms gpt service not 200: {r}'
                    raise Exception(err_msg)

                resp = r.json()
                resp = resp['data']['response_content']
                # resp = json.loads(str(resp))
                rsp_message = resp['choices'][0]['message']
                if 'content' not in rsp_message:
                    rsp_message['content'] = None
                # self.url_decode(rsp_message)
                if not fc_api:
                    rsp_message = rsp_message['content']
                else:
                    rsp_message['llm_input'] = {
                        'messages': input_turns,
                        'tools': tools,
                    }
                succ = True
            except Exception as e:
                n_fail += 1
                err_msg = f'[-] gpt_api exception:{str(e)}, r:{r}, resp:{resp}, traceback:{traceback.format_exc()}'
                rsp_message = None
                # if 'Please reduce the length of the messages' in err_msg or n_fail > 50:
                if 'Please reduce the length of the messages' in err_msg or 'InvalidRequestError' in err_msg:
                    break
                if self.args.skip_fail and ('Invalid' in err_msg or 'invalid' in err_msg):
                    break

                print(err_msg)
                time.sleep(self.args.wait_seconds)
        return rsp_message

    def generate(self, inp):
        rsp_message = self.generate_ms(inp)
        return rsp_message

    def url_decode(self, message):
        tool_calls = message.get('tool_calls', None)
        if tool_calls:
            for tool_call in tool_calls:
                args_str = tool_call['function']['arguments']
                args = json.loads(args_str)
                for key, val in args.items():
                    args[key] = urllib.parse.unquote(val)
                args_str = json.dumps(args, ensure_ascii=False)
                tool_call['function']['arguments'] = args_str
