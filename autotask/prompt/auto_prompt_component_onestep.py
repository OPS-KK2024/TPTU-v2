from langchain.prompts import PromptTemplate
from copy import deepcopy
from autotask.utils.eval_utils_API_retriever import write_json, mkpath, evaluate, load_json
from autotask.prompt.prompt_component_onestep import (\
    DELIMITER, \
    # SIMP_1_PROMPT_COMP_TEMPLATE, \
    DATASET_CONSTRAINST_PROMPT_COMP_TEMPLATE, \
    ROLE_PROMPT_COMP_TEMPLATE, \
    TASK_PROMPT_COMP_TEMPLATE, \
    TOOLSET_CONSTRAINST_PROMPT_COMP_TEMPLATE, \
    OUTPUT_CONSTRAINST_PROMPT_COMP_TEMPLATE, \
    DEMO_PROMPT_COMP_TEMPLATE, \
    USER_INST_PROMPT_COMP_TEMPLATE, \
    ROLE_TASK_REIT_PROMPT_COMP_TEMPLATE, \
    USER_INST_REIT_PROMPT_COMP_TEMPLATE, \
    OUTPUT_CONSTRAINST_ERROR_FEEDBACK_PROMPT_COMP_TEMPLATE, \
    USER_INST_ERROR_FEEDBACK_PROMPT_COMP_TEMPLATE, \
    EN_DATASET_CONSTRAINST_PROMPT_COMP_TEMPLATE, \
    EN_ROLE_PROMPT_COMP_TEMPLATE, \
    EN_TASK_PROMPT_COMP_TEMPLATE, \
    EN_TOOLSET_CONSTRAINST_PROMPT_COMP_TEMPLATE, \
    EN_OUTPUT_CONSTRAINST_PROMPT_COMP_TEMPLATE, \
    EN_DEMO_PROMPT_COMP_TEMPLATE, \
    EN_USER_INST_PROMPT_COMP_TEMPLATE, \
    EN_ROLE_TASK_REIT_PROMPT_COMP_TEMPLATE, \
    EN_USER_INST_REIT_PROMPT_COMP_TEMPLATE, \
    EN_OUTPUT_CONSTRAINST_ERROR_FEEDBACK_PROMPT_COMP_TEMPLATE, \
    EN_USER_INST_ERROR_FEEDBACK_PROMPT_COMP_TEMPLATE, \
    toolset, \
    en_toolset, \
    toolset_bmtools, \
    en_toolset_bmtools, \
    toolset_bmtools_stock, \
    toolset_update_bmtools_stock, \
    toolset_update_bmtools_stock_expand, \
    toolset_bmtools_map, \
    toolset_centurio, \
    few_shot_demonstrations, \
    few_shot_demonstrations_bmtools, \
    few_shot_demonstrations_bmtools_stock, \
    few_shot_demonstrations_update_bmtools_stock, \
    few_shot_demonstrations_update_bmtools_stock_expand, \
    few_shot_demonstrations_bmtools_map, \
    few_shot_demonstrations_centurio, \
)
    


""" Auto Prompt Component Config """

AUTO_PROMPT_COMPONENT_CONFIG = {
    'zh':{
        '0': {
            'name': 'DATASET', 
            'description': '数据集描述，数据集中的具体数据内容和说明。', 
            'template': DATASET_CONSTRAINST_PROMPT_COMP_TEMPLATE, 
            'input_variables': ['table_info'], 
            },  
        '1': {
            'name': 'ROLE', 
            'description': '角色描述，根据这个，便可以知道该角色是什么领域的资深专家。', 
            'template': ROLE_PROMPT_COMP_TEMPLATE, 
            'input_variables': [], 
            }, 
        '2': {
            'name': 'TASK', 
            'description': '任务描述，根据这个，便可以知道任务是解决什么类型的问题。', 
            'template': TASK_PROMPT_COMP_TEMPLATE, 
            'input_variables': [], 
            }, 
        '3': {
            'name': 'TOOLSET', 
            'description': '工具集描述，工具集中的每个工具定义和说明。', 
            'template': TOOLSET_CONSTRAINST_PROMPT_COMP_TEMPLATE, 
            'input_variables': ['toolset'], 
            }, 
        '4': {
            'name': 'OUTPUTFORMAT', 
            'description': '输出要求描述，根据这个，便可以知道输出需要遵循的具体要求，比如类型、格式、内容等。', 
            'template': OUTPUT_CONSTRAINST_PROMPT_COMP_TEMPLATE, 
            'input_variables': [], 
            }, 
        '5': {
            'name': 'DEMO', 
            'description': '要求提供几个不同的例子，更好的进行解释。', 
            'template': DEMO_PROMPT_COMP_TEMPLATE, 
            'input_variables': ['demonstrations'], 
            }, 
        '6': {
            'name': 'USER_INST', 
            'description': '用户的问题描述。', 
            'template': USER_INST_PROMPT_COMP_TEMPLATE, 
            'input_variables': ['question'], 
            }, 
        # '7_1': ROLE_TASK_REIT_PROMPT_COMP_TEMPLATE, 
        # '7_2': USER_INST_REIT_PROMPT_COMP_TEMPLATE, 
        # '8_1': OUTPUT_CONSTRAINST_ERROR_FEEDBACK_PROMPT_COMP_TEMPLATE, 
        # '8_2': USER_INST_ERROR_FEEDBACK_PROMPT_COMP_TEMPLATE, 
    },
}

