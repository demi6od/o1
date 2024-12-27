import logging
import copy
import json
from collections import deque

logger = logging.getLogger('ShortTermMemory')

class ShortTermMemory:
    def __init__(self, args):
        self.args = args

        self.short_memorys = deque(maxlen=self.args.short_mem_capacity)
        self.memory_history = deque(maxlen=1000)

    def store(self, mem_unit):
        self.short_memorys.append(copy.deepcopy(mem_unit))
        self.memory_history.append(copy.deepcopy(mem_unit))

    def retrieve(self):
        return list(self.short_memorys)

    def show(self):
        mem = list(self.memory_history)
        mem_str = json.dumps(mem, indent=4, ensure_ascii=False)
        logger.info(
            f'[+] memory_history:\n'
            f'{mem_str}\n'
        )

    def clear(self):
        self.short_memorys.clear()

    def reset(self):
        self.short_memorys.clear()
        self.memory_history.clear()

