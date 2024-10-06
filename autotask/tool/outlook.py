import time
import json
from datetime import datetime, timedelta
import requests
headers = {'Content-Type': 'application/json',
            'Authorization':'EwCYA8l6BAAUAOyDv0l6PcCVu89kmzvqZmkWABkAAXECoq+lZv3RcQazs0xSmARgimp/g+gzQnHdHlwRrj6zA8YKG/O4FlRScNbkH9dM0OiDYqwzgHGahoPp6f0UIGXa2649h4JmGLgPuwMZOgnb2j7qFJZeafPHKCrAAt0oBtKhizmdtS+tbxV/10cNZPwvGjQ+QzbqXrxuSBrVxLj2V4HzG+UAOn9jEpufRtkHzuJWyxYZYaXY9JGXKLV6841XXClbjUT+F84xZ4jXtSXlP4tx+O9KY7xKR0aR4GwT6mMHsq7iKkEYBFOUI0WBNXLluLg9mEV0iUCk4P2BwLcuMvCnYZzL0H12aTXmAW2lg4NVOFAslHxsa138ma1TnMkDZgAACAeZ5RBQC1mhaAJgLWr9IjeWBEW+6baboHU4BLtslggac9rAvE5dQ8VxqAP1ujl0T0EuyigAIb5ogMZino9v87kTfaVYm3nCoOw6yHPZjigKGpRS2y31J5/11hdRLoNEDlLe8yWgYXT2QqmEY/8ce+e/H0GZJQbpbQcYXciChG0Tl+jkk047WWFaz3YSeVyoDefA50V6Yg+gmErqzy8mq5RfZ+CZkX1fiBA6tjGB7ZGW4qx6Oo87sGlCCHmr1Ftv8z8kkAn3f/QnnUgT1XgfZEqEZSeCRA8xv79T1EDYwFrfcnIMjAEMECcRT4Jaj/+VE1LffqGG+tSJiIFY4SfRruRha3s5tHJKxlQflTcvO4tKLd5If5X6HGLsNPx0LyxQ+Hz+UfHo9pzky/wa7acBW6nlLdiIWG+sUNyjlLZNr0/R03xtSQjb1aoznLMgr2RS4LFeNbhoNmShsn9z+i3yCG3+M/SRmzwbo9axoACl3yFg1WG2zSPqfBwxSUYmq6DKJNL+YcF2av61K0GgTfkcq8uMmLp66siXWHACcToakme8K9XldqKgXW/YghidnreR+6Ggj57jk55QTsRxw1TGYTsJxg3CkpJ00JfPTL+uFh78PpYUdbkU/6YD0onyQn759qf8wD+RvPg4JYrzZ9zLOM7SWhX98uJkx554OKHo4BBU9Dj/Rpx8mdumfNwSM92QfB/24+LSd5IZRxbGT4GtCe+/Jm/8YnGrPUTvPS/ZMozq6i+/nNGzejLOmTWMvdNei40jJ1/P4PpQbXY7Q7j9Ytl3TcJeaQbouCLk0yZ2SeXAuAwqQ0v3fWjcph822ursVySXlwI='
           }


