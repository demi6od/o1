import json
import logging

logger = logging.getLogger('OutputParser')

class OutputParser:
    def __init__(self, args):
        self.args = args

    def extract_json(self, text):
        text = text.replace('：', ':')
        content = json.loads(text, strict=False)
        return content

    @staticmethod
    def parse_tool_param(param):
        if 'tool_input' in param:
            tool_input = param['tool_input']
        else:
            tool_input = param['tool_inputs']

        if 'tool_name' in param:
            tool_name = param['tool_name']
        elif 'tools_name' in param:
            tool_name = param['tools_name']
        elif 'ToolName' in param:
            tool_name = param['ToolName']
        else:
            tool_name = param['工具_name']

        if isinstance(tool_input, str):
            if tool_name == 'web_search':
                tool_input = {"query": tool_input}
            elif tool_name == 'python_interpreter':
                tool_input = {"code": tool_input}
            elif tool_name == 'code_agent':
                tool_input = {"query": tool_input}
            elif tool_name == 'knowledge_retrieval':
                tool_input = {"query": tool_input}
            elif tool_name == 'text2image':
                tool_input = {"prompt": tool_input}
        content = {
            'tool_name': tool_name,
            'tool_input': tool_input
        }
        return content

    def parse(self, llm_rsp, think_type):
        action = ''
        content = ''
        llm_content = llm_rsp['content']
        if think_type == 'plan_next':
            out = self.extract_json(llm_content)
            if 'action' in out:
                action = out['action']
            else:
                action = out['Action']

            if action == 'Execute Sub-task':
                action = 'execute'
                content = {
                    'sub_task': out['sub_task'],
                    'related_information': out['related_information'],
                }
            elif action == 'Update Work Notes':
                action = 'update'
                content = out['work_note']
            elif action == 'Task Completed':
                action = 'finish'
        elif think_type == 'execute_next':
            content = llm_rsp['content']
            tool_calls = llm_rsp.get('tool_calls', None)
            if tool_calls:
                acts = self.get_actions(tool_calls)
                thought = {
                    'action': 'act',
                    'content': content,
                    'acts': acts,
                    'message': llm_rsp,
                }
                return thought
            else:
                action = 'response'
        else:
            content = llm_content

        thought = {
            'action': action,
            'content': content,
        }
        return thought

    def get_actions(self, tool_calls):
        acts = []
        for tool_call in tool_calls:
            function_name = tool_call['function']['name']
            function_args = tool_call['function']['arguments']
            if isinstance(function_args, str):
                function_args = eval(tool_call['function']['arguments'])
                # function_args = json.loads(tool_call['function']['arguments'], strict=False)
            act = {
                'tool_name': function_name,
                'tool_input': function_args,
                'tool_id': tool_call['id'],
            }
            acts.append(act)
        return acts

    def parse_multi(self, out, agent_name):
        if agent_name == 'main':
            return out
        else:
            new_messages = []
            for new_message in out['new_messages']:
                if new_message['role'] == 'assistant':
                    new_message['role'] = f'assistant_{agent_name}'
                    new_messages.append(new_message)
            return new_messages
