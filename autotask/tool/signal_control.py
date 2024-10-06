import math

from autotask.prompt.prompt import Prompt
from autotask.llm.sensechat import SenseChat

final_result_all = ""
class SignalControl:
    def __init__(self, q_response, summarize):
        self.name = "get_cycle"
        self.description = "get signal control cycle."
        self.q_response = q_response
        self.summarize = summarize

    def get_cycle(self, traffic_intensity, min_cycle, max_cycle):
        # print("Input:" + self)
        ik = 0.6
        r1 = 0.1
        r2 = 1
        c = min_cycle + (max_cycle - min_cycle) / pow((1 + math.exp((-traffic_intensity + ik) / r1)), r2)

        # print("answer: " + str(c))
        # print("该路口的周期为: " + str(c))

        final_result = "该路口的周期设置为" + str(c) + "s比较合适。"
        global final_result_all
        final_result_all = final_result
        # if not self.q_response is None:
        self.summarize.put(final_result)
        self.q_response.put(c)
        return c

    def get_strength(self, flow, loop_length,car_length, car_speed, time_occupancy):
        # 有一处路口的车道流量约为26，平均车身长度为2.6m，车辆的平均速度约为16m/s，检测线圈长度为28，时间占有率约为0.8，那么请问该路口的交通强度是多少？
        # print("Input:" + self)

        # 模型参数，表征流量和时间占有率的权重
        a = 1.2
        # 关键相位i对应关键车道的流量(pcu/h);
        # qi =
        # 关键相位i对应关键车道的饱和流率，为常数(pcu/h)
        si = 2.4
        # 关键相位i对应关键车道绿灯期间的时间占有率
        # oi =

        # 检测线圈长度(m)
        # l =
        # 平均车身长度(m)
        # li =
        # 关键相位i对应关键车道以饱和流量释放时车辆的平均速度，由交叉口具体情况确定

        # 关键相位i对应关键车道饱和流量释放时车道的时间占有率
        # usi =

        osi = si * (loop_length + car_length) / car_speed
        ii = a * flow / si + (1 - a) * time_occupancy / osi
        ii = round(ii, 2)
        # print("该路口的交通强度为: " + str(ii))

        final_result = "该路口的交通强度为" + str(ii) + "比较合适。"
        global final_result_all
        final_result_all = final_result
        # if not self.q_response is None:
        self.summarize.put(final_result)
        self.q_response.put(ii)
        return ii

    def get_cycle(self, traffic_intensity, min_cycle, max_cycle):
        # print("Input:" + self)
        ik = 0.6
        r1 = 0.1
        r2 = 1
        c = min_cycle + (max_cycle - min_cycle) / pow((1 + math.exp((-traffic_intensity + ik) / r1)), r2)

        # print("answer: " + str(c))
        # print("该路口的周期为: " + str(c))

        final_result = "该路口的周期设置为" + str(c) + "s比较合适。"
        global final_result_all
        final_result_all = final_result
        # if not self.q_response is None:
        self.summarize.put(final_result)
        self.q_response.put(c)
        # print(self.name)
        return c

    def get_time_delay(self,flow_ratio,saturation):

        time_delay = 5
        # print("车辆的延误时间为: " + str(time_delay))
        return time_delay