""" Auto Prompt Instance """

AUTO_PROMPT_CONFIG = {
    'qa20':{
        'new_baseline': 
            {
                'language': 'zh',
                'inds': ['1', '2', '3', '4', '5', '6'],
                'inner_kwargs': {
                    'toolset': toolset,
                    'demonstrations': few_shot_demonstrations,
                    },
                'stop': ['\nAnswer'],
            }, 
        'seed_new_baseline': 
            {
                'language': 'zh',
                'inds': ['1', '2', '3', '4', '5'],
                'inner_kwargs': {
                    'toolset': toolset,
                    'demonstrations': few_shot_demonstrations,
                    },
                'stop': ['\nAnswer'],
            }, 
    }, 
    'bmtools':{
        'new_baseline': 
            {
                'language': 'zh',
                'inds': ['1', '2', '3', '4', '5', '6'],
                'inner_kwargs': {
                    'toolset': toolset_bmtools,
                    'demonstrations': few_shot_demonstrations_bmtools,
                    },
                'stop': ['\nAnswer'],
            }, 
        'seed_new_baseline': 
            {
                'language': 'zh',
                'inds': ['1', '2', '3', '4', '5'],
                'inner_kwargs': {
                    'toolset': toolset_bmtools,
                    'demonstrations': few_shot_demonstrations_bmtools,
                    },
                'stop': ['\nAnswer'],
            }, 
    }, 
    'bmtools_stock':{
        'new_baseline': 
            {
                'language': 'zh',
                'inds': ['1', '2', '3', '4', '5', '6'],
                'inner_kwargs': {
                    'toolset': toolset_bmtools_stock,
                    'demonstrations': few_shot_demonstrations_bmtools_stock,
                    },
                'stop': ['\nAnswer'],
            }, 
        'seed_new_baseline': 
            {
                'language': 'zh',
                'inds': ['1', '2', '3', '4', '5'],
                'inner_kwargs': {
                    'toolset': toolset_bmtools_stock,
                    'demonstrations': few_shot_demonstrations_bmtools_stock,
                    },
                'stop': ['\nAnswer'],
            }, 
    }, 
    'update_bmtools_stock':{
        'new_baseline': 
            {
                'language': 'zh',
                'inds': ['1', '2', '3', '4', '5', '6'],
                'inner_kwargs': {
                    'toolset': toolset_update_bmtools_stock,
                    'demonstrations': few_shot_demonstrations_update_bmtools_stock,
                    },
                'stop': ['\nAnswer'],
            }, 
        'seed_new_baseline': 
            {
                'language': 'zh',
                'inds': ['1', '2', '3', '4', '5'],
                'inner_kwargs': {
                    'toolset': toolset_update_bmtools_stock,
                    'demonstrations': few_shot_demonstrations_update_bmtools_stock,
                    },
                'stop': ['\nAnswer'],
            }, 
    }, 
    'update_bmtools_stock_expand':{
        'new_baseline': 
            {
                'language': 'zh',
                'inds': ['1', '2', '3', '4', '5', '6'],
                'inner_kwargs': {
                    'toolset': toolset_update_bmtools_stock_expand,
                    'demonstrations': few_shot_demonstrations_update_bmtools_stock_expand,
                    },
                'stop': ['\nAnswer'],
            }, 
        'seed_new_baseline': 
            {
                'language': 'zh',
                'inds': ['1', '2', '3', '4', '5'],
                'inner_kwargs': {
                    'toolset': toolset_update_bmtools_stock_expand,
                    'demonstrations': few_shot_demonstrations_update_bmtools_stock_expand,
                    },
                'stop': ['\nAnswer'],
            }, 
    }, 
    'bmtools_map':{
        'new_baseline': 
            {
                'language': 'zh',
                'inds': ['1', '2', '3', '4', '5', '6'],
                'inner_kwargs': {
                    'toolset': toolset_bmtools_map,
                    'demonstrations': few_shot_demonstrations_bmtools_map,
                    },
                'stop': ['\nAnswer'],
            }, 
        'seed_new_baseline': 
            {
                'language': 'zh',
                'inds': ['1', '2', '3', '4', '5'],
                'inner_kwargs': {
                    'toolset': toolset_bmtools_map,
                    'demonstrations': few_shot_demonstrations_bmtools_map,
                    },
                'stop': ['\nAnswer'],
            }, 
    }, 
    'centurio':{
        'new_baseline': 
            {
                'language': 'zh',
                'inds': ['1', '2', '3', '4', '5', '6'],
                'inner_kwargs': {
                    'toolset': toolset_centurio,
                    'demonstrations': few_shot_demonstrations_centurio,
                    },
                'stop': ['\nAnswer'],
            }, 
        'seed_new_baseline': 
            {
                'language': 'zh',
                'inds': ['1', '2', '3', '4', '5'],
                'inner_kwargs': {
                    'toolset': toolset_centurio,
                    'demonstrations': few_shot_demonstrations_centurio,
                    },
                'stop': ['\nAnswer'],
            }, 
    }, 
}

