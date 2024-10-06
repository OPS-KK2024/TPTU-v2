from autotask.prompt.prompt_onestep import Prompt_OneStep
from autotask.prompt.prompt_sequential import Prompt_Sequential
from autotask.prompt.prompt_component_onestep import Prompt_Component_OneStep
from autotask.prompt.auto_prompt_component_onestep import Auto_Prompt_Component_OneStep, get_prompt_template, AUTO_PROMPT_COMPONENT_CONFIG, AUTO_PROMPT_CONFIG, DELIMITER, DemosPrompt, get_simple_demos_template
from autotask.prompt.prompt_component_onestep_centurio_api import get_prompt_centurio_api
from autotask.utils.eval_utils_API_retriever import write_json, mkpath, evaluate, load_json, emb_similarity
from autotask.utils.retriever import ToolRetriever, parse_api

from datetime import datetime
import os
import numpy as np
from copy import deepcopy
from collections import defaultdict

""" utils for prompt """

def get_prompt(config):
    if config['agent_type'] == 'onestep':
        assert 'prompt_type' in config, 'Lack the type of prompt, please check the config_API_retriever.yaml file.'
        # assert config["prompt_type"] in config["supported_prompt"], "No such prompt type {}, please check the prompt_type in config_API_retriever.yaml file.".format(config["prompt_type"])
        if config["prompt_type"] in ("prompt_component_onestep", ):
            return Prompt_Component_OneStep(config["prompt_kwargs"]["prompt_name"])
        elif config["prompt_type"] in ("auto_prompt_component_onestep", ):
            task_name = config["prompt_kwargs"]["task_name"]
            prompt_name = config["prompt_kwargs"]["prompt_name"]
            prompt_config = config["prompt_kwargs"]["prompt_config"]
            prompt_component_config = config["prompt_kwargs"]["prompt_component_config"]
            if prompt_config == "default":
                prompt_config = AUTO_PROMPT_CONFIG
            if prompt_component_config == "default":
                prompt_component_config = AUTO_PROMPT_COMPONENT_CONFIG
            return Auto_Prompt_Component_OneStep(*get_prompt_template(task_name, prompt_name, prompt_config, prompt_component_config, delimiter=DELIMITER))
        elif config["prompt_type"] in ("prompt_onestep", ):
            return Prompt_OneStep()
        else:
            raise NotImplementedError('No implement of {}.'.format(config["prompt_type"]))
    elif config['agent_type'] == 'sequential':
        return Prompt_Sequential()
    elif config['agent_type'] == 'centurio_api_onestep':
        assert 'prompt_type' in config, 'Lack the type of prompt, please check the config_API_retriever.yaml file.'
        if config["prompt_type"] in ("prompt_component_onestep_centurio_api", ):
            return get_prompt_centurio_api(config)
        else:
            raise NotImplementedError('No implement of {}.'.format(config["prompt_type"]))
    raise NotImplementedError('No such agent type {}, please check the agent_type in config_API_retriever.yaml file.'.format(config["agent_type"]))

def get_prompt_name(config):
    if config['agent_type'] == 'onestep':
        assert 'prompt_type' in config, 'Lack the type of prompt, please check the config_API_retriever.yaml file.'
        # assert config["prompt_type"] in config["supported_prompt"], "No such prompt type {}, please check the prompt_type in config_API_retriever.yaml file.".format(config["prompt_type"])
        if config['prompt_type'] in ("prompt_component_onestep", ):
            return config['prompt_kwargs']['prompt_name']
        elif config['prompt_type'] in ("auto_prompt_component_onestep", ):
            return config['prompt_kwargs']['auto_prompt_name']
        elif config['prompt_type'] in ("prompt_onestep", ):
            return ""
        else:
            raise NotImplementedError('No implement of {}.'.format(config['prompt_type']))
    elif config['agent_type'] == 'sequential':
        return ""
    elif config['agent_type'] == 'centurio_api_onestep':
        assert 'prompt_type' in config, 'Lack the type of prompt, please check the config_API_retriever.yaml file.'
        if config['prompt_type'] in ("prompt_component_onestep_centurio_api", ):
            return config['prompt_kwargs']['prompt_name']
        else:
            raise NotImplementedError('No implement of {}.'.format(config['prompt_type']))
    raise NotImplementedError('No such agent type {}, please check the agent_type in config_API_retriever.yaml file.'.format(config["agent_type"]))

def get_save_name(config):
    now = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    prompt_name = get_prompt_name(config)
    if prompt_name:
        prompt_name = f"_{prompt_name}"
    return f"{config['llm_name']}_{config['agent_type']}{prompt_name}_planning_{now}", now


