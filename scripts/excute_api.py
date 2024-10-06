""" 用于测试在不同任务时，能否正确调用api"""
import time
import socket
import threading
import sys
import queue
from autotask.agent.onestep_select_api import SelectAgent
import yaml
import os

YAML_PATH = os.path.join("./autotask", "config.yaml")

# 开启socket服务
def socket_service():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 防止socket server重启后端口被占用（socket.error: [Errno 98] Address already in use）
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('10.4.27.14', 4466))
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
        t2 = threading.Thread(target=response_data, args=(conn, q_response))
        # 缺少线程销毁机制，后续补充
        t1.start()
        t2.start()


# 实时返回LLM的处理结果
def response_data(conn, q_response):
    time.sleep(1)
    while 1:
        if q_response.qsize() > 0:
            # str_ = str(q_response.get()).encode()
            conn.send(str(q_response.get()).encode())
            time.sleep(0.05)


# 处理从UE端发来的消息
def deal_data(conn, addr, q_response):
    print("---------socket线程---------")
    print('Accept new connection from {0}'.format(addr))

    # 加载模型配置
    with open(YAML_PATH, 'r', encoding='utf-8') as f:
        config = yaml.load(f.read(), Loader=yaml.FullLoader)
    agent = SelectAgent(config, q_response)

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
            agent(user_instruction)
            # print(response)
        except Exception as exc:  # 捕获异常后打印出来
            print(exc)
        # # 给UE返回处理后的结果
        # conn.send(str(response).encode())
    conn.close()
    print('connection close {0}'.format(addr))


if __name__ == '__main__':
    socket_service()
