import logging
import time

# from src.agent.tools.PythonInterpreter import PythonInterpreter
from src.agent.tools.WebSearch import WebSearch
from src.agent.tools.GeneralTool import GeneralTool
from src.agent.tools.ToolServer import ToolServer
from src.agent.tools.KnowledgeRetrieval import KnowledgeRetrieval
from src.agent.tools.Text2Image import Text2Image

logger = logging.getLogger('ToolManager')

class ToolManager:
    def __init__(self, args):
        self.args = args

        self.tool_server = ToolServer(args)

        self.knowledge_retrieval = KnowledgeRetrieval(args, self.tool_server)
        # self.python_interpreter = PythonInterpreter(args, self.tool_server)
        self.web_search = WebSearch(args, self.tool_server)
        self.text2image = Text2Image(args, self.tool_server)
        self.general_tool = GeneralTool(args, self.tool_server)

        self.tool_set = {
            # 'python_interpreter': self.python_interpreter,
            # 'web_search': self.web_search,
            'knowledge_retrieval': self.knowledge_retrieval,
            'text2image': self.text2image,
            'general_tool': self.general_tool,
        }
        self.tool_dict = {}

    def update(self):
        self.tool_dict = {}
        for tool in self.args.tools:
            if tool in self.tool_set:
                self.tool_dict[tool] = self.tool_set[tool]
            else:
                self.tool_dict[tool] = self.general_tool

    def use(self, tool_input, tool_name, history_messages):
        if tool_name not in self.tool_set:
            tool_input = {
                'tool_name': tool_name,
                'tool_input': tool_input,
                'history_messages': history_messages,
            }

        out = None
        time.sleep(1)
        for i in range(5):
            try:
                out = self.tool_dict[tool_name].run(**tool_input)
                break
            except Exception as e:
                err_msg = f'[*] tool exception tool_name={tool_name}, tool_input={tool_input}, error={e}'
                logger.warning(err_msg)
                if 'read timeout' in err_msg:
                    break
                time.sleep(5)
        else:
            logger.error(err_msg)
        return out

    def schema(self):
        schemas = []
        for key, tool in self.tool_dict.items():
            schema = tool.get_schema(key)
            schemas.append(schema)
        return schemas

    def reset(self):
        pass
        # self.python_interpreter.reset()