def actions_postprocess(actions):
    l, r = 0, len(actions) - 1
    if actions.find('[') >= 0:
        l = actions.find('[')
    if actions.rfind(']') >= 0:
        r = actions.rfind(']')
    return actions[l: r + 1]



def parse_data(qa_data, question_inds, gt_key):
    if not gt_key:
        gt_key = 'gt'
    inputs = list(map(lambda x: qa_data['Q' + str(x)]['question'], question_inds))
    outputs = list(map(lambda x: qa_data['Q' + str(x)][gt_key], question_inds))
    data = {
        'data': (inputs, outputs),
    }
    if 'tool_set' in qa_data['Q' + str(question_inds[0])]:
        assert isinstance(qa_data['Q' + str(question_inds[0])]['tool_set'], list)
        data['tool_set'] = list(map(lambda x: qa_data['Q' + str(x)]['tool_set'], question_inds))
    return data

def subsample_data(data, subsample_size):
    """
    Subsample data. Data is in the form of a tuple of lists.
    """
    inputs, outputs = data['data']
    assert len(inputs) == len(outputs)
    assert len(inputs) >= subsample_size
    indices = np.random.choice(len(inputs), subsample_size, replace=False)
    out = {
        'data': ([inputs[i] for i in indices], [outputs[i] for i in indices]),
    }
    if 'tool_set' in data:
        toolset = data['tool_set']
        assert len(inputs) == len(toolset)
        out['tool_set'] = [toolset[i] for i in indices]
    return out

def cat_data(data1, data2):
    """
    Subsample data. Data is in the form of a tuple of lists.
    """
    inputs1, outputs1 = data1['data']
    inputs2, outputs2 = data2['data']
    assert len(inputs1) == len(outputs1)
    assert len(inputs2) == len(outputs2)
    out = {
        'data': (inputs1 + inputs2, outputs1 + outputs2),
    }
    if 'tool_set' in data1 and 'tool_set' in data2:
        toolset1, toolset2 = data1['tool_set'], data2['tool_set']
        assert len(inputs1) == len(toolset1)
        assert len(inputs2) == len(toolset2)
        out['tool_set'] = toolset1 + toolset2
    return out


# top_compares, top_inds, top_scores = emb_similarity(query, [comp]+compares, top_k=1, model_name_or_path='all-mpnet-base-v2')
# demos_data = subsample_data(prompt_gen_data, config['auto_prompt_kwargs']['generation']['num_demos'])
# if prompt_gen_data_fixed:
#     demos_data = cat_data(demos_data, prompt_gen_data_fixed)
def adaptive_ICL(query, data, subsample_size, model_name_or_path='BAAI/bge-large-zh'):
    """
    Subsample data. Data is in the form of a tuple of lists.
    """
    inputs, outputs = data['data']
    assert len(inputs) == len(outputs)
    assert len(inputs) >= subsample_size
        
    compares = [x[::-1] for x in inputs]
    # compares = [f"{x[::-1]}\n{x}" for x in inputs]
    # compares = [str(x) for x in outputs]
    # compares = inputs
    # query, compares = f"Question: {query}", [f"Question: {inputs[i]}\nTasks: {str(outputs[i])}" for i in range(len(inputs))]
    
    top_compares, top_inds, top_scores = emb_similarity(query, compares, top_k=subsample_size, model_name_or_path=model_name_or_path)
    indices = top_inds
    
    out = {
        'data': ([inputs[i] for i in indices], [outputs[i] for i in indices]),
    }
    if 'tool_set' in data:
        toolset = data['tool_set']
        assert len(inputs) == len(toolset)
        out['tool_set'] = [toolset[i] for i in indices]
    return out

