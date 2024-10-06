# coding=utf-8
from autotask.prompt.prompt_centurio_all import Centurio_Prompt
import requests
import json
import time
import pandas as pd

User_tokens = 'xoxp-5120950788050-5738419988613-5778118670595-d8d2883357ed9dd10c79891eec43b9ea'
channel = "D05MT9V9V7C"
# claude_id = 'U053CD9EJTY'
prompt = Centurio_Prompt()


def send_msg(msg):
    send_url = "https://slack.com/api/chat.postMessage"
    claude = ''

    data = {
        "token": User_tokens,
        "channel": channel,
        "text": claude + msg
    }
    response = requests.post(url=send_url, data=data)
    text = json.loads(response.text)
    return text


def receive_msg(ts):
    send_url = "https://slack.com/api/conversations.history"
    data = {
        "token": User_tokens,
        "channel": channel,
        "ts": ts,
        "oldest":ts
    }
    response = requests.post(url=send_url, data=data)
    text = json.loads(response.text)
    return text
qa_data = json.load(open('./database/qa_30_SenseCenturio.json', encoding='utf-8'))
final_file = open('database/Claude_Question_0905_05.txt', 'a', encoding='utf-8')
for i in range(25,31):
    qad = qa_data['Q' + str(i)]
    instruction = qad['question']
    action_prompt = prompt.sys_prompt().format(question=instruction)
    data = send_msg(action_prompt)
    ts = data["ts"]
    text_test = ''
    while True:
        answer = receive_msg(ts)
        if len(answer['messages']) != 0:
            text = answer['messages'][0]['text']
            if text != text_test:
                if 'Typing' not in text:
                    text_test = text
            else:
                final_str = "第%s个问题：" % i + "\n" + qad['question'] + str(text_test) + "\n\n"
                final_file.write(final_str)
                print(text_test)
                break
# format_prompt = prompt.format_prompt().format(info=text_test)
# data = send_msg(format_prompt)
# # print(data)
# ts = data["ts"]
# text_test = ''
# while True:
#     answer = receive_msg(ts)
#     if len(answer['messages']) != 0:
#         text = answer['messages'][0]['text']
#         if text != text_test:
#             if 'Typing' not in text:
#                 text_test = text
#         else:
#             print(text_test)
#             break
