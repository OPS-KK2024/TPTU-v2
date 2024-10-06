""" 用于评估测试llm在业务场景中的planning能力 [相关API场景]"""
# !/usr/bin/env python
# -*- coding: utf-8 -*-
from autotask.agent.onestep_select_api_split_log_API import SelectAgent
import json
import os
from datetime import datetime
import yaml
import queue
import re

YAML_PATH = os.path.join("./autotask", "config.yaml")


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
    # summarize所需答案
    summarize = queue.Queue()
    # 真值判断所需答案
    q_response = queue.Queue()
    agent = SelectAgent(config, q_response, summarize)
    for i in range(3,4):
        save_path = config["save_path"]
        log_name = "{}_API_2k_{}_{}_all_true_value_02.json".format(config["llm_name"], str(i), datetime.now().strftime('%m%d%H%M'))
        save_path = os.path.join(save_path, log_name)
        f = open(save_path, "w", encoding="utf-8")
        # 回答正确的数量
        true_value_num = 0
        final_str = ''
        anno_all = {}
        anno_01 = []
        num_all = 0
        for j in range(10):
            print("第{}个问题".format(i))
            q_response.queue.clear()
            summarize.queue.clear()
            qad = qa_data['Q' + str(i)]
            instruction = qad['question']
            print("原始问题是 " + instruction)
            # 获得end2end的结果
            final_action = agent(instruction)

            # -----------真值判断-----------
            anno = {}
            anno["Q" + str(i)] = {}
            answer = qad['gt_plan_answer']
            anno["Q" + str(i)]["question"] = instruction
            anno["Q" + str(i)]["gt_plan_answer"] = qad['gt_plan_answer']
            llm_answer = []
            for n in range(len(q_response.queue)):
                llm_answer.append(q_response.queue[n])
            # 判断正确率
            if set(llm_answer) >= set(answer):
                true_value = True
                true_value_num = true_value_num + 1
            else:
                true_value = False
            anno["Q" + str(i)]["return_plan_answer"] = llm_answer
            anno["Q" + str(i)]["summarize_input_answer"] = list(summarize.queue)
            anno["Q" + str(i)]["summarize_output_text"] = final_action
            anno["Q" + str(i)]["true_vlaue"] = true_value
            anno_01.append(anno)
            # ---------------------------------------
        anno_all["qa_list"] = anno_01
        anno_all["accuracy"] = str(true_value_num) + "/" + str(10)
        f.write(json.dumps(anno_all, ensure_ascii=False, indent=4) + "\n")
        f.close()

    
