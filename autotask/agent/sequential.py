from autotask.prompt.prompt import Prompt
from autotask.llm.sensechat import SenseChat
from autotask.tool import (Echo, PythonREPL)


class SequentialAgent():
    def __init__(self, config: dict) -> None:
        self.config = config
        self.prompt = Prompt()
        self.action_llm = SenseChat(config)
        self.summary_llm = SenseChat(config)

    def __call__(self, instruction: str) -> None:
        print(f'User Instruction: {instruction}.')
        pass

