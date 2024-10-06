""" auto_task测试demo """
import time
import socket
import threading
import sys
import queue
from autotask.agent.onestep_centurio_API_retriever import CenturioAPIOneStepAgent
import yaml
import os
from autotask.utils.prompt_utils_API_retriever import get_agent_kwargs, APIWRAPPER

# 配置文件
YAML_PATH = os.path.join("./autotask", "config_API_retriever.yaml")

# 开启socket服务
def socket_service():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 防止socket server重启后端口被占用（socket.error: [Errno 98] Address already in use）
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('10.4.27.16', 4455))
        s.listen(10)
    except socket.error as msg:
        print(msg)
        sys.exit(1)
    print('Waiting connection...')

    while 1:
        conn, addr = s.accept()
        # 定义消息队列，用于存储LLM返回的消息
        q_response = queue.Queue()
        t1 = threading.Thread(target=deal_data, args=(conn, addr, q_response))
        # t2 = threading.Thread(target=response_data, args=(conn, q_response))
        # 缺少线程销毁机制，后续补充
        t1.start()
        # t2.start()


# 实时返回LLM的处理结果
def response_data(conn, q_response):
    time.sleep(1)
    while 1:
        if q_response.qsize() > 0:
            conn.send(str(q_response.get()).encode())
            time.sleep(0.05)


# 处理从UE端发来的消息
def deal_data(conn, addr, q_response):
    print("---------socket线程---------")
    print('Accept new connection from {0}'.format(addr))
    # 加载模型配置
    with open(YAML_PATH, 'r', encoding='utf-8') as f:
        config = yaml.load(f.read(), Loader=yaml.FullLoader)
    # loading demonstration data for adaptive ICL
    demos_data, demos_inds = None, None
    # agent_type
    if config['agent_type'] == 'centurio_api_onestep':
        agent = CenturioAPIOneStepAgent(config, q_response)
    else:
        print(
            'No such agent type {}, please check the agent_type in config_API_retriever.yaml file.'.format(config["agent_type"]))
        exit()
    # API_retriever
    api_wrapper = APIWRAPPER(config)
    # time.sleep(1)
    while 1:
        # 接收到的用户的指令
        user_instruction = conn.recv(4096).decode().strip()
        if not len(user_instruction) > 0:
            break
        # 调用llm执行
        try:
            print("user_instruction : " + user_instruction)
            anno = {}
            anno['question'] = user_instruction
            agent_kwargs = get_agent_kwargs(qad=anno, data=demos_data, config=config, api_wrapper=api_wrapper,
                                            is_aicl=False)
            agent(**agent_kwargs)
            if q_response.qsize() > 0:
                conn.send(str(q_response.get()).encode())
            # print(response)
        except Exception as exc:  # 捕获异常后打印出来
            print(exc)
        # # 给UE返回处理后的结果
        # conn.send(str(response).encode())
    conn.close()
    print('connection close {0}'.format(addr))


if __name__ == '__main__':
    socket_service()
