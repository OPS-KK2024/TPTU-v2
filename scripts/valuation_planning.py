""" 用于评估测试llm的planning能力 """
# !/usr/bin/env python
# -*- coding: utf-8 -*-
from autotask.agent.onestep import OneStepAgent
from autotask.utils.plan_utils import get_tool_list
from langchain import SQLDatabase
import json
import os
from datetime import datetime
import yaml

YAML_PATH = os.path.join("./autotask", "config.yaml")


if __name__ == '__main__':

    # loading the config 
    with open(YAML_PATH, 'r', encoding='utf-8') as f:
        config = yaml.load(f.read(), Loader=yaml.FullLoader)
    
    # loading the database and QA from the config
    db = SQLDatabase.from_uri(config["database_path"])
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

    agent = OneStepAgent(config)

    for i in range(question_range[0], question_range[1]):
        print("第{}个问题".format(i))
        qad = qa_data['Q' + str(i)]
        preresult = "原始问题是" + " " + qad['question']
        print(preresult)
        instruction = qad['question']
        final_action = agent(instruction)
        final_action_arr.append(final_action)
        final_str = "第%s个问题" % i + "\n" + str(final_action) + "\n"
        f.write(final_str)

        # 比对答案是否正确
        # gt答案
        tool_answer = qad['tool_answer']
        # plan的tool结果
        plan_tool = get_tool_list(final_action)
        if tool_answer == plan_tool:
            true_answer.append(i)
    f.write('The index of the correct answer are: ')
    f.write(str(true_answer))
    f.write('The planning accuracy is {} / {}.'.format(len(true_answer), question_range[1]-question_range[0]))
    f.close()
    print()
    print('The index of the correct answer are: ')
    print(true_answer)
    print('The planning accuracy is {} / {}.'.format(len(true_answer), question_range[1]-question_range[0]))
    
