
'''
============================
Utils for agent
============================
'''

from autotask.llm.sensechat import SenseChat
from autotask.llm.sensenova import SenseNova
from autotask.llm.ziya import Ziya
from autotask.llm.gpt import GPT
from autotask.llm.chatgpt import ChatGPT
from autotask.llm.sensechat_finetune import SenseChatFinetune


def instantiate_llm(config):
    '''
    instantiate the LLMs according to the config file
    input:
        config: -> dict: the configuration read from config_API_retriever.yaml file
    output:
        LLM instance: -> ClassName:  an instance of the specific class in autotask.llm
    
    '''
    assert 'llm_name' in config, 'Lack the name of LLM, please check the config_API_retriever.yaml file.'
    assert config["llm_name"] in config["supported_llm"], f"No such LLM named {config['llm_name']}, please check the llm_name in config_API_retriever.yaml file."
    if config["llm_name"] in ("sensechat-13B", "sensechat-120B", "sensechat-180B"):
        return SenseChat(config)
    elif config["llm_name"] in ("sensenova-xs", "sensenova-xl"):
        return SenseNova(config)
    elif config["llm_name"] == "ziya-13B":
        return Ziya(config)
    elif config["llm_name"] in ("gpt-3.5"):
        return GPT(config)
    elif config["llm_name"] in ("chatgpt"):
        return ChatGPT(config)
    elif config["llm_name"].startswith("sensechat-120B-FT-"):
        return SenseChatFinetune(config)
    else:
        print('No implement of {}.'.format(config["llm_name"]))

