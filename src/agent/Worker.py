import logging
import copy
import json

logger = logging.getLogger('Worker')

class Worker:
    def __init__(self, args, planner, executor):
        self.args = args

        self.planner = planner
        self.executor = executor

        self.task = ''
        self.work_note = ''
        self.sub_task_log = []

        self.n_step = 0

        self.messages_history = []
        self.messages_new = []

    def step(self):
        finish = False

        next_act = self.planner.next_step(self.work_note)

        next_act_str = json.dumps(next_act, indent=4, ensure_ascii=False)
        logger.info(
            f'[+] work_step_{self.n_step} start, next_action:\n'
            f'{next_act_str}\n'
        )

        if next_act['action'] == 'finish' or self.n_step >= self.args.max_work_step:
            finish = True
            final_task = (
                f'Based on the work records in the notes, conduct a comprehensive analysis and integration, and provide the detailed final result for the following "Main Task", including complete calculation steps.\n'
                f'Main Task: {self.task}'
            )
            out = self.executor.execute(final_task, [], self.work_note)
            result = out['response']
            self.work_note = (
                f'{self.work_note}\n'
                f'\n'
                f'# Main Task: {self.task}\n'
                f'[Final Result]:\n'
                f'{result}\n'
            )
        elif next_act['action'] == 'execute':
            sub_task = next_act['content']['sub_task']

            # related_information = next_act['content']['related_information']
            related_information = self.work_note

            out = self.executor.execute(sub_task, [], related_information)
            result = out['response']
            obs = {
                'sub_task': sub_task,
                'result': result,
                'actions': out['act_logs']
            }
            self.sub_task_log.append(obs)
            self.work_note = self.planner.update_result(self.work_note, obs)
        elif next_act['action'] == 'update':
            self.work_note = next_act['content']

        logger.info(
            f'[+] work_step_{self.n_step} end, work_note:\n'
            f'{self.work_note}\n'
        )
        return finish

    def run(self, task, previous_turns, note=''):
        self.task = task
        self.work_note = f'# Main Task: {task}'

        self.messages_history = copy.deepcopy(previous_turns)

        if self.args.working_mode == 'plan':
            finish = False
            while not finish:
                self.n_step += 1
                finish = self.step()
        elif self.args.working_mode == 'execute':
            out = self.executor.execute(task, previous_turns, note)
            result = out['response']
            self.work_note = (
                f'# Main Task: {self.task}\n'
                f'[Final Result]:\n'
                f'{result}\n'
            )

        return self.work_note

    def show(self):
        logger.info(
            f'[+] work_note:\n'
            f'{self.work_note}\n'
        )

    def reset(self):
        self.n_step = 0

        self.planner.reset()
        self.executor.reset()
