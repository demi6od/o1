import traceback
import copy
import logging
import json
from src.agent.llm.Gpt import Gpt
from src.agent.llm.InternLM import InternLM
from src.agent.prompt.Prompt import Prompt
from src.agent.prompt.OutputParser import OutputParser
from src.utils.utils import get_time

logger = logging.getLogger('Brain')

class Brain:
    def __init__(self, args, memory, tool):
        self.args = args

        self.memory = memory
        self.tool = tool

        if self.args.llm == 'gpt':
            self.llm = Gpt(args)
        elif self.args.llm == 'intern':
            self.llm = InternLM(args)

        self.prompt = Prompt(args)
        self.output_parser = OutputParser(args)

        self.tool_tasks = ['execute_next']
        self.tool_rel_tasks = ['plan_next']
        self.memory_tasks = ['execute_next', 'execute_finish']
        self.work_note_tasks = ['plan_next', 'plan_update_result']

        self.log = []
        self.n_think = 0

    def construct_message(self, system_message, previous_turns, user_message):
        user_prompt_len = len(str(user_message))
        system_prompt_len = len(str(system_message))
        message_len = len(str(previous_turns)) + user_prompt_len + system_prompt_len
        if message_len > self.args.max_llm_input_tokens:
            if self.args.debug:
                err_msg = f'[-] llm input length({message_len}) > max({self.args.max_llm_input_tokens})'
                logger.error(err_msg)
                raise Exception(err_msg)
            else:
                max_dialog_his_len = self.args.max_llm_input_tokens - user_prompt_len - system_prompt_len
                while len(str(previous_turns)) > max_dialog_his_len:
                    previous_turns = previous_turns[1:]

        messages = [system_message] + previous_turns
        if user_message:
            messages.append(user_message)

        return messages

    def construct_llm_input(self, think_input, think_type, previous_turns, note, no_user):
        # Construct prompt
        prompt = self.prompt.construct(think_input, think_type, note)
        if think_type in self.work_note_tasks and self.args.working_mode == 'plan':
            work_note_desc = f'<|Work Note Description|>: {self.prompt.get_work_note_desc()}'
        else:
            work_note_desc = ''
        system_prompt = (
            f'<|timer|>: Current date and time: {get_time()}\n'
            f'<|profile|>: {self.prompt.get_profile(self.args.role)}'
            f'{work_note_desc}'
        )
        # user_prompt = (
        #     f'<|instruction|>: {prompt}\n'
        # )
        user_prompt = prompt

        # Construct llm_input
        system_message = {
            "role": "system",
            "content": system_prompt
        }
        messages = [system_message] + previous_turns
        if not no_user:
            user_message = {
                "role": "user",
                "content": user_prompt
            }
            messages.append(user_message)

        if think_type in self.tool_tasks:
            tools = self.tool.schema()
        else:
            tools = []

        llm_input = {
            'messages': messages,
            'tools': tools,
        }
        return llm_input

    def think(self, think_input, think_type, previous_turns=None, note='', no_user=False):
        self.n_think += 1

        if previous_turns is None:
            previous_turns = []

        logger.info(f'[+] think_{self.n_think} start: {think_type}')

        llm_input = self.construct_llm_input(think_input, think_type, previous_turns, note, no_user)
        llm_output = None
        for i in range(self.args.n_llm_try):
            try:
                llm_output = self.llm.generate(llm_input)
                thought = self.output_parser.parse(llm_output, think_type)
                break
            except Exception as e:
                logger.warning(f'[*] llm run exception: {e}\nllm_output: {llm_output}\ntraceback={traceback.format_exc()}')
        else:
            err_str = f'[-] llm run failed {self.args.n_llm_try} times'
            logger.error(err_str)
            raise Exception(err_str)

        mem_unit = {
            'memory_type': 'think',
            'think_type': think_type,
            # 'think_input': think_input,
            'llm_input': llm_input,
            'think_output': llm_output,
        }
        if think_type in self.memory_tasks:
            self.memory.store(mem_unit)

        mem_str = json.dumps(mem_unit, indent=4, ensure_ascii=False)
        logger.info(
            f'[+] think_{self.n_think} end:\n'
            f'{mem_str}\n'
        )

        log_unit = {
            'think_type': think_type,
            'think_input': think_input,
            'llm_input': llm_input,
            'llm_output': llm_output,
        }
        self.log.append(copy.deepcopy(log_unit))

        if thought['action'] == 'act':
            if not no_user:
                previous_turns.append(llm_input['messages'][-1])
            previous_turns.append(thought['message'])
        return thought

    def observe(self, obs):
        self.memory.store(obs)

    def forget(self):
        self.memory.clear()

    def show(self):
        log_str = json.dumps(self.log, indent=4, ensure_ascii=False)
        logger.info(
            f'[+] <brain_log>\n'
            f'{log_str}\n'
            f'</brain_log>\n'
        )

    def get_log(self):
        return self.log

    def reset(self):
        self.log = []
        self.n_think = 0
