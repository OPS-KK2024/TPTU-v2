from typing import List, Optional
import requests
import time

from autotask.utils.general_utils import find_stop_in_message


class SenseNova():
    def __init__(self, config) -> None:
        self.config = config
        # loading sensenova config
        llm_config = config["sensenova"]
        self.url = llm_config["url"]
        self.data = {
            "model": llm_config["model"][config["llm_name"]],
            "messages": llm_config["messages"],
            "temperature": llm_config["temperature"],
            "top_p": llm_config["top_p"],
            "max_new_tokens": llm_config["max_new_tokens"],
            "repetition_penalty": llm_config["repetition_penalty"],
            "stream": llm_config["stream"],
            "user": llm_config["api_user"]
        }
        self.headers = {
            'Content-Type': llm_config["Content-Type"],
            'Authorization': llm_config["api_secret_key"]
        }
        print('**** SenseNova has been successfully initialized ****')
        print('The details of [{}: {}] are listed as follows:'.format(config["llm_name"], self.data["model"]))
        print('URL: {}'.format(self.url))
        print('Data: {}'.format(self.data))
        print('Headers: {}'.format(self.headers))
        print()

    def __call__(self, query: str, stop: Optional[List[str]] = None) -> str:
        # 设置查询的问题
        self.data["messages"][0]["content"] = query

        # 返回查询的结果
        response = requests.post(self.url, headers=self.headers, json=self.data)
        print('SenseNova response ==>', eval(response.text))
        message = eval(response.text)['data']['choices'][0]['message']

        stop_idx = find_stop_in_message(stop, message)

        # 调用限制：每3sec调用1次
        time.sleep(3)
        return message[: stop_idx]

