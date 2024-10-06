import requests

from autotask.prompt.prompt import Prompt
from autotask.llm.sensechat import SenseChat

final_result = ''

class GetWeather:

    def __init__(self, q_response):
        self.name = "get_weather"
        self.description = "get weather information."
        self.q_response = q_response

    def get_weather(self, location):
        url = "https://restapi.amap.com/v3/weather/weatherInfo?city=" + location + "&key=a6e3da0f958f7977a007d4ce1b7b01a6"
        info = requests.get(url)
        # print(info.text)
        message = eval(info.text)['lives'][0]['weather']
        temperature = eval(info.text)['lives'][0]['temperature']

        # print(location + "的天气：" + message + "，气温是：" + temperature + "度")
        global final_result
        final_result = location + "的天气：" + message + "，气温是：" + temperature + "度"
        # if not self.q_response is None:
        message = "晴，温度28℃"
        self.q_response.put(message)
        # print(self.name)
        return message

# weather = GetWeather()
# #
# # weather_01 = weather.get_weather("新疆")
# # weather_02 = weather.get_weather('北京')
# print(weather.get_weather('深圳'))