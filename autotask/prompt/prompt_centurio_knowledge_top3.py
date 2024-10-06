""" 定义与百夫长相关业务场景的prompt """

sys_prompt = """
您是我的AI助手,我会给您提供几个语句，您需要清楚每个语句想要表达的含义是什么。
最后我会给你一个问题，您的任务是理解这一问题想要表达的含义,并给出所提供的哪一个语句与此含义最相近。
下面是提供的几个语句：
{statement}
请使用下面这个格式:
Answer:最终答案
以下是一些问题答案输出格式的示例：
Answer:语句1：如何布控一批人。
Answer:都不相似。
下面正式开始：
问题是：{question}请问，从上述所提供的语句中，所给问题想表达的含义与哪一个语句想要表达的含义最相近？如果都不相近，请返回“都不相似”。
Answer:"""


format_prompt = """
您是我的AI助手,擅长各类文字的总结及处理，下面我将会给你一段文字描述，你需要把其中提到的功能名称整理出来且不重复，输出为列表形式。下面是相关的文字说明：
{info}
把上述描述中功能名称单独输出，输出为列表形式，请参考下面的格式：
Result:["功能名称"]
"""


final_answer_prompt_oneshot = """请你根据已有的信息，给出问题的答案。
注意你只能根据给定的History信息来解答问题。

请使用下面这个格式:

History:已知的信息
Question:这里是问题
Answer:最终的答案

下面正式开始。

History:{history}
Question:{question}
Answer:"""


class Centurio_Prompt:
    def __init__(self):
        pass

    @staticmethod
    def sys_prompt():
        return sys_prompt

    @staticmethod
    def format_prompt():
        return format_prompt

    @staticmethod
    def final_answer_prompt_oneshot():
        return final_answer_prompt_oneshot

    @staticmethod
    def select_prompt():
        return select_prompt
