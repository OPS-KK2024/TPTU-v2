from typing import List, Optional
import requests
import time

from autotask.utils.general_utils import find_stop_in_message


class Ziya():
    def __init__(self, config) -> None:
        self.config = config 
        # loading ziya config
        llm_config = config["ziya"]
        self.url = llm_config["url"]
        self.data = {
            "model": llm_config["model"],
            "messages": llm_config["messages"],
            "temperature": llm_config["temperature"],
            "top_p": llm_config["top_p"],
            "max_new_tokens": llm_config["max_new_tokens"],
            "disable_prompt_adapter": llm_config["disable_prompt_adapter"],
            "do_sample": llm_config["do_sample"],
        }
        print('**** Ziya has been successfully initialized ****')
        print('The details of [{}: {}] are listed as follows:'.format(config["llm_name"], self.data["model"]))
        print('URL: {}'.format(self.url))
        print('Data: {}'.format(self.data))
        print()

    def __call__(self, query: str, stop: Optional[List[str]] = None) -> str:   
        # 设置查询的问题    
        self.data["messages"][0]["content"] = query

        # 返回查询的结果
        response = requests.post(self.url, json=self.data)
        print('Ziya response ==>', eval(response.text))
        message = eval(response.text)['choices'][0]['message']
        message = message['content']

        stop_idx = find_stop_in_message(stop, message)

        # 调用限制：每3sec调用1次
        time.sleep(3)
        return message[:stop_idx]
 
