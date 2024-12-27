from abc import abstractmethod
import logging

logger = logging.getLogger('Agent')

class Agent:
    def __init__(self, args):
        self.args = args
        self.schema = None

    @abstractmethod
    def run(self, *args, **kwargs):
        raise NotImplementedError

    def get_schema(self, agent_name=''):
        return self.schema
