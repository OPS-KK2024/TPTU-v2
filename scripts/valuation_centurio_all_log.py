""" 用于评估测试llm在业务场景中的planning能力 [全量-log]"""
# !/usr/bin/env python
# -*- coding: utf-8 -*-
from autotask.agent.onestep_centurio_all import CenturioAgent
import json
import os
from datetime import datetime
import yaml

# 8k
YAML_PATH = os.path.join("./autotask", "config_8k.yaml")
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
    log_name = "{}_{}_{}_all_8k.json".format(config["llm_name"], config["log_name"], datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
    save_path = os.path.join(save_path, log_name)
    f = open(save_path, "w", encoding="utf-8")
    # 评估正确答案的序号
    true_answer =[]
    question_range = config["question_range"]



    agent = CenturioAgent(config)
    for j in range(1):
        final_str = ''
        true_value_num = 0
        anno_all = {}
        anno_01 = []
        for i in range(question_range[0], question_range[1]):
            print("第{}个问题".format(i))
            qad = qa_data['Q' + str(i)]
            preresult = "原始问题是" + " " + qad['question']
            # preresult = "原始问题是"
            print(preresult)
            instruction = qad['question']
            final_action = agent(instruction)

            # -----------真值判断-----------
            anno = {}
            anno["Q" + str(i)] = {}
            answer_final = []
            answer = qad['gt_plan_answer']
            anno["Q" + str(i)]["question"] = instruction
            anno["Q" + str(i)]["gt_plan_API"] = answer
            # final_action = agent(instruction)
            print(final_action)
            llm_answer = final_action.split('||')[0].split('["')[1].split('"]')[0].split('", "')
            # if len(answer) <= len(llm_answer):
            #     for llm_data in llm_answer:
            #         if llm_data in answer:
            #             answer_final.append(llm_data)
            #     print("answer", answer_final)
            #     if answer == answer_final:
            #         true_value = True
            #         true_value_num = true_value_num +1
            #     else:
            #         true_value = False
            # else:
            #     true_value = False
            if answer == llm_answer:
                true_value = True
                true_value_num = true_value_num + 1
            else:
                true_value = False
            # anno["Q" + str(i)]["return_plan_text"] = str(final_action.split('||')[1])
            anno["Q" + str(i)]["return_plan_API"] = llm_answer
            anno["Q" + str(i)]["true_vlaue"] = true_value
            print()
            anno_01.append(anno)
            # ---------------------------------------
            final_action_arr.append(final_action)
            final_str = "第%s个问题：" % i + "\n" + qad['question'] + "\n" + "gt_plan_answer:" + str(answer) + "\n" \
                        + str(final_action.split('||')[1]) + "\n" + str(
                final_action.split('||')[0]) + "\n\n" + "结果" + str(true_value) + "\n\n"
        anno_all["qa_list"] = anno_01
        anno_all["accuracy"] = str(true_value_num) + "/" + str(len(qa_data))
        f.write(json.dumps(anno_all, ensure_ascii=False, indent=4) + "\n")

    f.close()

    
