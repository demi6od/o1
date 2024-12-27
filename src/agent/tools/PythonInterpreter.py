import logging
import traceback
# from pumpcoder_sandbox_client import RunCKernelClient

from src.agent.tools.base_Tool import Tool

logger = logging.getLogger('PythonInterpreter')

class PythonInterpreter(Tool):
    def __init__(self, args, server):
        super().__init__(args, server)

        self.schema = {
            "type": "function",
            "function": {
                "name": "python_interpreter",
                "description": "This function serves as a Python interpreter, executing provided Python code within certain constraints. It is designed to process a variety of Python scripts, with the final output expected to be assigned to a variable named 'result'.",
                # "description": "This function serves as a Python interpreter, executing provided Python code within certain constraints. It is designed to process a variety of Python scripts.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The Python code to be executed. It should be well-formed and follow standard Python syntax. Execution constraints apply, such as a maximum runtime duration. The output of the code should be stored in a variable named 'result'."
                            # "description": "The Python code to be executed. It should be well-formed and follow standard Python syntax. Execution constraints apply, such as a maximum runtime duration."
                        }
                    },
                    "required": ["code"]
                }
            }
        }

        self.name = self.schema['function']['name']
        self.connect()

    def connect(self):
        # self.client = RunCKernelClient(host='10.4.236.13', port=19817, token='HelloAssistantsAndAgents', msg_timeout=200)
        pass

    def run(self, code):
        if self.args.tool_server:
            # out = self.execute(code)
            out = self.execute_local(code)
        else:
            # out = self.execute(code)
            out = self.execute_api(code)
        return out

    def execute(self, code):
        try:
            res = self.client.execute_code_blocking(code)
            out = {
                'result': str(res.result),
                'error': str(res.error),
            }
        except Exception as e:
            out = f'Run python code exception: {str(e)}'
            if 'websocket connection is closed' in out:
                self.connect()
        return out

    @staticmethod
    def execute_local(code):
        try:
            exec(code, locals())
            out = locals().get('result')
            if out is None:
                out = "final result is not put into 'result' variable"
            else:
                out = str(out)
        except Exception as e:
            out = f'Run python code exception: {str(e)}, traceback={traceback.format_exc()}'
        return out

    def execute_api(self, code):
        sample = {
            'code': code,
        }
        rsp = self.server.api(sample, self.name)
        return rsp

    def reset(self):
        try:
            self.client.reset()
        except Exception as e:
            self.connect()
