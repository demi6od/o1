import logging
import json
import requests

# from duckduckgo_search import DDGS

from src.agent.tools.base_Tool import Tool

logger = logging.getLogger('WebSearch')

class WebSearch(Tool):
    def __init__(self, args, server):
        super().__init__(args, server)

        self.top_k = 3

        self.schema = {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "This function acts as a search engine to retrieve a wide range of information from the web. It is capable of processing queries related to various topics and returning relevant results.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query used to retrieve information from the internet. While the primary language for queries is Chinese, queries in other languages are also accepted and processed."
                        }
                    },
                    "required": ["query"]
                }
            }
        }

        self.name = self.schema['function']['name']
        self.web_search_url = "http://10.112.97.25:32015/search"

    def run(self, query, top_k=3):
        if self.args.tool_server:
            out = self.search(query, top_k)
        else:
            out = self.search_api(query, self.top_k)
        return out

    def search_ddgs(self, query, top_k):
        web_contents = []
        with DDGS() as ddgs:
            # results = ddgs.text(query, max_results=top_k)
            print(query)
            results = ddgs.text(query)
            # results = results[:top_k]
            if results:
                for idx, result in enumerate(results):
                    if idx >= top_k:
                        break
                    web_contents.append(result['body'])
        return web_contents

    def search(self, query, top_k):
        data = {
            "query": query,
            "engine": self.args.engine,
        }
        headers = {
            "Content-type": "application/json"
        }
        rsp = requests.post(self.web_search_url, data=json.dumps(data), headers=headers)
        out = json.loads(rsp.text)

        answer = out['ans_dic']['ans_str']
        if answer:
            web_contents = [answer]
            return web_contents

        web_contents = []
        results = out['all_snip_dics']
        if results:
            results = results[:top_k]
            for result in results:
                if result['passage']:
                    web_contents.append(result['passage'])
                else:
                    web_contents.append(result['snippet'])
        return web_contents

    def search_api(self, query, top_k):
        sample = {
            'query': query,
            'top_k': top_k,
        }
        rsp = self.server.api(sample, self.name)
        return rsp
