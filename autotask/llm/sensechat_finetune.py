from typing import List, Optional
import requests
import time
from autotask.utils.llm_utils import parsing_output_of_llm


class SenseChatFinetune:
    def __init__(self, config) -> None:
        self.config = config
        # loading sensechat config
        llm_config = config["sensechat_finetune"]
        self.url = llm_config["url"]
        self.data = {
            "endpoint": llm_config["model"][config["llm_name"]],
            "inputs": "",
            "parameters": {
                "temperature": llm_config["temperature"],
                "top_p": llm_config["top_p"],
                "max_new_tokens": llm_config["max_new_tokens"],
                "repetition_penalty": llm_config["repetition_penalty"],
                "stop": llm_config["stop"]
            }
        }
        self.headers = {
            'Content-Type': llm_config["Content-Type"],
        }
        print('**** SenseChatFinetune has been successfully initialized ****')
        print('The details of [{}: {}] are listed as follows:'.format(config["llm_name"], llm_config["model"][config["llm_name"]]))
        print('URL: {}'.format(self.url))
        print('Data: {}'.format(self.data))
        print('Headers: {}'.format(self.headers))
        print()

        # PROMPT_TEMPLATE = "<系统> {system_prompt} <对话历史> {history_text} <知识> {knowledge} <最新问题> {user_new_query} SenseChat："
        self.prompt_prefix = "<系统>  <对话历史>  <知识>  <最新问题> "
        # self.prompt_prefix = "<系统> <对话历史> <知识> <最新问题> "
        self.prompt_suffix = " SenseChat："
        self.stop = llm_config["stop"]

    def __call__(self, query: str, stop: Optional[List[str]] = None) -> str:
        # 设置查询的问题
        # self.data["inputs"] = query
        self.data["inputs"] = self.prompt_prefix + query + self.prompt_suffix
        
        # add stop when post, which is hard to use. Clip the response with local function is recommended
        # if stop is not None:
        #     new_stop = [s for s in self.stop]  # deep copy
        #     new_stop.extend(stop)
        #     new_stop = list(set(new_stop))  # reduplicate
        #     self.data["parameters"]["stop"] = new_stop
        # else:
        #     self.data["parameters"]["stop"] = self.stop
        self.data["parameters"]["stop"] = ['\n\n\n\n']
        # if stop is not None:
        #     stop += self.stop
        # else:
        #     stop = self.stop
        
        # 返回查询的结果
        response_retry = self.config["max_response_retry_num"]
        while response_retry:
            try:
                response = requests.post(self.url, headers=self.headers, json=self.data, stream=False)
                assert  response.status_code == 200
                print('SenseChatFinetune response ==>', eval(response.text))
                message = response.json()["generated_text"]
            except:
                time.sleep(5)
                response_retry -= 1
                continue 
            break
        if not response_retry:
            print('LLM response exception, exit...')
            # exit()
            raise Exception('LLM response exception, exit...')
        return parsing_output_of_llm(self.config['agent_type'], message, stop)
