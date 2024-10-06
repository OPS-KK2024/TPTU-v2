""" 用于评估测试llm的planning能力 """
# !/usr/bin/env python
# -*- coding: utf-8 -*-
from autotask.agent.onestep_centurio_API_retriever import CenturioAPIOneStepAgent
import json
import os
import yaml
from autotask.utils.eval_utils_API_retriever import write_json, mkpath, evaluate, unix_path_join
from autotask.utils.prompt_utils_API_retriever import get_save_name, get_agent_kwargs, APIWRAPPER

# 配置文件
YAML_PATH = os.path.join("./autotask", "config_API_retriever.yaml")
with open(YAML_PATH, 'r', encoding='utf-8') as f:
    config = yaml.load(f.read(), Loader=yaml.FullLoader)

def valuation_planning():
    # 推理
    infer = True
    # 评测
    eval = True
    # 结果保存的路径
    save_name, now = get_save_name(config)

    save_path = config["save_path"]
    mkpath(save_path)
    log_name = f"{save_name}.log"
    save_path = unix_path_join(save_path, log_name)
    f = open(save_path, "w", encoding="utf-8")

    # 推理
    if infer:
        pred_path = config["pred_path"]
        mkpath(pred_path)
        pred_name = f"{save_name}_pred.json"
        pred_path = unix_path_join(pred_path, pred_name)
        # loading the database and QA from the config
        qa_data = json.load(open(config['QA_path'], encoding='utf-8'))
        # loading demonstration data for adaptive ICL
        demos_data, demos_inds = None, None
        # 保存测试生成的全部action(jason格式)
        pred_res_all = {}
        if config['agent_type'] == 'centurio_api_onestep':
            agent = CenturioAPIOneStepAgent(config)
        else:
            print(
                'No such agent type {}, please check the agent_type in config_API_retriever.yaml file.'.format(config["agent_type"]))
            exit()
        api_wrapper = APIWRAPPER(config)

        for i in range(1, 31):
            print("第{}个问题".format(i))
            if ('Q' + str(i)) not in qa_data:
                fail_str = f"Failed to get question (question id: {i}).\n"
                f.write(fail_str)
                print(fail_str)
                continue
            qad = qa_data['Q' + str(i)]
            preresult = "原始问题是" + " " + qad['question']
            anno = {}
            anno['question'] = qad['question']
            print(preresult)
            agent_kwargs = get_agent_kwargs(qad=anno, data=demos_data, config=config, api_wrapper=api_wrapper,
                                            is_aicl=False)
            final_action = agent(**agent_kwargs)
            if not final_action:
                fail_str = f"Failed to get predicted result (question id: {i}).\n"
                f.write(fail_str)
                print(fail_str)
                continue
            pred_res = {
                'question': qad['question'],
                'pred': final_action,
            }
            if config['auto_prompt_kwargs']['evaluation']['add_retrieval']:
                pred_res['relevant_docs'] = agent_kwargs['relevant_docs']
            pred_res_all['Q' + str(i)] = pred_res
            final_str = "第%s个问题" % i + "\n" + str(final_action) + "\n"
            f.write(final_str)
        write_json(pred_res_all, pred_path, json_type='all', mode='w')
    # 评测
    if eval:
        # name = f"{config['llm_name']}"
        # pred_path = unix_path_join(config['save_path'], name)
        pred_path = config["pred_path"]
        print(pred_path)
        assert os.path.isdir(pred_path)
        pred_paths = [unix_path_join(pred_path, p) for p in os.listdir(pred_path) if p.endswith('_pred.json')]
        # assert len(pred_paths) == 1, f'got len(pred_paths): {len(pred_paths)}, expected 1'
        pred_path = pred_paths[0]

        eval_res_all, eval_paths = evaluate(pred_json_path=pred_path, gt_json_path=config['QA_path'], config=config)
        eval_str = f"\nThe planning accuracy is {eval_res_all['exact']} / {eval_res_all['gt_num']} = {eval_res_all['acc']}." + \
                   f"\nThe planning precison is {eval_res_all['exact']} / {eval_res_all['count']} = {eval_res_all['precison']}." + \
                   f"\nThe planning recall is {eval_res_all['count']} / {eval_res_all['gt_num']} = {eval_res_all['recall']}." + \
                   "\nFor detail information, please refer to {}.".format('\n'.join(eval_paths))
        f.write(eval_str)
        print(eval_str)

    f.close()


if __name__ == '__main__':
    valuation_planning()

