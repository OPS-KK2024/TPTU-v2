""" auto_task测试demo """
import time
import socket
import threading
import sys
import queue
from autotask.agent.onestep_select_api_split_log_API_combination import SelectAgent
import yaml
import os

YAML_PATH = os.path.join("./autotask", "config.yaml")
# 开启socket服务
def socket_service():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 防止socket server重启后端口被占用（socket.error: [Errno 98] Address already in use）
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('127.0.0.1', 4455))
        s.listen(10)
    except socket.error as msg:
        print(msg)
        sys.exit(1)
    print('Waiting connection...')

    while 1:
        conn, addr = s.accept()
        # 定义消息队列，用于存储LLM返回的消息
        # 用于端到端的评测
        q_response = queue.Queue()
        # 用于总结最后的输出答案
        q_summarize = queue.Queue()
        # 用于UE端的消息传输
        q_ue = queue.Queue()
        t1 = threading.Thread(target=deal_data, args=(conn, addr, q_response, q_summarize, q_ue))
        t2 = threading.Thread(target=response_data, args=(conn, q_ue))
        # 缺少线程销毁机制，后续补充
        t1.start()
        t2.start()


# # 实时返回LLM的处理结果
# def response_data(conn, q_ue):
#     time.sleep(1)
#     while 1:
#         if q_ue.qsize() > 0:
#             str_send = str(q_ue.get())
#             if len(str_send) > 1200:
#                 split_01 = "split_01" + str_send[:1200]
#                 split_02 = "split_02" + str_send[1200:]
#                 conn.send(split_01.encode())
#                 time.sleep(0.01)
#                 conn.send(split_02.encode())
#             else:
#                 conn.send(str_send.encode())
#                 time.sleep(0.02)

# 实时返回LLM的处理结果
def response_data(conn, q_ue):
    time.sleep(1)
    while 1:
        if q_ue.qsize() > 0:
            str_send = str(q_ue.get())
            if 1500 < len(str_send) < 3000:
                split_01 = "split_01" + str_send[:1500]
                split_02 = "split_02" + str_send[1500:]
                split_03 = "split_03"
                conn.send(split_01.encode())
                time.sleep(0.05)
                conn.send(split_02.encode())
                time.sleep(0.05)
                conn.send(split_03.encode())
            elif len(str_send) > 3000:
                split_01 = "split_01" + str_send[:1500]
                split_02 = "split_02" + str_send[1500:3000]
                split_03 = "split_03" + str_send[3000:]
                conn.send(split_01.encode())
                time.sleep(0.05)
                conn.send(split_02.encode())
                time.sleep(0.05)
                conn.send(split_03.encode())
            else:
                conn.send(str_send.encode())
                time.sleep(0.02)

# 处理从UE端发来的消息
def deal_data(conn, addr, q_response, q_summarize, q_ue):
    print("---------socket线程---------")
    print('Accept new connection from {0}'.format(addr))

    # 加载模型配置
    with open(YAML_PATH, 'r', encoding='utf-8') as f:
        config = yaml.load(f.read(), Loader=yaml.FullLoader)
    agent = SelectAgent(config, q_response, q_summarize, q_ue)

    time.sleep(1)
    while 1:
        # 接收到的用户的指令
        user_instruction = conn.recv(4096).decode().strip()

        if not len(user_instruction) > 0:
            break
        # q.put(str_get)
        # 调用llm执行
        try:
            print("user_instruction : " + user_instruction)
            #  解析输入，获得用户问题和插件名称
            user_instruction = str(user_instruction)
            question = user_instruction[:user_instruction.find("_plugins_")]
            plugins_arr = user_instruction[user_instruction.find("_plugins_") + 9:]
            # print(question, plugins_arr)
            # 调用call函数
            agent(question, plugins_arr)
            # print(response)
        except Exception as exc:  # 捕获异常后打印出来
            print(exc)
        # # 给UE返回处理后的结果
        # conn.send(str(response).encode())
    conn.close()
    print('connection close {0}'.format(addr))


if __name__ == '__main__':
    socket_service()
