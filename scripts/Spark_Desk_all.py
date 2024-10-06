from autotask.llm import SparkApi
from autotask.prompt.prompt_centurio_all import Centurio_Prompt
import json

# 以下密钥信息从控制台获取
appid = "43be81b4"  # 填写控制台中获取的 APPID 信息
api_secret = "Y2MwYmYxMjM0NjcwODA1ZmNiYjAwMjQ3"  # 填写控制台中获取的 APISecret 信息
api_key = "f409e09360bb4b6184907e1425605c91"  # 填写控制台中获取的 APIKey 信息
# 用于配置大模型版本，默认“general/generalv2”
# domain = "general"  # v1.5版本
domain = "generalv2"    # v2.0版本
# 云端环境的服务地址
# Spark_url = "ws://spark-api.xf-yun.com/v1.1/chat"  # v1.5环境的地址
Spark_url = "ws://spark-api.xf-yun.com/v2.1/chat"  # v2.0环境的地址


text = []


def getText(role, content):
    jsoncon = {}
    jsoncon["role"] = role
    jsoncon["content"] = content
    text.append(jsoncon)
    return text


def getlength(text):
    length = 0
    for content in text:
        temp = content["content"]
        leng = len(temp)
        length += leng
    return length


def checklen(text):
    while (getlength(text) > 8000):
        del text[0]
    return text


if __name__ == '__main__':
    text.clear
    prompt = Centurio_Prompt()
    qa_data = json.load(open('./database/qa_30_SenseCenturio.json', encoding='utf-8'))
    final_str = ''
    true_value_num = 0
    anno_all = {}
    anno_01 = []
    final_file = open('./log/Spark_Desk_all_v2.1.txt', 'a', encoding='utf-8')
    # f = open('./log/Spark_Desk_API_v2.1.json', "w", encoding="utf-8")
    for i in range(1, 31):
        anno = {}
        anno["Q" + str(i)] = {}
        qad = qa_data['Q' + str(i)]
        instruction = qad['question']
        action_prompt = prompt.sys_prompt().format(question=instruction)

        SparkApi.answer = ""
        # 星火认知第一次
        Input_01 = action_prompt
        question = checklen(getText("user", Input_01))
        SparkApi.main(appid, api_key, api_secret, Spark_url, domain, question)
        getText("assistant", SparkApi.answer)
        while True:
            if SparkApi.status == 2:
                answer_01 = SparkApi.answer
                # print(answer_01)
                final_str = "第%s个问题：" % i + "\n" + qad['question'] + str(answer_01) + "\n\n"
                final_file.write(final_str)
                print(answer_01)
                break
    #     # 星火认知第二次
    #     SparkApi.answer = ""
    #     format_prompt = prompt.format_prompt().format(info=answer_01)
    #     # print(format_prompt)
    #     Input_02 = format_prompt
    #     question_02 = checklen(getText("user", Input_02))
    #     SparkApi.main(appid, api_key, api_secret, Spark_url, domain, question_02)
    #     while True:
    #         if SparkApi.status == 2:
    #             answer_02 = SparkApi.answer.replace('\n','')
    #             print(answer_02)
    #             if '", "' in answer_02:
    #                 llm_answer = answer_02.split('["')[1].split('"]')[0].split('", "')
    #             elif "', '" in answer_02:
    #                 llm_answer = answer_02.split("['")[1].split("']")[0].split("', '")
    #             else:
    #                 llm_answer = []
    #             if answers == llm_answer:
    #                 true_value = True
    #                 true_value_num = true_value_num + 1
    #             else:
    #                 true_value = False
    #             # anno["Q" + str(i)]["return_plan_text"] = answer_01
    #             anno["Q" + str(i)]["return_plan_API"] = llm_answer
    #             anno["Q" + str(i)]["true_vlaue"] = true_value
    #             print()
    #             anno_01.append(anno)
    #             # ---------------------------------------
    #             break
    # anno_all["qa_list"] = anno_01
    # anno_all["accuracy"] = str(true_value_num) + "/" + str(len(qa_data))
    # f.write(json.dumps(anno_all, ensure_ascii=False, indent=4) + "\n")


