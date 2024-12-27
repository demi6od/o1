import logging

logger = logging.getLogger('Planner')

class Planner:
    def __init__(self, args, brain):
        self.args = args
        self.brain = brain

    def next_step(self, work_note):
        thought = self.brain.think(work_note, 'plan_next')
        return thought

    def update_result(self, work_note, obs):
        think_input = {
            'work_note': work_note,
            'observation': obs
        }
        thought = self.brain.think(think_input, 'plan_update_result')
        new_work_note = thought['content']
        return new_work_note
