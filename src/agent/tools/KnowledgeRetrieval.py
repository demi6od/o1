import logging

from src.agent.tools.base_Tool import Tool

logger = logging.getLogger('KnowledgeRetrieval')

class KnowledgeRetrieval(Tool):
    def __init__(self, args, server):
        super().__init__(args, server)

        self.qd_top_k = 1
        self.es_top_k = 1
        self.rank = True

        self.schema = {
            "type": "function",
            "function": {
                "name": "knowledge_retrieval",
                "description": "Retrieves specific information from a designated knowledge base, focusing on task-related knowledge. The function is designed to handle queries primarily in Chinese but can accept other languages.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query in Chinese used to retrieve information. The query should be formulated clearly and can include specific keywords or questions related to the desired information."
                        }
                    },
                    "required": ["query"]
                }
            }
        }

        self.name = self.schema['function']['name']

    def run(self, query):
        out = self.retrieve(query)
        return out

    def qq_retrieve(self, query):
        sample = {
            'search_query': query,
            'know_ids': self.args.know_ids,
            'retrieve_type': 'qq',
        }
        rsp = self.server.api(sample, self.name)
        return rsp

    def retrieve(self, query):
        sample = {
            'search_query': query,
            'qd_top_k': self.qd_top_k,
            'es_top_k': self.es_top_k,
            'rank': self.rank,
            'know_ids': self.args.know_ids,
            'retrieve_type': 'qd',
        }
        rsp = self.server.api(sample, self.name)
        return rsp
