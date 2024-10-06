""" 用于评估测试llm在业务场景中的planning能力 [知识库]"""
# !/usr/bin/env python
# -*- coding: utf-8 -*-
from autotask.agent.onestep_centurio_knowledge_top3 import CenturioAgent
import json
import os
from datetime import datetime
import yaml
from sentence_transformers import SentenceTransformer, util

YAML_PATH = os.path.join("./autotask", "config_knowledge.yaml")

# 知识库，计算示例问题embeddings
top_k = 3
model = SentenceTransformer('moka-ai/m3e-base')
with open(YAML_PATH, 'r', encoding='utf-8') as f:
    config = yaml.load(f.read(), Loader=yaml.FullLoader)
example = config["knowledge_path"]
sentences2 = []
answer_all = []
data_example = open(example, "r", encoding="utf-8")
example_all = json.load(data_example)["qa_lst"]
for data in example_all:
    sentences2.append(data["example"])
    answer_all.append(data["answer"])
# 计算列表的嵌入
embeddings2 = model.encode(sentences2, convert_to_tensor=True)
# ---------知识库----------

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
    for j in range(1):
        for i in range(question_range[0], question_range[1]):
            print("第{}个问题".format(i))
            qad = qa_data['Q' + str(i)]
            preresult = "原始问题是" + " " + qad['question']
            print(preresult)
            instruction = qad['question']
            # ----------知识库----------
            embeddings1 = model.encode(instruction, convert_to_tensor=True)
            cosine_scores = util.cos_sim(embeddings1, embeddings2)
            # 判断所给问题与示例问题的相似度
            scores_all = []
            scores_final = []
            # top-3示例问题
            examples = []
            examples_test = []
            answers = []
            for j in range(len(answer_all)):
                scores_all.append(cosine_scores[0][j].item())
                scores_final.append(cosine_scores[0][j].item())
            scores_all.sort(reverse=True)
            print(scores_all[0])
            # 获取top1的示例问题
            for n in range(top_k):
                index = scores_final.index(scores_all[n])
                example = sentences2[index]  # 示例问题
                answer = str(answer_all[index]).replace("'", '"')  # 示例问题对应答案
                answers.append(answer)
                examples_test.append(example)
                examples.append("语句" + str(n + 1) + ':' + example)
            statement = '\n'.join(examples)
            answer = agent(instruction, statement, '|'.join(examples_test), '|'.join(answers))
            final_action = answer
            final_action_arr.append(final_action)
            final_str = "第%s个问题：" % i + "\n" + qad['question'] + str(final_action) + "\n\n"
            f.write(final_str)

    f.close()

    
