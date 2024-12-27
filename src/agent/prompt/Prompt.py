import logging

logger = logging.getLogger('Prompt')

class Prompt:
    def __init__(self, args):
        self.args = args

        self.work_note_desc = (
            f"Work Note Description:\n"
            f"1. A work note is a work plan and result record for completing the overall task, documenting work status, including a list of subtasks and corresponding result records. "
            f"Uses markdown format where heading levels represent task levels, forming a tree structure.\n"
            f"2. The first step is to assess the difficulty of the main task: if it's a simple task, execute it directly; "
            f"if it's a complex task, first update the work note with a detailed plan. The total number of subtasks should not exceed {self.args.max_sub_task}, and the last step in the plan is often to provide the final result based on all previous outcomes.\n"
            f"3. Decide the next action according to the plan: 'Execute Subtask', 'Update Work Note', or 'Task Completed'.\n"
            f"   Executing a subtask involves assigning it to an executor to carry out, filling in the task dependency information, often incorporating complete results from all relevant tasks in the work note.\n"
            f"   Updating the work note typically involves drafting or refining subsequent work plans, supplementing and improving task results, while keeping records of all completed subtasks. Try to keep the number of subtasks unchanged if possible.\n"
            f"   Task completion indicates the overall task is done.\n"
            f"4. The task result records should include as much useful information as possible. If a subtask cannot be completed during execution, record the useful information and skip it, proceeding with the next steps in the plan.\n"
            f"5. Keep records of all completed subtasks whenever possible, ensuring that the total number of subtasks in the note does not exceed {self.args.max_sub_task}.\n"
            f"6. The format of the work note should remain unchanged.\n"
            "\n"
            "Work Note Example:\n"
            "# Main Task: Description of the main task\n"
            "Status: In Progress.\n"
            "Result: None.\n"
            "## Subtask 1: Description of subtask 1\n"
            "Status: Completed.\n"
            "Result: Result of subtask 1.\n"
            "## Subtask 2: Description of subtask 2\n"
            "Status: In Progress.\n"
            "Result: None.\n"
            "### Subtask 2.1: Description of subtask 2.1\n"
            "Status: Completed.\n"
            "Result: Result of subtask 2.1.\n"
            "### Subtask 2.2: Description of subtask 2.2\n"
            "Status: Not Started.\n"
            "Result: None.\n"
        )

        self.tool_prompt = {
            'web_search': 'When additional information is needed, you can use the search engine (web_searcher tool) to search for knowledge online.',
            'knowledge_retrieval': 'When additional information is needed, you can use the professional knowledge base (knowledge_retrieval tool) to retrieve knowledge and information in the finance and banking fields.',
            'python_interpreter': 'You can write Python code and use the Python code interpreter (python_interpreter tool) to execute the code to obtain results and help solve problems.',
            'code_agent': 'You can call the code_agent to help you solve problems.',
            'text2image': 'You can use text-to-image (text2image tool) to generate images.'
        }

        self.profile = {
            'open_domain_expert': (
                "I am an expert in open domains, capable of solving various complex problems, and can answer questions in English."
            )
        }

    def get_profile(self, role):
        if self.args.profile == 'default':
            profile_prompt = f'{self.profile[role]}\n'
            for tool in self.args.tools:
                profile_prompt += f'{self.tool_prompt[tool]}\n'
        else:
            profile_prompt = self.args.profile

        return profile_prompt

    def get_work_note_desc(self):
        return self.work_note_desc

    def construct(self, think_input, think_type, note):
        # Planner
        if think_type == 'plan_next':
            work_note = think_input
            prompt = (
                'Please refer to the available tools in "<|tools|>", "<|Work Note Instructions|>", and the current "Work Notes" to decide on the next course of action. Respond in one of the following three JSON formats:\n'
                '{"thought": "[Fill in your thoughts]", "action": "Execute Sub-task", "sub_task": "[Fill in the sub-task to be executed]", "related_information": '
                '"[Fill in the relevant information this sub-task depends on, often the complete results of all related tasks in the "Work Notes"]"}\n'
                '{"thought": "[Fill in your thoughts]", "action": "Update Work Notes", "work_note": '
                '"[Fill in the updated work notes, usually for improvement plans and supplementing task results. Retain records of all completed sub-tasks and keep the task count as stable as possible]"}\n'
                '{"thought": "[Fill in your thoughts]", "action": "Task Completed"}\n'
                '\n'
                f'Work Notes:\n'
                f'{work_note}\n'
                f'\n'
                f'Next action:'
            )
        elif think_type == 'plan_update_result':
            work_note = think_input['work_note']
            obs = think_input['observation']
            prompt = (
                f'Please refer to "<|Work Note Description|>", the current "Work Note" and "Previous Subtask Results" to update the "Work Note", i.e., fill in the results and improve the subsequent plan (subtask list).\n'
                f'\n'
                f'Work Note:\n'
                f'{work_note}\n'
                f'\n'
                f'Previous Subtask Results:\n'
                f'{obs}\n'
                f'\n'
                f'Updated Work Note (try to maintain the same number of tasks):'
            )

        # Executor
        elif think_type == 'execute_next':
            if self.args.working_mode == 'plan':
                prompt = (
                    f'Task Record: {note}\n'
                    f'\n'
                    f'Current Task: {think_input}'
                )
            elif self.args.working_mode == 'execute':
                prompt = think_input
        elif think_type == 'execute_finish':
            if self.args.working_mode == 'plan':
                prompt = (
                    f'Task Record: {note}\n'
                    f'\n'
                    f'Current Task: {think_input}'
                )
            elif self.args.working_mode == 'execute':
                prompt = think_input
        else:
            prompt = str(think_input)
        return prompt
