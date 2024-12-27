import logging
from src.utils.utils import reindex_search_results

logger = logging.getLogger('Executor')

class Executor:
    def __init__(self, args, brain, body):
        self.args = args

        self.brain = brain
        self.body = body

        self.n_execute = 0

    def execute(self, task, previous_turns, note):
        self.n_execute += 1

        act_logs = []
        execute_step = 0
        while True:
            execute_step += 1
            logger.info(f'[+] execute_step_{execute_step}, n_execute_{self.n_execute}, task: {task}\n')

            previous_turns = reindex_search_results(previous_turns)

            # Reach max step
            if execute_step > self.args.max_execute_step:
                thought = self.brain.think(task, 'execute_finish', previous_turns, note, no_user=(execute_step > 1))
                response = thought['content']
                print(response)
                out = {
                    'response': response,
                    'act_logs': act_logs
                }
                return out

            thought = self.brain.think(task, 'execute_next', previous_turns, note, no_user=(execute_step > 1))

            # Reach task finish
            if thought['action'] == 'response':
                response = thought['content']
                print(response)
                out = {
                    'response': response,
                    'act_logs': act_logs
                }
                return out

            assert thought['action'] == 'act'
            think_content = thought['content']
            if think_content:
                print(f'{think_content}\n')

            acts = thought['acts']
            for act in acts:
                print(f'[使用工具] -> {act["tool_name"]}')
                if act['tool_name'] == 'code_agent' and self.args.code_agent_type == 'agent':
                    llm_input = self.brain.construct_llm_input('', 'execute_next', previous_turns, note, no_user=True)
                    messages = llm_input['messages']
                    messages = messages[:-1]
                    act['tool_input'] = {
                        'messages': messages
                    }
                    if self.args.unified_agent:
                        previous_turns = previous_turns[:-1]

                obs = self.body.act(act['tool_input'], act['tool_name'], previous_turns)

                if act['tool_name'] == 'code_agent' and self.args.unified_agent and self.args.code_agent_type == 'agent':
                    previous_turns += obs['tool_output']
                else:
                    tool_message = {
                        "tool_call_id": act['tool_id'],
                        "role": "tool",
                        "name": obs['tool_name'],
                        "content": str(obs['tool_output']),
                    }
                    previous_turns.append(tool_message)
                act_log = {
                    'name': obs['tool_name'],
                    'input': act['tool_input'],
                    'output': obs['tool_output'],
                }
                act_logs.append(act_log)

    def reset(self):
        self.n_execute = 0
