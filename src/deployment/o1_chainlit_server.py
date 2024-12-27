import chainlit as cl
import re
import pandas as pd
import shutil
import traceback
import os
import time
import base64
import sys
import json
import requests

PROJECT_DIR = os.path.join(os.path.dirname(__file__), '../..')
sys.path.append(PROJECT_DIR)

o1_url = 'http://10.198.7.37:12031/o1'

@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("messages", [])
    cl.user_session.set("img_id", 1)

@cl.step
async def thinking(msg):
    return msg

@cl.on_message
async def main(message: cl.Message):
    messages = cl.user_session.get("messages")

    # Show loading state
    msg = cl.Message(content="")
    await msg.send()

    # Get elements
    elems = message.elements
    content = message.content
    user_msg = {
        'role': 'user',
        'content': content,
    }
    messages.append(user_msg)
    sample = {
        'messages': messages
    }

    try:
        print(f'[+] in -> {sample}')
        r = requests.post(o1_url, json=sample, timeout=300)
        response = r.json()
        rsp = response['response']
        o1_dict = rsp['o1_dict']

        print(f'[+] out -> {rsp}')
    except Exception as e:
        err_msg = f'[-] o1 server error: {str(e)}, traceback: {traceback.format_exc()}'
        await cl.Message(
            content=err_msg,
        ).send()
        return

    # Show step messages
    task_titles = o1_dict['task_titles']
    final_answer = o1_dict['final_answer']
    for idx, task_title in enumerate(task_titles):
        msg = {
            'role': 'thought',
            'content': task_title
        }
        messages.append(msg)
        await thinking(msg['content'])

    # Show turn rsp
    rsp_content = final_answer
    messages.append(
        {
            'role': 'assistant',
            'content': final_answer
        }
    )

    out_str = (
        f'{rsp_content}'
    )
    out_msg = cl.Message(content=out_str, elements=elems)

    await out_msg.send()
    await out_msg.update()

    # Update message history
    cl.user_session.set("messages", messages)
