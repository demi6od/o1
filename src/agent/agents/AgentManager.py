import logging
import time

from src.agent.agents.GeneralAgent import GeneralAgent

logger = logging.getLogger('AgentManager')

class AgentManager:
    def __init__(self, args):
        self.args = args
        self.general_agent = GeneralAgent(args)

    def run(self, agent_name, history_messages):
        agent_input = {
            'agent_name': agent_name,
            'history_messages': history_messages,
        }

        out = None
        time.sleep(1)
        for i in range(5):
            try:
                out = self.general_agent.run(**agent_input)
                break
            except Exception as e:
                err_msg = f'[*] agent exception agent_name={agent_name}, agent_input={agent_input}, error={e}'
                logger.warning(err_msg)
                time.sleep(5)
        else:
            logger.error(err_msg)
        return out
