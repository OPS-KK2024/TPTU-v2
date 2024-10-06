from typing import List, Optional
import requests
import time
import openai
from langchain import OpenAI
from autotask.utils.llm_utils import parsing_output_of_llm


class GPT:
    def __init__(self, config) -> None:
        self.config = config
        # loading gpt config
        llm_config = config["gpt"]
        self.url = llm_config["url"]
        self.data = {
            "model": llm_config["model_name"],
            "temperature": llm_config["temperature"],
            "max_tokens": llm_config["max_tokens"],
            "request_timeout": llm_config["request_timeout"],
            "openai_api_key": llm_config["openai_api_key"],
            "api2d_api_key": llm_config["api2d_api_key"],
        }
        openai.api_key = self.data["openai_api_key"]
        print('**** GPT has been successfully initialized ****')
        print('The details of [{}: {}] are listed as follows:'.format(config["llm_name"], self.data["model"]))
        if self.config["gpt"]["source"] == "api2d":
            print('URL: {}'.format(self.url))
        print('Data: {}'.format(self.data))
        print()

    def __call__(self, query: str, stop: Optional[List[str]] = None) -> str:
        # 返回查询的结果
        response_retry = self.config["max_response_retry_num"]
        while response_retry:
            try:
                if self.config["gpt"]["source"] == "openai":
                    response = openai.ChatCompletion.create(
                        model=self.data["model"],
                        messages = [
                            {'role': 'user', 'content': query}
                        ],
                        max_tokens=self.data["max_tokens"],
                        temperature=self.data["temperature"],
                    )
                    print('GPT response ==>', response)
                    message = response["choices"][0]["message"]["content"]
                elif self.config["gpt"]["source"] == "api2d":
                    llm = OpenAI(
                        model_name=self.data["model"],
                        max_tokens=self.data["max_tokens"],
                        temperature=self.data["temperature"],
                        openai_api_key=self.data["api2d_api_key"],
                        openai_api_base=self.url,
                        request_timeout=self.data["request_timeout"],
                    )
                    response = llm(query, stop=[])
                    print('GPT response ==>', response)
                    message = response
                else:
                    print('No such impletement of source from {}'.format(self.config["gpt"]["source"]))
                    exit()                
            except:
                time.sleep(5)
                response_retry -= 1
                continue 
            break
        if not response_retry:
            print('LLM response exception, exit...')
            exit()
        return parsing_output_of_llm(self.config['agent_type'], message, stop)