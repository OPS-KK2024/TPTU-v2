""" 用于评估测试llm在业务场景中的planning能力 """
# !/usr/bin/env python
# -*- coding: utf-8 -*-
from autotask.agent.onestep_centurio_API_retriever import CenturioAPIOneStepAgent
import yaml
import os
from autotask.utils.prompt_utils_API_retriever import get_agent_kwargs, APIWRAPPER
import json
from datetime import datetime
import numpy
# 2K
YAML_PATH = os.path.join("./autotask", "config_API_retriever.yaml")
# 8K
# YAML_PATH = os.path.join("./autotask", "config_8k.yaml")
# gpt
# YAML_PATH = os.path.join("./autotask", "config_gpt.yaml")

if __name__ == '__main__':

    # loading the config 
    with open(YAML_PATH, 'r', encoding='utf-8') as f:
        config = yaml.load(f.read(), Loader=yaml.FullLoader)
    
    # 加载测试问题
    qa_data = json.load(open(config['QA_path'], encoding='utf-8'))
    # 保存测试用的全部action
    final_action_arr = []    
    # 结果保存的路径
    save_path = config["save_path"]
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    log_name = "{}_{}_{}_2k_6.json".format(config["llm_name"], config["log_name"], datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
    save_path = os.path.join('G:/autotask_planning/log/0927/', log_name)
    f = open(save_path, "w", encoding="utf-8")
    # 评估正确答案的序号
    true_answer =[]
    question_range = config["question_range"]

    demos_data, demos_inds = None, None
    # agent_type
    if config['agent_type'] == 'centurio_api_onestep':
        agent = CenturioAPIOneStepAgent(config)
    else:
        print(
            'No such agent type {}, please check the agent_type in config_API_retriever.yaml file.'.format(
                config["agent_type"]))
        exit()
    # API_retriever
    api_wrapper = APIWRAPPER(config)
    for j in range(1):
        true_value_num = 0
        final_str = ''
        anno_all = {}
        anno_01 = []
        num_all = 0
        for i in range(1, 31):
            num_all = num_all + 1
            answer_final = []
            anno = {}
            anno["Q" + str(i)] = {}
            print("第{}个问题".format(i))
            qad = qa_data['Q' + str(i)]
            preresult = "原始问题是" + " " + qad['question']
            print(preresult)
            instruction = qad['question']
            anno_qu = {}
            anno_qu['question'] = qad['question']
            agent_kwargs = get_agent_kwargs(qad=anno_qu, data=demos_data, config=config, api_wrapper=api_wrapper,
                                            is_aicl=False)
            final_action = agent(**agent_kwargs)
            # final_action = agent(instruction, function, prompt_suffix)
            # -----------真值判断-----------
            answer = qad['gt_plan_answer']
            anno["Q" + str(i)]["question"] = instruction
            anno["Q" + str(i)]["gt_plan_API"] = answer
            # if final_action.split('||')[0] != '':
            llm_answer = final_action
            # else:
            #     final_action = "|| "
            #     llm_answer = ''
            if len(answer) <= len(llm_answer):
                for llm_data in llm_answer:
                    if llm_data in answer:
                        answer_final.append(llm_data)
                if answer == answer_final:
                    true_value = True
                    true_value_num = true_value_num + 1
                else:
                    true_value = False
            # if answer == llm_answer:
            #     true_value = True
            #     true_value_num = true_value_num + 1
            else:
                true_value = False
            anno["Q" + str(i)]["return_plan_text"] = str(final_action)
            anno["Q" + str(i)]["return_plan_API"] = llm_answer
            anno["Q" + str(i)]["true_vlaue"] = true_value
            anno_01.append(anno)
            # ---------------------------------------
            final_action_arr.append(final_action)
            # final_str = "第%s个问题：" % i + "\n" + qad['question'] + "\n"+ "gt_plan_answer:"+ str(answer) + "\n" \
            #             + str(final_action.split('||')[1]) + "\n"+ str(final_action.split('||')[0]) + "\n\n" + "结果" + str(true_value) + "\n\n"
        anno_all["qa_list"] = anno_01
        anno_all["accuracy"] = str(true_value_num)+"/"+str(len(qa_data))
        # f.write(final_str + "\n正确率" + str(true_value_num)+"/"+str(len(question_range)))
        f.write(json.dumps(anno_all, ensure_ascii=False, indent=4) + "\n")

    f.close()

    
