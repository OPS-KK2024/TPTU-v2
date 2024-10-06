from autotask.prompt.prompt_onestep import Prompt_OneStep
from autotask.llm.sensechat import SenseChat
from autotask.llm.sensenova import SenseNova
from autotask.llm.ziya import Ziya
import queue


from autotask.utils.plan_exception import FormatException, ReturnFormat, ToolSelect, ToolException
from autotask.utils.agent_utils_API_retriever import instantiate_llm
from autotask.utils.prompt_utils_API_retriever import get_prompt, actions_postprocess


class CenturioAPIOneStepAgent():
    def __init__(self, config: dict, q_response: [queue] = None) -> None:
        self.config = config
        self.prompt, self.format_prompt = get_prompt(config)
        # 数据信息队列
        self.q_response = q_response
        # instantiate llm
        if config["mode"] != "test":
            self.action_llm = instantiate_llm(config)
        self.summary_llm = instantiate_llm(config)

        # # verify version compliance
        # self.agent_version = config["agent_version"]["onestep"]
        # assert self.agent_version <= config["latest_agent_version"]["onestep"], \
        # f"The version you specified, {self.agent_version}, is invalid. " + \
        # f"The latest version of the onestep agent is {config['latest_agent_version']['onestep']}. " +\
        # "Please check the config_API_retriever.yaml file."

        print('---- CenturioAPIOneStepAgent has been initialized successfully ----\n')
        # print('Current version is: {}\n'.format(self.agent_version))

    def __call__(self, instruction: str, **kwargs) -> str:
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
                actions = ""
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
                        # action_prompt = self.prompt.system_prompt_onestep().format(question=instruction, error=action_more_info)
                        action_prompt = self.prompt(question=instruction, error=action_more_info, **kwargs)
                        print('ACTION PROMPT: ', action_prompt)
                        # 调用llm，返回执行结果
                        actions = self.action_llm(action_prompt, stop=self.prompt.stop)
                        # print('[before postprocess]ACTION: ', actions)
                        # actions = actions_postprocess(actions)
                        # print('[after postprocess]ACTION: ', actions)
                        # # check
                        # check_action_01 = eval(actions)
                        # assert isinstance(check_action_01, list)
                        # for x in check_action_01:
                        #     assert isinstance(x, str)
                        
                        # str_action_01 = str(actions)
                        # final_answer_01 = str_action_01
                        # final_answer = final_answer_01
                        str_action_01 = str(actions)
                        final_answer_01 = str_action_01

                        while True:
                            try:
                                print('---------------------------------------')
                                # 调用第二次的LLN输出模块名称
                                format_prompt = self.format_prompt(info=str_action_01)
                                # print("format_prompt", format_prompt)
                                # 调用llm，返回执行结果
                                # actions = self.action_llm(format_prompt, stop=['\nAnswer'])
                                actions = self.action_llm(format_prompt, stop=self.format_prompt.stop)
                                # print('ACTION: ', actions)
                                str_action = str(actions)
                                # print(str_action)
                                # 创建ReturnFormat，并进行格式正确性的判断
                                ReturnFormat().return_format(str_action)
                                # 截取其中最终的结果
                                s_idx = 0
                                if str_action.find("Result: ") >= 0:
                                    s_idx = str_action.find("Result: ") + len("Result: ")
                                elif str_action.find("Result:") >= 0:
                                    s_idx = str_action.find("Result:") + len("Result:")
                                result = str_action[s_idx:]

                                # print(result)
                                # 中间结果保存在队列里面
                                # self.q_response.put(result)
                                if self.q_response is not None:
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
                            action=actions, error=error, instruction=instruction)
                        other_err += 1
                        print(error)
                # 函数返回，最终plan的结果
                return final_answer + "||" + str(final_answer_01)
            else:
                print('No such mode, please check the mode in config_API_retriever.yaml.')
        else:
            print('Please specify the code execution mode.')
