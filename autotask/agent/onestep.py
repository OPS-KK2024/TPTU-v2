from autotask.prompt.prompt_onestep import Prompt_OneStep
from autotask.llm.sensechat import SenseChat
from autotask.llm.sensenova import SenseNova
from autotask.llm.ziya import Ziya

from autotask.tool import (Echo, PythonREPL)
from autotask.utils.plan_exception import ToolSelect, ToolException


class OneStepAgent():
    def __init__(self, config: dict) -> None:
        self.config = config
        self.prompt = Prompt_OneStep()
        assert 'llm_name' in config, 'Lack the name of LLM, please check the config.'
        assert config["llm_name"] in config["supported_llm"], "No such LLM named {}, please check the llm_name in config.yaml.".format(config["llm_name"])
        if config["llm_name"] in ("sensechat-13B", "sensechat-120B", "sensechat-180B"):
            if config["mode"] != "test":
                self.action_llm = SenseChat(config)
            self.summary_llm = SenseChat(config)
        elif config["llm_name"] in ("sensenova-xs", "sensenova-xl"):
            if config["mode"] != "test":
                self.action_llm = SenseNova(config)
            self.summary_llm = SenseNova(config)
        elif config["llm_name"] == "ziya-13B":
            if config["mode"] != "test":
                self.action_llm = Ziya(config)
            self.summary_llm = Ziya(config)
        else:
            print('No implement of {}.'.format(config["llm_name"]))
        print('---- OneStepAgent has been initialized successfully ----')
        print()

    def __call__(self, instruction: str) -> str:
        if 'mode' in self.config:
            if self.config['mode'] == 'test':
                print(f'User Instruction: {instruction}.')
                final_answer = self.summary_llm(instruction)
                print('LLM Final Answer:')
                print(final_answer)
                return ''
            elif self.config['mode'] == 'val_planning':
                final_answer = ""
                action_more_info = ""
                # 尝试的次数
                retry = 0
                # 定义格式出错的次数
                format_err = 0
                # 定义工具出错的次数
                tool_err = 0
                # 定义其他问题次数
                other_err = 0

                while True:
                    retry += 1
                    if retry > self.config["max_retry_num"]:
                        break
                    try:
                        print("================================START================================")
                        action_prompt = self.prompt.system_prompt_oneshot().format(question=instruction, error=action_more_info)
                        # 调用llm，返回执行结果
                        actions = self.action_llm(action_prompt, stop=['\nAnswer'])
                        print('ACTION: ', actions)
                        # 将规划的结果转化为list格式
                        # 捕获格式出错/语法错误的问题
                        actions = eval(actions)
                        # 进行plan工具正确的校验
                        for action in actions:
                            print('action type: ', type(action))
                            for tool, query in action.items(): # the action here is a dict that contains only one <tool, query> pair
                                # 解析得到对应的tool、query
                                print("tool: " + tool)
                                print("query: " + query)
                                # 创建toolselecet实例，并进行正确性的判断
                                tool_selecet = ToolSelect()
                                tool_selecet.tool_name(tool)
                        # 如果全都正确，返回最终答案
                        final_answer = actions
                        print("循环次数为：", retry, ";其中语法错误为: ", format_err, ";工具错误为: ", tool_err, ";其他错误为: ", other_err)
                        print("最终答案为：", final_answer, end='\n\n')
                        break

                    # 捕获语法错误
                    except (SyntaxError, AttributeError):
                        print("**********语法错误**********")
                        format_err += 1
                        print(format_err)
                        action_more_info += '\n你生成的语法有问题，请检查你的格式是否正确。请考虑生成更合理的Action来完成原始的问题{instruction}'.format(
                            instruction=instruction)
                    # 捕获工具选择错误
                    except ToolException:
                        print("**********工具错误**********")
                        tool_err += 1
                        print(tool_err)
                        action_more_info += '\n你生成的工具有问题，请检查你的工具是否正确。请考虑生成更合理的Action来完成原始的问题{instruction}'.format(
                            instruction=instruction)
                    # 捕获其他错误
                    except Exception as error:
                        print("**********其他错误**********")
                        action_more_info += '\n你生成的{action}有问题，具体错误为{error}。请考虑生成更合理的Action来完成原始的问题{instruction}'.format(
                            action=action, error=error, instruction=instruction)
                        other_err += 1
                        print(error)
                # 函数返回，最终plan的结果
                return final_answer
            else:
                print('No such mode, please check the mode in config.yaml.')
        else:
            print('Please specify the code execution mode.')
