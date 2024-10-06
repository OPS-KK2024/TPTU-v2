""" 用于评估测试llm在业务场景中的planning能力 """
# !/usr/bin/env python
# -*- coding: utf-8 -*-
from autotask.agent.onestep_centurio import CenturioAgent
import json
import os
from datetime import datetime
import yaml

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
    log_name = "{}_{}_{}.txt".format(config["llm_name"], config["log_name"], datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
    save_path = os.path.join(save_path, log_name)
    f = open(save_path, "w", encoding="utf-8")
    # 评估正确答案的序号
    true_answer =[]
    question_range = config["question_range"]

    agent = CenturioAgent(config)

    for i in range(question_range[0], question_range[1]):
        print("第{}个问题".format(i))
        qad = qa_data['Q' + str(i)]
        preresult = "原始问题是" + " " + qad['question']
        print(preresult)
        instruction = qad['question']
        final_action = agent(instruction)
        final_action_arr.append(final_action)
        final_str = "第%s个问题：" % i + "\n" + qad['question'] + str(final_action) + "\n\n"
        f.write(final_str)

    f.close()

    
