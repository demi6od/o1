import logging
import json
import os.path

import requests

from src.agent.agents.base_Agent import Agent
from src.agent.llm.Gpt import Gpt
from src.utils.utils import read_file

logger = logging.getLogger('GeneralAgent')

class GeneralAgent(Agent):
    def __init__(self, args):
        super().__init__(args)

        self.args = args
        in_file = os.path.join(args.agent_dir, 'agent_dict.json')

        agent_dict = read_file(in_file)
        self.schema_dict = agent_dict['schema']
        self.server_dict = agent_dict['server']

        self.gpt = Gpt(args)

    def get_schema(self, agent_name=''):
        return self.schema_dict[agent_name]

    def run(self, agent_name, history_messages=None):
        if self.args.virtual_agent:
            return self.simulate(agent_name, history_messages)
        else:
            try:
                agent_input = {
                    'messages': history_messages,
                }
                r = requests.post(self.server_dict[agent_name], json=agent_input, timeout=30)
                response = r.json()
            except Exception as e:
                err_msg = f'[-] {agent_name} Server error: {str(e)}'
                logger.error(err_msg)
                raise Exception(err_msg)

            if response['status'] != 'OK' or 'response' not in response:
                err_msg = f'[-] {agent_name} Server error: {response["status"]}'
                logger.error(err_msg)
                raise Exception(err_msg)

            resp = response['response']
            return resp

    def simulate(self, agent_name, history_messages):
        schema = self.schema_dict[agent_name]
        prompt = (
            f'请根据提供的对话历史（dialog history）、agent描述（agent schema），虚构一个agent的中文输出结果（agent output），尽可能严谨合理保证准确。\n'
            f'dialog history:\n'
            f'{history_messages}\n'
            f'\n'
            f'agent schema:\n'
            f'{schema}\n'
            f'\n'
            f'agent output:\n'
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
