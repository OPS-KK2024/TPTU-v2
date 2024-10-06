'''
============================
Utils for LLMs
============================
'''

import time 


def find_stop_in_message(stop, message):
    if stop is not None:
        stop_idxs = []
        for s in stop:
            if message.find(s) >= 0:
                stop_idxs.append(message.find(s))
        if len(stop_idxs) == 0:
            stop_idx = len(message)
        else:
            stop_idx = min(stop_idxs)
    else:
        stop_idx = len(message)
    
    return stop_idx


def find_idx_in_message(stop, message):
    '''
    this function extracts the Tool_Query dictionary from llm's response and also checks whether llm knows the final answer or not.

    input: 
        stop -> dict: including two keys, 'get_tool' and 'get_answer'.
                    'get_tool' refers to extracting the Tool_Query from the response, 
                    while 'get_answer' indicates that llm already knows the final answer
        message -> str: response of llm
    output:
        start_idx, end_idx -> int, which represent the idx of clipped part

    '''
    if stop and stop['agent_version'] == 1:
        stop_idxs = []
        for s in stop['get_answer']:
            if message.find(s) >= 0:
                return 0, 0 # set the value of the "action" variable to an empty string (''), which indicates that llm knows the final answer
        for s in stop['get_tool']:
            if message.find(s) >= 0:
                stop_idxs.append(message.find(s))
        if len(stop_idxs) == 0:
            stop_idx = len(message)
        else:
            stop_idx = min(stop_idxs)
        return 0, stop_idx     
    elif stop and stop['agent_version'] in (2, 3):
        res = {
            'thought': '',
            'tool': ''
        }
        if stop['get_thought'] and message.find(stop['get_thought']) >= 0:
            thought_idx = message.find(stop['get_thought'])
            res['thought'] = message[:thought_idx]
        else:
            return res 
        if stop['get_tool'] and message.find(stop['get_tool']) >= 0:
            tool_idx = message.find(stop['get_tool'])
            res['tool'] = message[thought_idx+len(stop['get_thought']):tool_idx]
        else:
            return res
        return res 
    else:
        print('Invalid value of parameter stop in the function find_idx_in_message(), please check it.')


def parsing_output_of_llm(agent_type, message, stop):
    '''
    parse the output of llm according different agent type and version 

    '''
    assert type(message) is str, f'Wrong type of message, which should be str but current is {type(message)}'
    if not stop:
        return message.strip(' ').strip('\n')
    if agent_type in ('onestep', 'twostep', 'centurio_api_onestep'):
        start_idx = 0
        if type(stop) is dict and 'start_token' in stop:
            start_token, end_token = stop['start_token'], stop['end_token']
            idx = message.find(start_token)
            if idx >= 0:
                # start_idx = idx + len(start_token)
                message = message[idx + len(start_token):]
                stop = [end_token]
            else:
                stop = [stop['common_token']]
        stop_idx = find_stop_in_message(stop, message)
    elif agent_type == 'sequential':
        if type(stop) is list:
            start_idx = 0
            stop_idx = find_stop_in_message(stop, message)
        elif stop['agent_version'] == 1:
            start_idx, stop_idx = find_idx_in_message(stop, message)
        elif stop['agent_version'] in (2, 3):
            time.sleep(3)
            return find_idx_in_message(stop, message).strip(' ').strip('\n')
        else:
            print('Version {} of the sequential agent has not been implemented yet.'.format(stop['agent_version']))
            exit()
    else:
        print('Function parsing_output_of_llm inside llm_utils:\nNo such type of agent, please check the config_API_retriever.yaml file.\n')
        exit()
    time.sleep(3)
    return message[start_idx:stop_idx].strip(' ').strip('\n')

