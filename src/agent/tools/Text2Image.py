import logging
import time
import requests

from src.agent.tools.base_Tool import Tool
from src.utils.utils import generate_rand_id

logger = logging.getLogger('Text2Image')

class Text2Image(Tool):
    def __init__(self, args, server):
        super().__init__(args, server)

        self.schema = {
            "type": "function",
            "function": {
                "name": "text2image",
                "description": "This function generates a visual representation of a given textual description. It is capable of creating images in various styles based on the provided prompts, adhering to specified guidelines and constraints for content.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "A detailed textual description used to generate the image. The prompt should be clear and descriptive, potentially including details about the desired style, color scheme, and content of the image. There may be limitations on the length and complexity of the description."
                        }
                    },
                    "required": ["prompt"]
                }
            }
        }

        self.name = self.schema['function']['name']

        # self.api_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIyWlFhZFVRQ1J2SGJQN3hLTHJRNVBTQmJWangiLCJleHAiOjE3MjIxNjY3MDQsIm5iZiI6MTcwNDE2NjY5OX0.klOeFtFXnQVKm5Ezz2dD3X9X7lnup5FSJVW0qQkhMdA'
        self.api_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiIyWlFhZFVRQ1J2SGJQN3hLTHJRNVBTQmJWangiLCJleHAiOjE3MzEyNzQyNjAsIm5iZiI6MTcxMzI3NDI1NX0.mwh1c1qnGRFBMlCWTaca3cdSghOEmJC0A4tVNBjxDms'
        self.mirage_url = 'https://api.stage.sensenova.cn/v1/imgen/internal/generation_tasks'
        self.mirage_models_url = 'https://api.stage.sensenova.cn/v1/imgen/models'
        self.model_id = "sgl_artist_v0.4.0"
        self.headers = {
            "Authorization": f'Bearer {self.api_token}',
            "Content-Type": "application/json"
        }

        # models = self.ls_model()['data']
        # ids = [model['id'] for model in models]
        # print(ids)
        # time.sleep(100)

    def run(self, prompt):
        out = self.generate(prompt)
        return out

    def generate(self, prompt):
        # rand_url = f'https://{generate_rand_id()}.jpg'
        # return rand_url

        payload = {
            "prompt": prompt,
            "model_id": self.model_id,
        }

        r = requests.post(self.mirage_url, json=payload, headers=self.headers)
        rsp = r.json()
        task_id = rsp['task_id']
        img_url = self.get_img_wait(task_id)
        return img_url

    def ls_model(self):
        r = requests.get(self.mirage_models_url, headers=self.headers)
        rsp = r.json()
        return rsp

    def get_img_wait(self, task_id):
        img_url = ''
        while not img_url:
            time.sleep(1)
            img_url = self.get_img(task_id)
        return img_url

    def get_img(self, task_id):
        url = f'{self.mirage_url}/{task_id}'
        r = requests.get(url, headers=self.headers)
        rsp = r.json()
        task = rsp['task']
        state = task['state']
        if state == 'SUCCESS':
            img_url = task['result'][0]['raw']
        else:
            img_url = ''
        return img_url

    def generate_diffusion(self, prompt):
        sample = {
            'prompt': prompt,
        }
        url = self.server.api(sample, self.name)
        return url


# text2img = Text2Image(None, None)
# task_id = 'eddf5041-fd03-4591-b300-0e664dad86f4'
# img_url = text2img.get_img(task_id)
#
# print(img_url)
