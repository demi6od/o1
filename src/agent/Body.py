import logging
import json

logger = logging.getLogger('Body')

class Body:
    def __init__(self, args, tool):
        self.args = args

        self.tool = tool
        self.n_act = 0

    def act(self, tool_input, tool_name, history_messages):
        self.n_act += 1

        tool_output = self.tool.use(tool_input, tool_name, history_messages)

        obs = {
            'memory_type': 'observation',
            'tool_name': tool_name,
            'tool_input': tool_input,
            'tool_output': tool_output,
        }
        obs_str = json.dumps(obs, indent=4, ensure_ascii=False)
        logger.info(
            f'[+] act_{self.n_act}:\n'
            f'{obs_str}\n'
        )
        return obs

    def reset(self):
        self.n_act = 0