SEED_PROMPT_NAME = "seed_new_baseline"
REF_PROMPT_NAME = "new_baseline"
CANDIDATE_INDS = ('1', '2', '4')

""" Auto Prompt class Definition """

class Auto_Prompt_Component_OneStep:
    def __init__(self, prompt_template, inner_kwargs, stop):
        self.prompt_template = prompt_template
        # Check that the stop is valid
        assert isinstance(stop, list) or stop is None
        self._stop = stop
        self.inner_kwargs = {k: v for k, v in inner_kwargs.items() if k in self.prompt_template.input_variables}
        print(f'**** {self.__class__.__name__} has been successfully initialized ****')
        print(f'**** stop ({self.stop})  ****')
        print(f"**** prompt content\n{self.__call__(**{'question': 'xxxx', 'error': 'xxxx', **self.inner_kwargs})}\n ****")
        # raise Exception()

    def __call__(self, **kwargs):
        prompt_kwargs = deepcopy(self.inner_kwargs)
        for k in kwargs:
            if k in self.prompt_template.input_variables:
                prompt_kwargs[k] = kwargs[k]
        return self.prompt_template.format(**prompt_kwargs)
    
    @property
    def stop(self):
        return self._stop


class DemosPrompt:
    def __init__(self, prompt_template, delimiter='\n\n'):
        self.prompt_template = prompt_template
        self.delimiter = delimiter

    def __call__(self, data):
        """
        Fills in the template with the given values. Data is a tuple of lists.
        """
        demos = []
        for i, (input_, output_) in enumerate(zip(*data)):
            demos.append(self.prompt_template.format(input=input_, output=output_))
        return self.delimiter.join(demos)


""" Prompt Template Definition """

def get_prompt_template(task_name, prompt_name, prompt_config, prompt_component_config, delimiter=DELIMITER, has_language=True):
    if isinstance(prompt_config, dict):
        prompt_config = prompt_config
    elif isinstance(prompt_config, str):
        prompt_config = load_json(prompt_config, json_type='all')
    else:
        raise ValueError(f'Invalid type(prompt_config): {type(prompt_config)}')
    
    if isinstance(prompt_component_config, dict):
        prompt_component_config = prompt_component_config
    elif isinstance(prompt_component_config, str):
        prompt_component_config = load_json(prompt_component_config, json_type='all')
    else:
        raise ValueError(f'Invalid type(prompt_component_config): {type(prompt_component_config)}')
    
    prompt_info = prompt_config[task_name][prompt_name]
    if has_language:
        prompt_component_config = prompt_component_config[prompt_info['language']]
    input_variables = []
    for idx in prompt_info['inds']:
        assert isinstance(prompt_component_config[idx]['input_variables'], list)
        input_variables.extend(prompt_component_config[idx]['input_variables'])
    prompt_template = PromptTemplate(input_variables=input_variables,
                            template=delimiter.join(prompt_component_config[idx]['template'] for idx in prompt_info['inds']),
                            )
    inner_kwargs, stop = deepcopy(prompt_info['inner_kwargs']), deepcopy(prompt_info['stop'])
    return prompt_template, inner_kwargs, stop


def get_simple_demos_template(demos_template, mode='qta-tuples'):
    if demos_template is None:
        if mode == 'io-pairs':
            demos_template = PromptTemplate(input_variables=['input', 'output'],
                                    template="Input: {input}\nOutput: {output}",
                                    )
        elif mode == 'qt-pairs':
            demos_template = PromptTemplate(input_variables=['input', 'output'],
                                    template="Question: {input}\nTasks: {output}",
                                    )
        elif mode == 'qta-tuples':
            demos_template = PromptTemplate(input_variables=['input', 'output'],
                                    template="Question: {input}\nTasks: {output}\nAnswer: 已完成",
                                    )
        elif mode == 'zh-qt-pairs':
            demos_template = PromptTemplate(input_variables=['input', 'output'],
                                    template="问题是：{input}\n答案是：{output}",
                                    )
        else:
            raise ValueError('Invalid mode: {}'.format(mode))
    
    return demos_template