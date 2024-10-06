from autotask.prompt.prompt_select_api_split_API import Prompt_Select
from autotask.llm.sensechat import SenseChat
from autotask.llm.sensenova import SenseNova
from autotask.llm.chatgpt import ChatGPT
from autotask.llm.ziya import Ziya
import queue
import re

from autotask.tool.get_weather import GetWeather
from autotask.tool.signal_control import SignalControl
from autotask.tool.ids import IDS
from autotask.tool.outlook import OutLook
from autotask.tool import get_weather
from autotask.tool import signal_control
from autotask.tool import ids
from autotask.utils.plan_exception import FormatException, ReturnFormat


class SelectAgent():
    def __init__(self, config: dict, q_response: [queue] = None, summarize: [queue] = None) -> None:
        self.config = config
        self.prompt = Prompt_Select()
        # 数据信息队列
        self.q_response = q_response
        # 总结
        self.summarize = summarize

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
                # 拆分问题的答案
                summarize_answer = []
                # 总结
                final_summarize = ''
                final_answer_all = []
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
                        # 拆分原始问题并选择合适的场景
                        select_sence_prompt = self.prompt.select_sence() + instruction
                        # print(select_sence_prompt)
                        # 拆分的结果
                        split_sence_result = self.action_llm(select_sence_prompt, stop=['\nstop'])
                        print(split_sence_result)
                        # 把涉及到的场景转换为list
                        split_sence_result_arr = eval(split_sence_result[split_sence_result.find("answer:") + 7:])
                        print("================================START================================")


                        # 初始化工具类
                        ids_func = IDS(self.q_response, self.summarize)
                        # weather = GetWeather(self.q_response)
                        signalcontrol = SignalControl(self.q_response, self.summarize)
                        outlook = OutLook(self.q_response, self.summarize)
                        # 数组清空
                        ids.address_arr.clear()
                        ids.coordinate_all.clear()
                        ids.coordinate_test.clear()
                        ids.uuid_all.clear()
                        # 根据拆分的场景切换到不同prompt
                        for i in split_sence_result_arr:
                            # 交通计算业务场景
                            if int(i) == 1:
                                signalcontrol_all = ['get_cycle', 'get_strength']
                                signalcontrol_prompt = self.prompt.signalcontrol_prompt()
                                action_prompt = signalcontrol_prompt + instruction

                                # 调用llm，返回执行结果
                                actions_ids = self.action_llm(action_prompt, stop=['\nstop'])
                                # 获得返回答案中的问题、伪代码列表
                                question_arr = []
                                # code_arr = []
                                code_arr = []
                                temp_code = ""
                                # 把返回的结果根据“换行”转换为列表
                                action_arr = list(actions_ids.split("\n"))
                                # 判断列表中，含有question则为拆分的子问题，含有=则为代码，其他均为无效信息
                                for str in action_arr:
                                    if "question" in str:
                                        question_arr.append(str)
                                        code_arr.append(temp_code.strip())
                                        temp_code = ""
                                    elif "=" in str:
                                        if "answer" in str:
                                            code = str[str.find("answer") + 7:]
                                        else:
                                            code = str
                                        temp_code = temp_code + code + "\n"
                                        # code_arr.append(code.strip())
                                code_arr.append(temp_code.strip())
                                del code_arr[0]
                                print("-------------------------------拆分结果-------------------------------")
                                print("\n原始问题为：" + instruction + "\n")
                                # print(question_arr)
                                # print(code_arr)
                                for i in range(0, len(question_arr)):
                                    print(question_arr[i])
                                    code_str = code_arr[i]
                                    for func in signalcontrol_all:
                                        if func in code_str:
                                            code_str = code_str.replace(func, "signalcontrol." + func)
                                    print("该步骤的伪代码：")
                                    print(code_str)
                                    exec(code_str)
                                    llm_answer =[]
                                    llm_summarize = []
                                    # 伪代码行数
                                    code_all = code_str.count('signalcontrol.')
                                    for n in range(code_all):
                                        index = len(self.q_response.queue) - (code_all - n)
                                        llm_answer.append(self.q_response.queue[index])
                                        # 总结所需答案
                                        llm_summarize.append(self.summarize.queue[index])
                                    # for n in range(len(self.q_response.queue)):
                                    #     llm_answer.append(self.q_response.queue[n])
                                    #     # 总结所需答案
                                    #     llm_summarize.append(self.summarize.queue[n])
                                    print("该步骤的答案：")
                                    print(llm_summarize, "\n")

                            # 个人助手场景
                            elif int(i) == 2:
                                # outlook相关函数
                                outlook_all = ['get_all_events', 'schedule_meeting', 'send_an_email', 'search_mail', 'get_weather']

                                outlook_prompt = self.prompt.outlook_prompt()
                                action_prompt = outlook_prompt + instruction
                                # 调用llm，返回执行结果
                                actions_ids = self.action_llm(action_prompt, stop=['\nstop'])
                                # 获得返回答案中的问题、伪代码列表
                                question_arr = []
                                # code_arr = []
                                code_arr = []
                                temp_code = ""
                                # 把返回的结果根据“换行”转换为列表
                                action_arr = list(actions_ids.split("\n"))
                                # 判断列表中，含有question则为拆分的子问题，含有=则为代码，其他均为无效信息
                                for str in action_arr:
                                    if "question" in str:
                                        question_arr.append(str)
                                        code_arr.append(temp_code.strip())
                                        temp_code = ""
                                    elif "=" in str:
                                        if "answer" in str:
                                            code = str[str.find("answer") + 7:]
                                        else:
                                            code = str
                                        temp_code = temp_code + code + "\n"
                                        # code_arr.append(code.strip())
                                code_arr.append(temp_code.strip())
                                del code_arr[0]
                                print("-------------------------------拆分结果-------------------------------")
                                print("\n原始问题为：" + instruction + "\n")
                                # print(question_arr)
                                # print(code_arr)
                                for i in range(0, len(question_arr)):
                                    print(question_arr[i])
                                    code_str = code_arr[i]
                                    for func in outlook_all:
                                        if func in code_str:
                                            code_str = code_str.replace(func, "outlook." + func)
                                    print("该步骤的伪代码：")
                                    print(code_str)
                                    exec(code_str)
                                    llm_answer =[]
                                    llm_summarize = []
                                    llm_summarize = []
                                    # 伪代码行数
                                    code_all = code_str.count('outlook.')
                                    for n in range(code_all):
                                        index = len(self.q_response.queue) - (code_all - n)
                                        llm_answer.append(self.q_response.queue[index])
                                        # 总结所需答案
                                        llm_summarize.append(self.summarize.queue[index])
                                    # for n in range(len(self.q_response.queue)):
                                    #     llm_answer.append(self.q_response.queue[n])
                                    print("该步骤的答案：")
                                    print(llm_summarize, "\n")


                            # 路径规划业务场景
                            elif int(i) == 3:
                                # 路径规划相关函数
                                ids_all = ['get_coordinate','get_uuid','get_route_result','get_poi_search','get_location_search','get_location_delete']
                                ids_prompt = self.prompt.ids_prompt()
                                action_prompt = ids_prompt + instruction
                                # 调用llm，返回执行结果
                                actions_ids = self.action_llm(action_prompt, stop=['\nstop'])
                                # 获得返回答案中的问题、伪代码列表
                                question_arr = []
                                # code_arr = []
                                code_arr = []
                                temp_code = ""
                                # 把返回的结果根据“换行”转换为列表
                                action_arr = list(actions_ids.split("\n"))
                                # 判断列表中，含有question则为拆分的子问题，含有=则为代码，其他均为无效信息
                                for str in action_arr:
                                    if "question" in str:
                                        question_arr.append(str)
                                        code_arr.append(temp_code.strip())
                                        temp_code = ""
                                    elif "=" in str:
                                        if "answer" in str:
                                            code = str[str.find("answer") + 7:]
                                        else:
                                            code = str
                                        temp_code = temp_code + code + "\n"
                                        # code_arr.append(code.strip())
                                code_arr.append(temp_code.strip())
                                del code_arr[0]
                                print("-------------------------------拆分结果-------------------------------")
                                print("\n原始问题为：" + instruction + "\n")
                                # print(question_arr)
                                # print(code_arr)
                                for i in range(0, len(question_arr)):
                                    print(question_arr[i])
                                    code_str = code_arr[i]
                                    for func in ids_all:
                                        if func in code_str:
                                            code_str = code_str.replace(func, "ids_func." + func)
                                    print("该步骤的伪代码：")
                                    print(code_str)
                                    exec(code_str)
                                    llm_answer =[]
                                    llm_summarize = []
                                    # 伪代码行数
                                    code_all = code_str.count('ids_func.')
                                    for n in range(code_all):
                                        index = len(self.q_response.queue) - (code_all - n)
                                        llm_answer.append(self.q_response.queue[index])
                                        # 总结所需答案
                                        llm_summarize.append(self.summarize.queue[index])
                                    # for n in range(len(self.q_response.queue)):
                                    #     llm_answer.append(self.q_response.queue[n])
                                    print("该步骤的答案：")
                                    print(llm_summarize, "\n")

                            # 不属于以上任何场景
                            elif int(i) == 4:
                                null_prompt = self.prompt.null_prompt().format(question=instruction)
                                # 调用llm，返回执行结果
                                actions_null = self.action_llm(null_prompt, stop=['\nstop'])
                                self.summarize.put(actions_null)
                                self.q_response.put('null')
                                print(actions_null)
                        # 总结
                        print("-------------------------------结果总结-------------------------------")
                        action_final = self.prompt.summarize_prompt().format(question=instruction, answer=list(self.summarize.queue))
                        # 调用llm，返回执行结果
                        final_summarize = self.action_llm(action_final, stop=['\nstop'])
                        print("最终答案：")
                        print(final_summarize, "\n")
                        break
                    # 捕获语法错误
                    except (SyntaxError, AttributeError):
                        print("**********语法错误**********")
                        format_err += 1
                        print(format_err)
                        self.summarize.queue.clear()
                        self.q_response.queue.clear()
                        action_more_info += '\n你生成的语法有问题，请检查你的格式是否正确。请考虑生成更合理的Action来完成原始的问题{instruction}'.format(
                            instruction=instruction)
                    # 捕获格式错误
                    except FormatException:
                        print("**********格式错误**********")
                        format_err += 1
                        print(format_err)
                        self.summarize.queue.clear()
                        self.q_response.queue.clear()
                        action_more_info += '\n你生成的语法有问题，请检查你的格式是否正确。请考虑生成更合理的Action来完成原始的问题{instruction}'.format(
                            instruction=instruction)
                    # 捕获其他错误
                    except Exception as error:
                        print("**********其他错误**********")
                        print(error)
                        self.summarize.queue.clear()
                        self.q_response.queue.clear()
                        format_err += 1
                # 函数返回，最终plan的结果
                return final_summarize

            else:
                print('No such mode, please check the mode in config.yaml.')
        else:
            print('Please specify the code execution mode.')
