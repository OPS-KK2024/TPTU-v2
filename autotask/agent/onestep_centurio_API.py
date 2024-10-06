from autotask.prompt.prompt_centurio_API import Centurio_Prompt
from autotask.llm.sensechat import SenseChat
from autotask.llm.sensenova import SenseNova
from autotask.llm.chatgpt import ChatGPT
from autotask.llm.ziya import Ziya
import queue
from autotask.utils.plan_exception import FormatException, ReturnFormat


class CenturioAgent():
    def __init__(self, config: dict, q_response: [queue] = None) -> None:
        self.config = config
        self.prompt = Centurio_Prompt()
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

    def __call__(self, instruction: str,  function: str, prompt_suffix: str) -> str:
        if 'mode' in self.config:
            if self.config['mode'] == 'test':
                print(f'User Instruction: {instruction}.')
                final_answer = self.summary_llm(instruction)
                print('LLM Final Answer:')
                print(final_answer)
                return ''
            elif self.config['mode'] == 'val_planning':
                final_answer = ""
                final_answer_01 = ""
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
                        action_prompt = self.prompt.sys_prompt_function().format(question=instruction, function=function, prompt_suffix=prompt_suffix)
                        print(action_prompt)

                        # 调用llm，返回执行结果
                        actions = self.action_llm(action_prompt, stop=['\nAnswer'])
                        print('ACTION: ', actions)
                        str_action_01 = str(actions)
                        final_answer_01 = str_action_01

                        while True:
                            try:
                                print('---------------------------------------')
                                # 调用第二次的LLN输出模块名称
                                format_prompt = self.prompt.format_prompt().format(info=str_action_01)
                                print("format_prompt",format_prompt)
                                # 调用llm，返回执行结果
                                actions = self.action_llm(format_prompt, stop=['\nAnswer'])
                                print('ACTION: ', actions)
                                str_action = str(actions)
                                print(str_action)
                                # 创建ReturnFormat，并进行格式正确性的判断
                                return_format = ReturnFormat()
                                return_format.return_format(str_action)
                                # 截取其中最终的结果
                                result = str_action[str_action.find("Result: ") + 8:]

                                # print(result)
                                # 中间结果保存在队列里面
                                # self.q_response.put(result)
                                if not self.q_response is None:
                                    self.q_response.put(str_action)

                                # 如果全都正确，返回最终答案
                                final_answer = result
                                break
                            # 捕获格式错误
                            except FormatException:
                                print("**********格式错误**********")
                                format_err += 1
                                print(format_err)
                                action_more_info += '\n你生成的语法有问题，请检查你的格式是否正确。请考虑生成更合理的Action来完成原始的问题{instruction}'.format(
                                    instruction=instruction)

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
                return final_answer + "||" + str(final_answer_01)
            else:
                print('No such mode, please check the mode in config.yaml.')
        else:
            print('Please specify the code execution mode.')
