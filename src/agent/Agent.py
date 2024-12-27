import copy
import logging

from src.utils.utils import read_args, parse_args, log_config
from src.agent.memory.ShortTermMemory import ShortTermMemory
from src.agent.Brain import Brain
from src.agent.Body import Body
from src.agent.tools.ToolManager import ToolManager
from src.agent.Planner import Planner
from src.agent.Worker import Worker
from src.agent.Executor import Executor

logger = logging.getLogger('Agent')

class Agent:
    def __init__(self, pre_args):
        self.pre_args = pre_args
        self.args = read_args(pre_args)
        self.args = parse_args(self.args)

        log_config(self.args, self.args.task)

        self.tool = ToolManager(self.args)
        if self.args.tools:
            self.tool.update()

        self.short_memory = ShortTermMemory(self.args)

        self.brain = Brain(self.args, self.short_memory, self.tool)
        self.body = Body(self.args, self.tool)

        self.planner = Planner(self.args, self.brain)
        self.executor = Executor(self.args, self.brain, self.body)

    def set_tool(self, tools):
        self.args.tools = tools
        self.tool.update()

    def get_tool(self):
        return self.args.tools

    def faq(self, query):
        out = self.tool.knowledge_retrieval.qq_retrieve(query)
        outs = out['outs']
        if outs:
            answer = outs[0]['faq_answer']
        else:
            answer = ''
        return answer

    def interact(self, query, previous_turns, system_prompt, know_ids):
        previous_turns = copy.deepcopy(previous_turns)

        self.args.know_ids = know_ids
        self.args.profile = system_prompt

        worker = Worker(self.args, self.planner, self.executor)
        rsp = worker.run(query, previous_turns)
        worker.show()
        out = {
            'rsp': rsp,
            'note': worker.work_note,
            'sub_tasks': worker.sub_task_log
        }
        return out

    def show_states(self):
        self.short_memory.show()
        self.brain.show()

    def get_brain_log(self):
        brain_log = self.brain.get_log()
        return brain_log

    def reset(self):
        self.tool.reset()
        self.short_memory.reset()

        self.brain.reset()
        self.body.reset()

        self.executor.reset()
