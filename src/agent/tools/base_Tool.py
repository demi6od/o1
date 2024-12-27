from abc import abstractmethod
import logging

logger = logging.getLogger('Tool')

class Tool:
    def __init__(self, args, server):
        self.args = args

        self.schema = None
        self.server = server

    @abstractmethod
    def run(self, *args, **kwargs):
        raise NotImplementedError

    def get_schema(self, tool_name=''):
        return self.schema