def get_agent_kwargs(qad, data, config, api_wrapper, is_aicl=False):
    # demos_prompt = DemosPrompt(get_simple_demos_template(demos_template=None, mode=config['auto_prompt_kwargs']['evaluation']['demos_mode']), delimiter='\n\n')
    # demos_data = adaptive_ICL(query=query, data=data, 
    #                           subsample_size=config['auto_prompt_kwargs']['evaluation']['num_demos'], 
    #                           model_name_or_path=config['auto_prompt_kwargs']['evaluation']['demos_retriever_model'], 
    #                           )
    
    # agent_kwargs = {
    #     'demonstrations': demos_prompt(demos_data['data']),
    # }
    # if 'tool_set' in demos_data:
    #     toolset_list = []
    #     for x in demos_data['tool_set']:
    #         toolset_list.extend(x)
    #     # toolset_list = sorted(list(set(toolset_list)))
    #     # agent_kwargs['tool_set'] = '\n'.join(toolset_list)
    #     agent_kwargs['tool_set'] = sorted(list(set(toolset_list)))
    
    # return agent_kwargs
    if is_aicl:
        query = qad['question']
        demos_prompt = DemosPrompt(get_simple_demos_template(demos_template=None, mode=config['auto_prompt_kwargs']['evaluation']['demos_mode']), \
                                delimiter='\n', \
                                # delimiter='\n\n', \
                                )
        demos_data = adaptive_ICL(query=query, data=data, 
                                subsample_size=config['auto_prompt_kwargs']['evaluation']['num_demos'], 
                                model_name_or_path=config['auto_prompt_kwargs']['evaluation']['demos_retriever_model'], 
                                )
        agent_kwargs = {
            'demonstrations': demos_prompt(demos_data['data']),
        }
        if 'tool_set' in demos_data:
            toolset_list = []
            for x in demos_data['tool_set']:
                toolset_list.extend(x)
            agent_kwargs['tool_set'] = sorted(list(set(toolset_list)))
    else:
        agent_kwargs = {}
    
    agent_kwargs['instruction'] = qad['question']

    # api_wrapper = APIWRAPPER(config)
    data_dict = api_wrapper.get_tool_set_dict(qad)
    if 'tool_set' in data_dict:
        assert isinstance(data_dict['tool_set'], list)
        if 'tool_set' in agent_kwargs:
            agent_kwargs['tool_set'] = sorted(list(set(agent_kwargs['tool_set'] + data_dict['tool_set'])))
        else:
            agent_kwargs['tool_set'] = data_dict['tool_set']
            # agent_kwargs['tool_set'] = sorted(list(set(data_dict['tool_set'])))
    
    if 'tool_set' in agent_kwargs:
        agent_kwargs['tool_set'] = '\n'.join(agent_kwargs['tool_set'])
        # agent_kwargs['tool_set'] = '\n'.join(f"{i + 1}、{x.strip()}" for i, x in enumerate(agent_kwargs['tool_set']))
    
    if 'relevant_docs' in data_dict:
        agent_kwargs['relevant_docs'] = data_dict['relevant_docs']
    
    if 'prompt_prefix' in qad:
        agent_kwargs['prompt_prefix'] = qad['prompt_prefix']
    if 'prompt_suffix' in qad:
        agent_kwargs['prompt_suffix'] = qad['prompt_suffix']
    return agent_kwargs


# api wrapper
class APIWRAPPER:
    def __init__(self, config):
        self.add_retrieval = config['auto_prompt_kwargs']['evaluation']['add_retrieval']
        self.corpus_tsv_path = config['auto_prompt_kwargs']['evaluation']['corpus_tsv_path']
        self.retrieval_model_path = config['auto_prompt_kwargs']['evaluation']['retrieval_model_path']
        self.retrieved_api_nums = config['auto_prompt_kwargs']['evaluation']['retrieved_api_nums']
        
        if self.add_retrieval:
            self.retriever = self.get_retriever()
        else:
            self.retriever = None

    def get_retriever(self):
        return ToolRetriever(corpus_tsv_path=self.corpus_tsv_path, model_path=self.retrieval_model_path)
    
    def retrieve_tools(self, query, top_k):
        retrieved_tools = self.retriever.retrieving(query, top_k=top_k, excluded_tools={})
        query_json = {"tool_set":[], "relevant_docs":[]}
        for tool_dict in retrieved_tools:
            if len(query_json["tool_set"]) == top_k:
                break
            doc_id = tool_dict["doc_id"]
            doc = tool_dict["doc"]
            tool_name = tool_dict["tool_name"]
            score = tool_dict["score"]
            query_json["tool_set"].append(doc)
            query_json["relevant_docs"].append(deepcopy(tool_dict))
        # deduplicate
        tool_set_info = defaultdict(list)
        for i, doc in enumerate(query_json["tool_set"]):
            tool_set_info[doc].append(i)
        unique_tool_set = sorted(list(tool_set_info), key=lambda x: tool_set_info[x][0])
        unique_inds = [tool_set_info[x][0] for x in unique_tool_set]
        query_json["tool_set"] = unique_tool_set
        query_json["relevant_docs"] = [query_json["relevant_docs"][i] for i in unique_inds]
        return query_json
    
    def get_tool_set_dict(self, qad):
        data_dict = {}
        if self.retriever is not None:
            query = qad['question']
            data_dict = self.retrieve_tools(query, top_k=self.retrieved_api_nums)
        else:
            if 'tool_set' in qad:
                assert isinstance(qad['tool_set'], list)
                data_dict['tool_set'] = qad['tool_set']
        return data_dict
