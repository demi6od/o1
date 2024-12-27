# -*- coding: utf-8 -*-

import requests


def generate(messages, intent_model, model_url):
    url = f"http://10.121.4.11:8001/chat_complete"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "messages": messages,
        "model_name": intent_model,
        "model_url": model_url
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        out = response.json().get('response')
        return out
    else:
        # print(response.json())
        raise Exception(f"Error: {response.json().get('error')}")


if __name__ == "__main__":
    messages = [{"role": "user", "content": "The equation $\\left(m+2\\right)x^{|m|}+3mx+1=0$ is a quadratic equation in $x$. Find the value of $m$."}]
    print(generate(messages, 'qwen', '103.177.28.206:22222'))
    # print(generate(messages, "gpt4o-ptu-client", ""))
