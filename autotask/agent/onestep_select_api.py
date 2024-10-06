from autotask.prompt.prompt_select_api import Prompt_Select
from autotask.llm.sensechat import SenseChat
from autotask.llm.sensenova import SenseNova
from autotask.llm.chatgpt import ChatGPT
from autotask.llm.ziya import Ziya
import queue

from autotask.tool.get_weather import GetWeather
from autotask.tool.signal_control import SignalControl
from autotask.tool.ids import IDS
from autotask.utils.plan_exception import FormatException, ReturnFormat


class SelectAgent():
    def __init__(self, config: dict, q_response: [queue] = None) -> None:
        self.config = config
        self.prompt = Prompt_Select()
        # 数据信息队列
        self.q_response = q_response

        assert 'llm_name' in config, 'Lack the name of LLM, please check the config.'
        assert config["llm_name"] in config[
            "supported_llm"], "No such LLM named {}, please check the llm_name in config.yaml.".format(
            config["llm_name"])
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
        elif config["llm_name"] in ("chatgpt"):
            if config["mode"] != "test":
                self.action_llm = ChatGPT(config)
            self.summary_llm = ChatGPT(config)
        else:
            print('No implement of {}.'.format(config["llm_name"]))
        print('---- CenturioAgent has been initialized successfully ----')
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
                # 尝试的次数
                retry = 0
                action_more_info = ""
                # 定义格式出错的次数
                format_err = 0

                while True:
                    retry += 1
                    if retry > self.config["max_retry_num"]:
                        break
                    try:
                        print("================================START================================")
                        # action_prompt = self.prompt.system_prompt_select().format(question=instruction)
                        action_prompt = self.prompt.system_prompt_select()
                        # print(action_prompt)

                        # 调用llm，返回执行结果
                        actions = self.action_llm(action_prompt, stop=['\nstop'])
                        # print(actions)
                        str_action = str(actions)

                        # 解析对应的工具和参数/生成的代码
                        # tool = (str_action[str_action.find("Tool:") + 5:str_action.find("\nInput")]).replace(" ", "")
                        # input = (str_action[str_action.find("Input:") + 6:]).replace(" ", "")
                        # print(tool, input)
                        # 调用具体的工具
                        code = str_action[str_action.find("answer:") + 9:]
                        print("-----------------------------code_start-----------------------------")
                        print(code)
                        print("------------------------------code_end------------------------------")
                        # input = (str_action[str_action.find("Input:") + 6:]).replace(" ", "")
                        ids = IDS(self.q_response)
                        weather = GetWeather()
                        signalcontrol = SignalControl(self.q_response)

                        exec(code)


                        if tool == "get_weather":
                            result = GetWeather.get_location_weather(input)
                            finall_prompt = self.prompt.final_answer_prompt_oneshot().format(question=instruction,
                                                                                             answer=result)
                            # 调用llm，返回执行结果
                            final_result = self.action_llm(finall_prompt, stop=['\nAnswer'])
                            print(final_result)
                            str_final_result = str(final_result)

                            if not self.q_response is None:
                                self.q_response.put(str_final_result)
                        if tool == "get_cycle" or tool == "get_strength":
                            # SignalControl = SignalControl(self.q_response)
                            signalcontrol = SignalControl(self.q_response)
                            print(input)
                            exec(input)
                        # 执行路径规划的工具
                        if tool == "get_location" :
                            ids = IDS(self.q_response)
                            print(input)
                            exec(input)
                        # if tool == "get_strength":
                        #     SignalControl = SignalControl(self.q_response)
                        #     print(input)
                        #     exec(input)

                        break
                    # 捕获语法错误
                    except (SyntaxError, AttributeError):
                        print("**********语法错误**********")
                        format_err += 1
                        print(format_err)
                        action_more_info += '\n你生成的语法有问题，请检查你的格式是否正确。请考虑生成更合理的Action来完成原始的问题{instruction}'.format(
                            instruction=instruction)
                    # 捕获格式错误
                    except FormatException:
                        print("**********格式错误**********")
                        format_err += 1
                        print(format_err)
                        action_more_info += '\n你生成的语法有问题，请检查你的格式是否正确。请考虑生成更合理的Action来完成原始的问题{instruction}'.format(
                            instruction=instruction)
                    # 捕获其他错误
                    except Exception as error:
                        print("**********其他错误**********")
                        print(error)
                # 函数返回，最终plan的结果
                return final_answer
            else:
                print('No such mode, please check the mode in config.yaml.')
        else:
            print('Please specify the code execution mode.')
