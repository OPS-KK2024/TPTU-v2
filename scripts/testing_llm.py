from autotask.agent import OneStepAgent
from autotask.agent import SequentialAgent

import os
import yaml

YAML_PATH = os.path.join("./autotask", "config.yaml")


if __name__ == '__main__':
    with open(YAML_PATH, 'r', encoding='utf-8') as f:
        config = yaml.load(f.read(), Loader=yaml.FullLoader)
    config['mode'] = 'test'

    # instruction = input('输入你的问题：')
    instruction = 'Please tell me a joke.'
    
    agent = OneStepAgent(config)
    agent(instruction)

