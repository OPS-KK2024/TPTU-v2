""" 公安业务中掉用api接口工具 """
from autotask.prompt.prompt import Prompt
from autotask.llm.sensechat import SenseChat


class PythonREPL:
    name = "PythonREPL"
    description = "Simulation of a standalone Python REPL. Can execute python code."

    def __init__(self, config) -> None:
        self.prompt = Prompt()
        self.python_llm = SenseChat(config)
        self.python_error = ""

    def __call__(self, command: str) -> str:
        retry = 10
        while retry > 0:
            try:
                python_prompt = self.prompt.python_prompt().format(question=command+' '+self.python_error)
                answer = self.python_llm(python_prompt, stop=['Answer'])
                idx = answer.find('def solution')
                python_answer = answer[idx:]
                print("\tPythonREPL Code:\n \033[93m{}\033[0m".format(python_answer))

                output = {}
                exec(python_answer, globals(), output)
                # print(output)  # {'solution': <function solution at 0x000001DCBE72A940>}
                return str(output['solution']())
            except TypeError:
                print('\n\033[91mPython语句不正确\033[0m')
                self.python_error = '\n你之前生成的Python代码是:\n'+python_answer+'\n该Python代码无法正确执行，请重新生成一段语法正确的Python代码。'
                retry -= 1
                continue
            except SyntaxError:
                print('\n\033[91mPython语句不正确\033[0m')
                self.python_error = '\n你之前生成的Python代码是:\n'+python_answer+'\n该Python代码无法正确执行，请重新生成一段语法正确的Python代码。'
                retry -= 1
                continue
        return "tool retry 10 times"

