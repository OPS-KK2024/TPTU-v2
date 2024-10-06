from typing import Any, List, Mapping, Optional
import time
import warnings
warnings.filterwarnings("ignore")
import json
import re
# import math
import logging
import json
import datetime
import os
from copy import deepcopy
from tqdm import tqdm
from collections import defaultdict
from sentence_transformers import SentenceTransformer, util
# import pandas as pd
import numpy as np
# import matplotlib
from pathlib import Path
import re


""" common utils for eval or other purpose """

def unix_path_join(*paths):
    return (os.path.join(*paths)).replace('\\', '/')

def abs_path_join(*paths):
    return os.path.abspath(os.path.join(*paths))


def load_json(json_file, json_type='all'):
    metas = []
    if json_type == 'all':
        with open(json_file, 'r', encoding='utf-8') as f:
            metas = json.load(f)
    elif json_type == 'line':
        with open(json_file, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                meta = json.loads(line.strip())
                metas.append(meta)
    return metas


def write_json(data, path, json_type='all', mode='w'):
    dirname = os.path.dirname(path)
    os.makedirs(dirname, exist_ok=True)
    if json_type == 'all':
        with open(path, mode=mode, encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        with open(path, mode=mode, encoding='utf-8') as f:
            for x in data:
                f.write(json.dumps(x, ensure_ascii=False) + '\n')


def print_now(return_flag=False):
    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    now = datetime.datetime.now(JST)
    now = now.strftime('%Y/%m/%d %H:%M:%S')
    if not return_flag:
        print(now)
        return
    return now


def mkpath(path):
    if not os.path.exists(path):
        os.makedirs(path)


def get_logger(log_file=None):
    if not log_file:
        now = print_now(True).split(' ')[0].replace('/', '-')
        Log_Folder = f'log/temp'
        mkpath(f'{Log_Folder}')
        log_file = f'{Log_Folder}/log_{now}.log'
    # logging.basicConfig(filename=log_file)
    formatter = logging.Formatter('%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    sh = logging.StreamHandler()
    fh = logging.FileHandler(filename=log_file)
    fh.setFormatter(formatter)
    sh.setFormatter(formatter)
    logger = logging.getLogger()
    if not logger.handlers:
        logger.addHandler(fh)
        logger.addHandler(sh)
    logger.setLevel(level=logging.INFO)
    return logger


def clear_logger_handlers(logger):
    if logger:
        while logger.handlers:
            logger.handlers.clear()
    return logger


def check_tasks_format(tasks):
    tasks = eval(tasks)
    assert isinstance(tasks, list) and len(tasks) > 0
    assert all(isinstance(x, dict) for x in tasks)
    assert all(list(x.keys())[0] in ('SQL生成器', 'Python生成器') for x in tasks)
    return tasks


""" Embeddings Similarity """

def emb_similarity(query, compares, top_k=1, model_name_or_path='all-mpnet-base-v2'):
    assert isinstance(compares, list)
    # Load embedding model
    # model_name_or_path: ('all-mpnet-base-v2', 'all-MiniLM-L6-v2')
    model = SentenceTransformer(model_name_or_path)
    comp_embeddings = model.encode(compares, normalize_embeddings=True)
    query_embeddings = model.encode([query], normalize_embeddings=True)
    similarity_matrix = util.pytorch_cos_sim(query_embeddings, comp_embeddings)
    top_scores, top_inds = similarity_matrix.topk(k=top_k, dim=-1)
    top_scores, top_inds = top_scores.squeeze(0).tolist(), top_inds.squeeze(0).tolist()
    return [compares[i] for i in top_inds], top_inds, top_scores


""" Evaluator Definition"""

class EmbSimEvaluator(object):
    """A simple evaluator"""
    def __init__(self, logger=None, tools=("SQL生成器", "PythonREPL"), sim_thresh=0.9, verbose=True):
        """init"""
        self.logger = logger if logger else get_logger()
        self.built_ins = tools
        self.sim_thresh = sim_thresh
        self.verbose = verbose
    
    def get_scores(self, match_cnt, gt_cnt, pred_cnt):
        if pred_cnt != gt_cnt:
            return 0
        elif match_cnt == gt_cnt:
            return 1
        return 0
    
    def eval_check(self, pred, gt):
        def dfs_cvt_all(target, seen):
            if not target:
                return 0, [], []
            if isinstance(target[0], list):
                cur_cnt, cur_k, cur_v = dfs_cvt_all(target[0], seen)
            else:
                cur_cnt, cur_k, cur_v = 1, list(target[0].keys())[0], list(target[0].values())[0]
                seen[cur_v] = cur_k
            cnt, k, v = dfs_cvt_all(target[1:], seen)
            return cur_cnt + cnt, [cur_k] + k, [cur_v] + v
        
        def dfs_cnt(target):
            if not target:
                return 0
            return (dfs_cnt(target[0]) if isinstance(target[0], list) else 1) + dfs_cnt(target[1:])
        
        def dfs_check(target):
            if not target:
                return True
            if isinstance(target[0], list):
                if not dfs_check(target[0]):
                    return False
            else:
                if not (isinstance(target[0], (dict, )) \
                    and isinstance(list(target[0].values())[0], (str, )) \
                        and list(target[0].keys())[0] in self.built_ins):
                    return False
            return dfs_check(target[1:])
        
        assert isinstance(pred, list), f"invalid pred: {pred}"
        assert dfs_check(gt), f"invalid gt: {gt}"
        gt_map = {}
        gt_cnt, gt_tools, gt_querys = dfs_cvt_all(gt, gt_map)
        pred_map = {}
        pred_cnt, pred_tools, pred_querys = dfs_cvt_all(pred, pred_map)
        # # TODO
        # assert pred_cnt >= gt_cnt, f"pred_cnt: {pred_cnt} and gt_cnt: {gt_cnt}"
        return gt_cnt, gt_tools, gt_querys, gt_map, pred_cnt, pred_tools, pred_querys, pred_map
        
    def eval_exact_match(self, pred, gt):
        self.logger.info(f"*******************Start Eval*******************")
        gt_cnt, gt_tools, gt_querys, gt_map, pred_cnt, pred_tools, pred_querys, pred_map = self.eval_check(pred, gt)
        
        mismatch_info = {
            'tool_error': 0, 
            'query_error': 0, 
            'task_len_error': 0, 
        }
        
        # TODO
        # if pred_cnt < gt_cnt:
        if pred_cnt != gt_cnt:
            mismatch_info['task_len_error'] += 1
            score = 0
            res_info = {
                'match_cnt': None, 
                'gt_cnt': gt_cnt, 
                'pred_cnt': pred_cnt, 
                'score': score, 
                'mismatch_info': mismatch_info, 
                'gt_querys': gt_querys, 
                'pred_querys': pred_querys, 
                'gt_tools': gt_tools, 
                'pred_tools': pred_tools, 
            }
            self.logger.info(f"*******************End Eval*******************")
            if self.verbose:
                self.logger.info(f"*******************res_info: {res_info}*******************")
            return res_info, score
        
        def match_func(query, compares, mismatch_info):
            comp = compares.pop(0)
            if gt_map[query] != pred_map[comp]:
                if self.verbose:
                    self.logger.info(f"*******************tool_error*******************")
                    self.logger.info(f"*******************query {query}*******************")
                    self.logger.info(f"*******************comp {comp}*******************")
                    self.logger.info(f"*******************gt_map[query] {gt_map[query]}*******************")
                    self.logger.info(f"*******************pred_map[comp] {pred_map[comp]}*******************")
                mismatch_info['tool_error'] += 1
                return 0
            top_compares, top_inds, top_scores = emb_similarity(query, [comp]+compares, top_k=1, model_name_or_path='all-mpnet-base-v2')
            # TODO: take top_scores into consideration?how to set thresh?
            # if not (comp == top_compares[0]):
            if not (comp == top_compares[0] and top_scores[0] >= self.sim_thresh):
                if self.verbose:
                    self.logger.info(f"*******************query_error*******************")
                    self.logger.info(f"*******************query {query}*******************")
                    self.logger.info(f"*******************comp {comp}*******************")
                    self.logger.info(f"*******************top_compares[0] {top_compares[0]}*******************")
                    self.logger.info(f"*******************top_scores[0] {top_scores[0]}*******************")
                mismatch_info['query_error'] += 1
                return 0
            return 1
        
        def dfs_match_cnt(pred, gt, mismatch_info):
            if not gt:
                return 0
            return (dfs_match_cnt(pred, gt[0], mismatch_info) if isinstance(gt[0], list) else match_func(gt[0], pred, mismatch_info)) + dfs_match_cnt(pred, gt[1:], mismatch_info)
        
        match_cnt = dfs_match_cnt(deepcopy(pred_querys), deepcopy(gt_querys), mismatch_info)
        score = self.get_scores(match_cnt, gt_cnt, pred_cnt)
        res_info = {
            'match_cnt': match_cnt, 
            'gt_cnt': gt_cnt, 
            'pred_cnt': pred_cnt, 
            'score': score, 
            'mismatch_info': mismatch_info, 
            'gt_querys': gt_querys, 
            'pred_querys': pred_querys, 
            'gt_tools': gt_tools, 
            'pred_tools': pred_tools, 
        }
        
        self.logger.info(f"*******************End Eval*******************")
        if self.verbose:
            self.logger.info(f"*******************res_info: {res_info}*******************")
        return res_info, score


class APIEmbSimEvaluator(EmbSimEvaluator):
    """A simple evaluator"""
    def __init__(self, logger=None, tools=("SQL生成器", "PythonREPL"), sim_thresh=0.9, verbose=True, delimiter="=", new_temp_name="new_val"):
        """init"""
        super(APIEmbSimEvaluator, self).__init__(logger=logger, tools=tools, sim_thresh=sim_thresh, verbose=verbose)
        self.delimiter = delimiter
        self.new_temp_name = new_temp_name
    
    @staticmethod
    def parse_query(query, delimiter):
        idx = None
        if query.find(delimiter) >= 0:
            idx = query.find(delimiter)
        return query[:idx].strip(), query[idx + 1:].strip()
    
    def eval_preprocess_api(self, tools, querys, delimiter="=", new_temp_name="new_val"):
        assert len(tools) == len(querys)
        # split
        temps, apis = list(zip(*[self.parse_query(query, delimiter) for query in querys]))
        temps, apis = list(temps), list(apis)
        
        # sort
        sorted_inds = np.array(apis).argsort()
        sorted_apis = [apis[i] for i in sorted_inds]
        sorted_temps = [temps[i] for i in sorted_inds]
        sorted_tools = [tools[i] for i in sorted_inds]
        # raw ix --> sorted idx
        temps_map = dict(zip(sorted_temps, [f"{new_temp_name}{i + 1}" for i in range(len(sorted_inds))]))

        # replace temp
        out_apis = []
        out_temps = []
        for i in range(len(sorted_inds)):
            cur_api = sorted_apis[i]
            cur_temp = f"{new_temp_name}{i + 1}"
            for t in temps_map:
                if t in cur_api:
                    cur_api = cur_api.replace(t, temps_map[t])
            out_apis.append(cur_api)
            out_temps.append(cur_temp)
        
        # merge
        out_querys = []
        for t, a in zip(out_temps, out_apis):
            out_querys.append(f"{t} = {a}")
        return sorted_tools, out_querys, dict(zip(out_querys, sorted_tools))
    
    def eval_check(self, pred, gt):
        def dfs_cvt_all(target, seen):
            if not target:
                return 0, [], []
            if isinstance(target[0], list):
                cur_cnt, cur_k, cur_v = dfs_cvt_all(target[0], seen)
            else:
                cur_cnt, cur_k, cur_v = 1, list(target[0].keys())[0], list(target[0].values())[0]
                seen[cur_v] = cur_k
            cnt, k, v = dfs_cvt_all(target[1:], seen)
            return cur_cnt + cnt, [cur_k] + k, [cur_v] + v
        
        def dfs_cnt(target):
            if not target:
                return 0
            return (dfs_cnt(target[0]) if isinstance(target[0], list) else 1) + dfs_cnt(target[1:])
        
        def dfs_check(target):
            if not target:
                return True
            if isinstance(target[0], list):
                if not dfs_check(target[0]):
                    return False
            else:
                if not (isinstance(target[0], (dict, )) \
                    and isinstance(list(target[0].values())[0], (str, )) \
                        and list(target[0].keys())[0] in self.built_ins):
                    return False
            return dfs_check(target[1:])
        
        assert isinstance(gt, list) and dfs_check(gt), f"invalid gt: {gt}"
        assert isinstance(pred, list) and dfs_check(pred), f"invalid pred: {pred}"
        gt_map = {}
        gt_cnt, gt_tools, gt_querys = dfs_cvt_all(gt, gt_map)
        pred_map = {}
        pred_cnt, pred_tools, pred_querys = dfs_cvt_all(pred, pred_map)
        # preprocess for api calls
        gt_tools, gt_querys, gt_map = self.eval_preprocess_api(gt_tools, gt_querys, delimiter=self.delimiter, new_temp_name=self.new_temp_name)
        pred_tools, pred_querys, pred_map = self.eval_preprocess_api(pred_tools, pred_querys, delimiter=self.delimiter, new_temp_name=self.new_temp_name)
        return gt_cnt, gt_tools, gt_querys, gt_map, pred_cnt, pred_tools, pred_querys, pred_map



class CenturioAPIEvaluator(object):
    """A simple evaluator"""
    def __init__(self, logger=None, tools=("SQL生成器", "PythonREPL"), sim_thresh=0.9, verbose=True):
        """init"""
        self.logger = logger if logger else get_logger()
        self.built_ins = tools
        self.sim_thresh = sim_thresh
        self.verbose = verbose
    
    def eval_check(self, pred, gt):
        if pred.split('||')[0] != '':
            # llm_pred = pred.split('||')[0].split('["')[1].split('"]')[0].split('", "')
            # llm_pred = [_.strip("'").strip('"') for _ in pred.split('||')[0].split('[')[1].split(']')[0].split(', ') if _.strip()]
            llm_pred = [_.strip().strip("'").strip('"').strip() for _ in pred.split('||')[0].split('[')[1].split(']')[0].split(',') if _.strip()]
            # llm_pred = [re.sub(re.compile(r"\d+\."), '', _, count=1) for _ in llm_pred]
        else:
            pred = "|| "
            llm_pred = []
        
        if isinstance(gt, dict):
            # gt, order = gt['gt'], gt['order']
            raw_gt = gt
            gt, order, multi_solution = raw_gt['gt'], (raw_gt['order'] if 'order' in raw_gt else True), (raw_gt['multi_solution'] if 'multi_solution' in raw_gt else False)
            gt_list = raw_gt['gt_list'] if multi_solution else [gt]
        else:
            order = True
            multi_solution = False
            gt_list = [gt]
        
        # assert isinstance(gt, list), f"invalid gt: {gt}"
        assert all(isinstance(_, list) for _ in gt_list), f"invalid gt_list: {gt_list}"
        assert isinstance(llm_pred, list), f"invalid llm_pred: {llm_pred}"
        
        # gt_cnt = len(gt)
        gt_cnt = [len(_) for _ in gt_list]
        pred_cnt = len(llm_pred)
        
        return gt_cnt, gt_list, order, multi_solution, pred_cnt, llm_pred, pred
    
    def eval_exact_match(self, pred, gt):
        self.logger.info(f"*******************Start Multi Solution*******************")
        gt_cnt, gt_list, order, multi_solution, pred_cnt, llm_pred, pred = self.eval_check(pred, gt)
        assert len(gt_list) > 0, f"empty gt_list: {gt_list}"
        
        res_info, score = None, 0
        if multi_solution:
            for i in range(len(gt_list)):
                res_info, score = self.eval_exact_match_single(gt_cnt[i], gt_list[i], order, pred_cnt, llm_pred, pred)
                if score == 1:
                    break
        else:
            res_info, score = self.eval_exact_match_single(gt_cnt[0], gt_list[0], order, pred_cnt, llm_pred, pred)
        
        return res_info, score
    
    # def eval_exact_match(self, pred, gt):
    def eval_exact_match_single(self, gt_cnt, gt, order, pred_cnt, llm_pred, pred):
        self.logger.info(f"*******************Start Eval*******************")
        # gt_cnt, gt_list, order, multi_solution, pred_cnt, llm_pred, pred = self.eval_check(pred, gt)
        
        mismatch_info = {
            'tool_error': 0, 
            'query_error': 0, 
            'task_len_error': 0, 
        }
        
        if pred_cnt < gt_cnt:
            mismatch_info['task_len_error'] += 1
            score = 0
            res_info = {
                'match_cnt': None, 
                'gt_cnt': gt_cnt, 
                'pred_cnt': pred_cnt, 
                'score': score, 
                'mismatch_info': mismatch_info, 
                'gt': gt, 
                'llm_pred': llm_pred, 
                'pred': pred, 
                'llm_pred_shot': None, 
            }
            self.logger.info(f"*******************End Eval*******************")
            if self.verbose:
                self.logger.info(f"*******************res_info: {res_info}*******************")
            return res_info, score
        
        match_cnt = 0
        llm_pred_shot = []
        for x in llm_pred:
            if x in gt:
                match_cnt += 1
                llm_pred_shot.append(x)
            else:
                mismatch_info['tool_error'] += 1
        score = int(llm_pred_shot == gt) if order else int(match_cnt == gt_cnt)
        res_info = {
            'match_cnt': match_cnt, 
            'gt_cnt': gt_cnt, 
            'pred_cnt': pred_cnt, 
            'score': score, 
            'mismatch_info': mismatch_info, 
            'gt': gt, 
            'llm_pred': llm_pred, 
            'pred': pred, 
            'llm_pred_shot': llm_pred_shot, 
        }
        
        self.logger.info(f"*******************End Eval*******************")
        if self.verbose:
            self.logger.info(f"*******************res_info: {res_info}*******************")
        return res_info, score


""" Evaluate interface"""

def evaluate(pred_json_path, gt_json_path, config):
    eval_kwagrs = config['eval_kwagrs']
    eval_kwagrs['tools'] = config['toolset']
    gt_key = eval_kwagrs.pop('gt_key', None)
    eval_type = config['eval_type']
    supported_eval = config['supported_eval']
    eval_path = config['eval_path']
    
    assert eval_type in supported_eval, f"No such eval_type named {eval_type}, please check the eval_type in config.yaml file."
    
    pred_dir, pred_file = os.path.split(pred_json_path)
    name = os.path.splitext(pred_file)[0]
    mkpath(eval_path)
    
    error_file = unix_path_join(eval_path, f"_pred_thresh{eval_kwagrs['sim_thresh']:.3f}_eval_error.json")
    res_file = unix_path_join(eval_path, f"_pred_thresh{eval_kwagrs['sim_thresh']:.3f}_eval_result.json")
    log_file = unix_path_join(eval_path, f"_pred_thresh{eval_kwagrs['sim_thresh']:.3f}_eval_log.log")
    # error_file = unix_path_join(eval_path, f"{name}_thresh{eval_kwagrs['sim_thresh']:.3f}_eval_error.json")
    # res_file = unix_path_join(eval_path, f"{name}_thresh{eval_kwagrs['sim_thresh']:.3f}_eval_result.json")
    # log_file = unix_path_join(eval_path, f"{name}_thresh{eval_kwagrs['sim_thresh']:.3f}_eval_log.log")
    
    logger = get_logger(log_file=log_file)
    logger.info(f"---------------Eval Setting Finished---------------")
    logger.info(f"---------------pred_json_path: {pred_json_path}---------------")
    logger.info(f"---------------gt_json_path: {gt_json_path}---------------")
    logger.info(f"---------------error_file: {error_file}---------------")
    logger.info(f"---------------res_file: {res_file}---------------")
    logger.info(f"---------------log_file: {log_file}---------------")
    
    logger.info(f"---------------Start Evaluation---------------")
    # load data
    pred_data = load_json(pred_json_path, json_type='all')
    pred_inds = sorted([int(x.split('Q')[-1]) for x in pred_data])
    
    gt_data = load_json(gt_json_path, json_type='all')
    gt_inds = sorted([int(x.split('Q')[-1]) for x in gt_data])
    
    # assert pred_inds == gt_inds, f"invalid pred_inds:{pred_inds} v.s. gt_inds{gt_inds}"
    if eval_type == "emb_sim":
        evaluator = EmbSimEvaluator(logger=logger, **eval_kwagrs)
    elif eval_type == "api_emb_sim":
        evaluator = APIEmbSimEvaluator(logger=logger, **eval_kwagrs)
    elif eval_type == "centurio_api":
        evaluator = CenturioAPIEvaluator(logger=logger, **eval_kwagrs)
    else:
        logger.info(f'No implement of {eval_type}.')
    
    eval_error_all = {}
    eval_res_all = {
        'all': {'count': 0, 'exact': 0, 'gt_num': 0, 'precison':0, 'recall':0, 'acc': 0},
    }
    for idx in tqdm(gt_inds, total=len(gt_inds)):
        logger.info(f"---------------第{idx}个问题---------------")
        eval_res_all['all']['gt_num'] += 1
        if idx not in pred_inds:
            continue
        predd, gtd = pred_data['Q' + str(idx)], gt_data['Q' + str(idx)]
        if gtd['question'] != predd['question']:
            logger.warning(
                f"question mismatch in gt: {gtd['question']} v.s. pred: {predd['question']}"
            )
            continue
        
        # pred, gt = predd['pred'], gtd['gt']
        pred, gt = predd['pred'], (gtd[gt_key] if gt_key else gtd['gt'])
        # TODO
        if 'gt_plan_order' in gtd:
            gt = {
                'gt': gt,
                'order': gtd['gt_plan_order'],
            }
        if 'gt_plan_multi_solution' in gtd:
            if isinstance(gt, dict):
                gt['multi_solution'] = gtd['gt_plan_multi_solution']
                # gt['gt_list'] = gtd['gt_plan_answer_list']
                gt['gt_list'] = gtd.get('gt_plan_answer_list', [])
            else:
                gt = {
                    'gt': gt,
                    # 'order': gtd['gt_plan_order'],
                    'multi_solution': gtd['gt_plan_multi_solution'],
                    # 'gt_list': gtd['gt_plan_answer_list'],
                    'gt_list': gtd.get('gt_plan_answer_list', []),
                }
        
        try:
            eval_res, eval_score = evaluator.eval_exact_match(pred, gt)
        except Exception as e:
            eval_error = {
                'question': predd['question'], 
                'error': str(e), 
            }
            eval_error_all['Q' + str(idx)] = eval_error
            logger.warning(
                f"an error raised when evaluation (question id: {idx}). "
                f"ERROR: {getattr(e.__class__, '__name__')}:{str(e)}"
            )
            continue
        eval_res_all['all']['count'] += 1
        eval_res_all['all']['exact'] += eval_score
        eval_res['question'] = predd['question']
        eval_res_all['Q' + str(idx)] = eval_res
    
    eval_res_all['all']['precison'] = 1. * eval_res_all['all']['exact'] / eval_res_all['all']['count'] \
        if eval_res_all['all']['count'] > 0 \
            else None
    eval_res_all['all']['recall'] = 1. * eval_res_all['all']['count'] / eval_res_all['all']['gt_num'] \
        if eval_res_all['all']['gt_num'] > 0 \
            else None
    eval_res_all['all']['acc'] = 1. * eval_res_all['all']['exact'] / eval_res_all['all']['gt_num'] \
        if eval_res_all['all']['gt_num'] > 0 \
            else None
    
    write_json(eval_res_all, res_file, json_type='all', mode='w')
    write_json(eval_error_all, error_file, json_type='all', mode='w')
    logger.info(f"---------------End Evaluation---------------")
    clear_logger_handlers(logger)
    return eval_res_all['all'], (error_file, res_file, log_file)