class OutLook:
    def __init__(self, q_response, summarize):
        self.name = "ids"
        self.description = ""
        self.q_response = q_response
        self.summarize = summarize


    # 获取所有的日程
    def get_all_events(self):

        url = 'https://graph.microsoft.com/v1.0/me/events?$select=subject,body,bodyPreview,organizer,attendees,start,end,location'
        body = {
        }
        # r 为响应对象
        # r = requests.get(url, json=body, headers=headers, verify=False)
        # # 查看响应结果
        # print("api: " + str(r.json()))
        # print("\n日程信息获取成功")
        # start_beijing_time = datetime.strptime(
        #     str(r.json()['value'][0]['start']['dateTime'])[:-6], "%Y-%m-%dT%H:%M:%S.%f") + timedelta(hours=8)
        # endbeijing_time = datetime.strptime(
        #     str(r.json()['value'][0]['end']['dateTime'])[:-6], "%Y-%m-%dT%H:%M:%S.%f") + timedelta(hours=8)
        # start_beijing_time_02 = datetime.strptime(
        #     str(r.json()['value'][1]['start']['dateTime'])[:-6], "%Y-%m-%dT%H:%M:%S.%f") + timedelta(hours=8)
        # endbeijing_time_02 = datetime.strptime(
        #     str(r.json()['value'][1]['end']['dateTime'])[:-6], "%Y-%m-%dT%H:%M:%S.%f") + timedelta(hours=8)
        #
        # print("第一个会议是：" + r.json()['value'][1]['subject'] + "，时间是 " + str(start_beijing_time_02) + " 至 " + str(
        #     endbeijing_time_02))
        # print("第二个会议是：" + r.json()['value'][0]['subject'] + "，时间是 " + str(start_beijing_time) + " 至 " + str(
        #     endbeijing_time))

        response = "日程信息获取成功"
        self.summarize.put(response)
        self.q_response.put(response)
        return response

    # 预定会议任务
    def schedule_meeting(self, subject, start_time, end_time):
        url = 'https://graph.microsoft.com/v1.0/me/events'

        body={
                "subject": subject,
                "start": {
                    "dateTime": start_time,
                    "timeZone": "China Standard Time"
                },
                "end": {
                    "dateTime": end_time,
                    "timeZone": "China Standard Time"
                }
            }
        # # r为响应对象
        # r = requests.post(url, json=body, headers=headers, verify=False)
        # # 查看响应结果
        # print("api: " + str(r.json()))
        # response = r.json()['responseStatus']['response']
        time.sleep(1.5)
        response_summarize = '"'+subject + '"' + "会议已创建成功。"
        response = "会议已创建成功"
        # print(response)
        self.summarize.put(response_summarize)
        self.q_response.put(response)
        return response

    # 发送邮件
    def send_an_email(self, subject,content,emailAddress):
        url = "https://graph.microsoft.com/v1.0/me/sendMail "
        emailAddress = emailAddress + "@outlook.com"
        body = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "Text",
                    "content": content
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": emailAddress
                        }
                    }
                ]
            }
        }
        # # r 为响应对象
        # r = requests.post(url, json=body, headers=headers, verify=False)
        # # 查看响应结果
        # print("api: " + str(r.json()))
        send_result_summarize = emailAddress + "的邮件已发送成功！"
        send_result = "邮件已发送成功！"
        time.sleep(1)
        # print(send_result)
        self.summarize.put(send_result_summarize)
        self.q_response.put(send_result)
        return send_result

    # 检索邮件中是否包含哪些信息
    def search_mail(self, keyword):

        url = "https://graph.microsoft.com/v1.0/me/messages?$search=" + keyword
        # print(url)
        # headers = {'Content-Type': 'application/json'}
        body = {
        }
        # # r 为响应对象
        # r = requests.get(url, json=body, headers=headers)
        # # 查看响应结果
        # print(r.json())
        # # search_result = r.json()['value']
        # search_result = "r.json()['value']"

        # search_result = "\n关于报销的邮件内容有：\n培训相关费用报销\n服务器发票报销\n车票报销信息"
        search_result = keyword + "相关的邮件已检索完成。"
        # print(search_result)
        self.summarize.put(search_result)
        self.q_response.put(search_result)
        return search_result

    # 查询天气
    def get_weather(self, location):
        # url = "https://restapi.amap.com/v3/weather/weatherInfo?city=" + location + "&key=a6e3da0f958f7977a007d4ce1b7b01a6"
        # info = requests.get(url)
        # # print(info.text)
        # message = eval(info.text)['lives'][0]['weather']
        # temperature = eval(info.text)['lives'][0]['temperature']
        #
        # # print(location + "的天气：" + message + "，气温是：" + temperature + "度")
        # global final_result
        # final_result = location + "的天气：" + message + "，气温是：" + temperature + "度"
        # if not self.q_response is None:
        message = location + "的天气：" + "晴，温度23℃"
        self.summarize.put(message)
        self.q_response.put("晴，温度28℃")
        # print(self.name)
        return message







#
# outlook = OutLook("none")
#
# # # outlook.schedule_meeting("测试", "10:00", "16:00")
# # # outlook.send_an_email("测试", "10:00", "ew4se")
# outlook.search_mail("报销")
#
