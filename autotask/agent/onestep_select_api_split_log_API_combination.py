from autotask.prompt.prompt_select_api_split_API_combination import Prompt_Select
from autotask.llm.sensechat import SenseChat
from autotask.llm.sensenova import SenseNova
from autotask.llm.chatgpt import ChatGPT
from autotask.llm.ziya import Ziya
import queue
import re
import json
import time

from autotask.tool.get_weather import GetWeather
from autotask.tool.signal_control import SignalControl
from autotask.tool.ids import IDS
from autotask.tool.outlook import OutLook
from autotask.tool import get_weather
from autotask.tool import signal_control
from autotask.tool import ids
from autotask.utils.plan_exception import FormatException, ReturnFormat


class SelectAgent():
    def __init__(self, config: dict, q_response: [queue] = None, q_summarize: [queue] = None, q_ue: [queue] = None) -> None:
        self.config = config
        self.prompt = Prompt_Select()
        # 端到端评测
        self.q_response = q_response
        # 总结
        self.q_summarize = q_summarize
        # ue前段消息队列
        self.q_ue = q_ue

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

    def __call__(self, instruction: str, scence_num: str) -> str:

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
                # 组合prompt配置文件
                combination_prompt_cfg = json.load(open(self.config['combination_path'], encoding='utf-8'))

                while True:
                    retry += 1
                    if retry > self.config["max_retry_num"]:
                        err_str_01 = "api请求相应超时，请重新提问。"
                        err_str_02 = "summarize最终答案：\n" + "api请求相应超时，请重新提问。"
                        self.q_ue.put(err_str_01)
                        time.sleep(3)
                        self.q_ue.put(err_str_02)
                        break
                    try:
                        print("================================START================================")
                        # 初始化工具类
                        ids_func = IDS(self.q_response, self.q_summarize)
                        signalcontrol = SignalControl(self.q_response, self.q_summarize)
                        outlook = OutLook(self.q_response, self.q_summarize)
                        # 工具中包含的函数
                        signalcontrol_all = ['get_cycle', 'get_strength']
                        outlook_all = ['get_all_events', 'schedule_meeting', 'send_an_email', 'search_mail',
                                       'get_weather']
                        ids_all = ['get_coordinate', 'get_uuid', 'get_route_result', 'get_poi_search',
                                   'get_location_search', 'get_location_delete']
                        # 数组清空
                        ids.address_arr.clear()
                        ids.coordinate_all.clear()
                        ids.coordinate_test.clear()
                        ids.uuid_all.clear()
                        self.q_summarize.queue.clear()
                        self.q_response.queue.clear()
                        self.q_ue.queue.clear()
                        if len(scence_num) > 0:

                            # 场景编号
                            split_sence_result_arr = re.findall(r"\d+\.?\d*",str(scence_num))
                            # 场景组合
                            tool = ''
                            suffix = ''
                            # 相关prompt信息
                            for index in split_sence_result_arr:
                                combination = combination_prompt_cfg['Tool' + str(index)]
                                suffix = suffix + combination['prompt_suffix']
                                # 工具
                                tool = tool + str(combination['tool'][0]) + '\n'
                            combination_prompt = self.prompt.combination_prompt().format(suffix=suffix,tool=tool) + instruction
                            # 调用llm，返回执行结果
                            combination_result = self.action_llm(combination_prompt,stop=['\nstop'])
                            # 获得返回答案中的问题、伪代码列表
                            question_arr = []
                            code_arr = []
                            temp_code = ""
                            # 把返回的结果根据“换行”转换为列表
                            action_arr = list(combination_result.split("\n"))
                            # 判断列表中，含有question则为拆分的子问题，含有=则为代码，其他均为无效信息
                            for strt in action_arr:
                                if "question" in strt:
                                    question_arr.append(strt)
                                    code_arr.append(temp_code.strip())
                                    temp_code = ""
                                elif "=" in strt:
                                    if "answer" in strt:
                                        code = strt[strt.find("answer") + 10:]
                                    else:
                                        code = strt
                                    temp_code = temp_code + code + "\n"
                                    # code_arr.append(code.strip())
                                # 不相关场景
                                elif 'null' in strt:
                                    temp_code = strt[strt.find("answer") + 10:]
                            code_arr.append(temp_code.strip())
                            del code_arr[0]
                            print("-------------------------------拆分结果-------------------------------")
                            # llm思考的过程
                            # str_process = "\n原始问题为：" + instruction + "\n"
                            # print("\n原始问题为：" + instruction + "\n")
                            str_process = ""
                            if len(question_arr)>0:
                                for i in range(0, len(question_arr)):
                                    # print(question_arr[i])
                                    str_process = str_process + str(question_arr[i]) + "\n"
                                    code_str = code_arr[i]
                                    # 相关场景
                                    if 'null' not in code_str:
                                        # 交通相关
                                        for func in signalcontrol_all:
                                            if func in code_str:
                                                code_str = code_str.replace(func, "signalcontrol." + func)
                                        # 个人助手相关
                                        for func in outlook_all:
                                            if func in code_str:
                                                code_str = code_str.replace(func, "outlook." + func)
                                        # 路径规划相关
                                        for func in ids_all:
                                            if func in code_str:
                                                code_str = code_str.replace(func, "ids_func." + func)
                                        # print("该步骤的伪代码：")
                                        str_process = str_process + "该步骤的伪代码：\n" + code_str + "\n"
                                        # print(code_str)
                                        exec(code_str)
                                        llm_answer = []
                                        llm_summarize = []
                                        code_all = 0
                                        # 伪代码行数
                                        if 'signalcontrol.' in code_str:
                                            code_all = code_str.count('signalcontrol.')
                                        elif 'outlook.' in code_str:
                                            code_all = code_str.count('outlook.')
                                        elif 'ids_func.' in code_str:
                                            code_all = code_str.count('ids_func.')
                                        for n in range(code_all):
                                            index = len(self.q_response.queue) - (code_all - n)
                                            llm_answer.append(self.q_response.queue[index])
                                            # 总结所需答案
                                            llm_summarize.append(self.q_summarize.queue[index])
                                        str_process = str_process + "该步骤的答案：\n" + str(llm_summarize) + "\n\n"
                                        # print("该步骤的答案：")
                                        # print(llm_summarize, "\n")

                                    # 不相关场景
                                    else:
                                        null_prompt = self.prompt.null_prompt().format(question=question_arr[i])
                                        # 调用llm，返回执行结果
                                        actions_null = self.action_llm(null_prompt, stop=['\nstop'])
                                        self.q_summarize.put(actions_null)
                                        self.q_response.put('null')
                                        print("该步骤的答案：")
                                        str_process = str_process + actions_null + "\n"
                                        #print(actions_null)
                            else:
                                null_prompt = self.prompt.null_prompt().format(question=instruction)
                                # 调用llm，返回执行结果
                                actions_null = self.action_llm(null_prompt, stop=['\nstop'])
                                self.q_summarize.put(actions_null)
                                self.q_response.put('null')
                                print("该步骤的答案：")
                                str_process = str_process + actions_null + "\n"
                                # print(actions_null)
                            str_process = "原始问题为：" + instruction + "\n\n" + str_process
                            print(str_process)
                            # 把思考的过程放入队列传回UE
                            self.q_ue.put(str_process)
                            # 总结
                            print("-------------------------------结果总结-------------------------------")
                            # 最终整理后的答案
                            str_final = ""
                            action_final = self.prompt.summarize_prompt().format(question=instruction, answer=list(self.q_summarize.queue))
                            # 调用llm，返回执行结果
                            final_summarize = self.action_llm(action_final, stop=['\nstop'])
                            str_final = "summarize最终答案：\n" + final_summarize
                            # print("最终答案：")
                            # print(final_summarize, "\n")
                            print(str_final)
                            self.q_ue.put(str_final)
                            break
                        else:
                            print("-------------------------------拆分结果-------------------------------")
                            null_prompt = self.prompt.null_prompt().format(question=instruction)
                            # 调用llm，返回执行结果
                            actions_null = self.action_llm(null_prompt, stop=['\nstop'])
                            self.q_summarize.put(actions_null)
                            self.q_response.put('null')
                            print("该步骤的答案：")
                            str_process = actions_null + "\n"
                            print(actions_null)
                            str_process = "原始问题为：" + instruction + "\n\n" + str_process
                            print(str_process)
                            # 把思考的过程放入队列传回UE
                            self.q_ue.put(str_process)
                            print("-------------------------------结果总结-------------------------------")
                            # 最终整理后的答案
                            str_final = ""
                            action_final = self.prompt.summarize_prompt().format(question=instruction,
                                                                                 answer=list(self.q_summarize.queue))
                            # 调用llm，返回执行结果
                            final_summarize = self.action_llm(action_final, stop=['\nstop'])
                            str_final = "summarize最终答案：\n" + final_summarize
                            # print("最终答案：")
                            # print(final_summarize, "\n")
                            print(str_final)
                            self.q_ue.put(str_final)
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
                        format_err += 1
                # 函数返回，最终plan的结果
                return final_summarize

            else:
                print('No such mode, please check the mode in config.yaml.')
        else:
            print('Please specify the code execution mode.')
