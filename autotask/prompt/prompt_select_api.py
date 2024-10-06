







""" 用于测试是否可以选择正确的api工具 """

system_prompt_select = """
你是一个策略模型，我会给定你一些工具集和一个问题，你需要理解问题的含义并选择合适的工具执行。
注意，你首先要判断问题是否为复杂问题，如果是的话，你需要将其拆解为多个子问题进行回答，不要一次性给出答案。

工具集中的每个工具定义如下:
{"tool_list":[{"get_weather":{"description":"用于查询天气的情况。","input":["地点名称location"],"output":"温度temperature"}},{"get_cycle":{"description":"用于查询交通路口周期相关问题，比如关于路口的周期设置。","input":["路口的交通强度traffic_intensity","最大周期max_cycle","最小周期min_cycle"],"output":"路口周期time_cycle"}},{"get_strength":{"description":"用于查询交通路口强度相关问题，比如关于路口的相位交通强度是多少。","input":["车道流量flow","检测线圈长度loop_length","平均车身长度car_length","车辆的平均速度car_speed","时间占有率time_occupancy"],"output":"路口的交通强度traffic_intensity"}},{"get_time_delay":{"description":"用于计算交通路口车辆的延误时间。","input":["流量比flow_ratio","饱和度saturation"],"output":"延误时间time_delay"}},{"get_location":{"description":"用于将地址转换为经纬度坐标。","input":["详细地址address"],"output":"经纬度坐标coordinate"}},{"get_uuid":{"description":"用于将经纬度坐标转换为IDS地理位置注册编码。","input":["经纬度坐标coordinate"],"output":"编码uuid"}},{"get_route_result":{"description":"用于查询路径规划结果。","input":["IDS编码列表loc_uuid_all"],"output":"规划的路径"}},{"get_poi_search":{"description":"通过关键字进行查询POI信息。","input":["查询关键字keyword"],"output":""}},{"get_location_search":{"description":"用于查询IDS地理位置注册编码对应的经纬度坐标。","input":["IDS点位编码uuid"],"output":"经纬度坐标coordinate"}},{"get_location_delete":{"description":"用于删除IDS地理位置注册编码对应的信息。","input":["IDS点位编码uuid"],"output":""}}]}

请使用下面这个格式，注意不需要生成其他信息:
question_01:这是拆分的第一个子问题
answer：这是第一个问题调用的工具及参数
question_02:这是拆分的第二个子问题
answer：这是第二个问题调用的工具及参数
stop

以下是回答的示例:
question_01:北京的天气怎么样
answer：weather_01 = weather.get_weather('北京')
question_02:该路口的交通强度是多少？
answer：cycle_01 = signalcontrol.get_cycle(traffic_intensity=110,min_cycle=20,max_cycle=30)
stop

question_01:问题一
answer：coordinate_01 = ids.get_location('详细地址address')
stop

question_01:问题一
answer：uuid_01 = ids.get_uuid(coordinate_01)
stop

question_01:问题一
answer：result_01 = ids.get_route_result([uuid_01,uuid_02])
stop

下面正式开始:
广东省深圳市福田区福中三路市民中心C区和广东省深圳市福田区太平洋保险大厦这两个地方的经纬度坐标分别是多少？
"""


final_answer_prompt_oneshot = """下面我会给你一个问题和答案，麻烦你帮我优化下，让答案更加丰富。你只需要返回最终优化后的答案即可。
问题是：{question}
答案是：{answer}
优化后的答案是：

cycle_01 = signalcontrol.get_cycle(traffic_intensity=110,min_cycle=20,max_cycle=30)

strength_01 = signalcontrol.get_strength(flow=11,loop_length=22,car_length=6.2,car_speed=23,time_occupancy=2)

location_01 = ids.get_location('广东省深圳市福田区太平洋保险大厦')

uuid_01 = ids.get_uuid('114.052543,22.564281')

result_01 = ids.get_route_result(['e8089020-c52b-47a4-a76b-213a23f3e469'])


以下是回答的示例:

question:北京的天气怎么样
answer：weather_01 = weather.get_weather('北京')
stop

question:该路口的交通强度是多少？
answer：cycle_01 = signalcontrol.get_cycle(traffic_intensity=110,min_cycle=20,max_cycle=30)
stop


"""


class Prompt_Select:
    def __init__(self):
        pass

    @staticmethod
    def system_prompt_select():
        return system_prompt_select

    @staticmethod
    def final_answer_prompt_oneshot():
        return final_answer_prompt_oneshot




