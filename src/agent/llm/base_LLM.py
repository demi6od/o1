from abc import abstractmethod
import logging
import json

logger = logging.getLogger('LLM')

class LLM:
    def __init__(self, args):
        self.args = args

    @abstractmethod
    def generate(self, inp):
        raise NotImplementedError
