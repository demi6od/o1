import logging
import json
import os.path

import requests

from src.agent.tools.base_Tool import Tool
from src.agent.llm.Gpt import Gpt
from src.utils.utils import read_file

logger = logging.getLogger('GeneralTool')

class GeneralTool(Tool):
    def __init__(self, args, server):
        super().__init__(args, server)

        self.args = args
        in_file = os.path.join(args.tool_dir, 'tool_dict.json')

        tool_dict = read_file(in_file)
        self.schema_dict = tool_dict['schema']
        self.server_dict = tool_dict['server']

        self.gpt = Gpt(args)

    def get_schema(self, tool_name=''):
        return self.schema_dict[tool_name]

    def run(self, tool_name, tool_input, history_messages=None):
        if self.args.virtual_tool:
            return self.simulate(tool_name, tool_input, history_messages)
        else:
            try:
                if 'agent' in tool_name:
                    if not isinstance(tool_input, dict):
                        tool_input = {}
                    tool_input['messages'] = history_messages
                r = requests.post(self.server_dict[tool_name], json=tool_input, timeout=30)
                response = r.json()
            except Exception as e:
                err_msg = f'[-] {tool_name} Server error: {str(e)}'
                logger.error(err_msg)
                raise Exception(err_msg)

            if response['status'] != 'OK' or 'response' not in response:
                err_msg = f'[-] {tool_name} Server error: {response["status"]}'
                logger.error(err_msg)
                raise Exception(err_msg)

            resp = response['response']
            return resp

    def simulate(self, tool_name, tool_input, history_messages):
        schema = self.schema_dict[tool_name]
        prompt = (
            f'请根据提供的对话历史（dialog history）、工具描述（tool schema）和输入（tool input），虚构一个工具的中文输出结果（tool output），尽可能严谨合理保证准确。\n'
            f'dialog history:\n'
            f'{history_messages}\n'
            f'\n'
            f'tool schema:\n'
            f'{schema}\n'
            f'\n'
            f'tool input:\n'
            f'{tool_input}\n'
            f'\n'
            f'tool output:\n'
        )
        message = {
            'role': 'user',
            'content': prompt,
        }
        llm_input = {
            'messages': [message]
        }
        llm_output = self.gpt.generate(llm_input)
        return llm_output
