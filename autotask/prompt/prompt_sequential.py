""" 定义sequential相关的prompt """

system_prompt_sequential = """
你是一个策略模型，给定问题、工具集，你需要生成接下来调用的工具以及对应的子问题。

工具集中的每个工具定义如下:
SQL生成器: 给定一个输入问题和一个数据库，创建一个语法正确的 SQLite 查询语句。
PythonREPL: 给定一个输入问题和一些信息，生成一段语法正确的 Python 代码。

请使用下面这个格式:

Question:这里是问题
Error:这里是之前生成的错误输出，为空代表目前没有错误信息
History:这里是之前生成的子问题历史，为空代表目前没有历史信息
Tool_Query:这里是Python中Dict类型，字典的key表示选择的Tool，value是调用工具时输入的Query。请注意根据Error的提示生成更合理的Tool以及Query。
Result:这里是调用当前Tool_Query里Tool的输出结果
...
Error:这里是之前生成的所有错误输出
History:这里是之前生成的所有子问题历史
Tool_Query:无代表可以得到Final_Answer了
Result:无代表可以得到Final_Answer了
Final_Answer:这里是最终的答案，当Error和History足够推理出答案的时候直接给出Final_Answer

在上面的格式中...意味着(Error/History/Tool_Query/Result)可以重复N次。
当你能够得到Final_Answer的时候可以生成空的Tool_Query和Result，并给出Final_Answer
请在生成Result行或Final_Answer行后停下。


以下是一些示例:

Question:蔡依林的专辑数量的平方是多少？
Error:
History:
Tool_Query:{{"SQL生成器": "蔡依林的专辑数量是多少？"}}
Result:10
Error:
History:第1次执行工具的Tool_Query为:{{"SQL生成器": "蔡依林的专辑数量是多少？"}}，Result为:10
Tool_Query:{{"PythonREPL": "蔡依林的专辑数量的平方是多少？"}}
Result:100
Error:
History:第1次执行工具的Tool_Query为:{{"SQL生成器": "蔡依林的专辑数量是多少？"}}，Result为:10
        第2次执行工具的Tool_Query为:{{"PythonREPL": "蔡依林的专辑数量的平方是多少？"}}，Result为:100
Tool_Query:无
Result:无
Final_Answer:100

Question:先计算40的平方记为A，并找到粉丝总数比A少的所有歌手姓名。
Error:
History:
Tool_Query:{{"PythonREPL": "A为40的平方，A的值是多少？"}}
Result:1600
Error:
History:第1次执行工具的Tool_Query为:{{"SQL生成器": "蔡依林的专辑数量是多少？"}}，Result为:1600
Tool_Query:{{"SQL生成器": "粉丝总数比A少的所有歌手姓名"}}
Result:蔡依林
Error:
History:第1次执行工具的Tool_Query为: {{"PythonREPL": "A为40的平方，A的值是多少？"}}，Result为: 1600
        第2次执行工具的Tool_Query为: {{"SQL生成器": "粉丝总数比A少的所有歌手姓名"}}，Result为: 蔡依林
Tool_Query:无
Result:无
Final_Answer:蔡依林


你必须要注意的是：生成的Tool_Query必须严格符合格式要求，且每次只能生成一个Tool_Query。不要进行额外的问题分析，严格遵守题目的格式，生成类似示例的输出

下面正式开始:

Question:{question}
Error:{error}
History:{history}
Tool_Query:"""

# temporarily unavailable for planning
# python_prompt_sequential = """你是一个Python代码生成器，给定一个Question，你需要生成没有语法错误的Python代码，从而解决问题。


# 请严格按照下面的格式来生成Python代码并解决Question:
# Question: 这里是数学问题
# def solution():
#     这里是你要生成的Python代码
# Answer: 这里是执行Python代码输出的结果

# 以下是一些将问题映射到Python代码的示例:

# Question: 37593 * 67是多少？
# def solution():
#     return 37593 * 67
# Answer: 2518731

# Question: 37593的1/5次方是多少？
# def solution():
#     return 37593 ** 1/5
# Answer: 8.222831614237718

# Question: 以10为底5的对数是多少？
# def solution():
#     import math
#     return math.log(5, 10)
# Answer: 0.69897


# 下面正式开始:
# Question: {question}
# """

final_answer_prompt_sequential = """请你根据已有的信息，给出问题的答案。
注意你只能根据给定的History信息来解答问题。

请使用下面这个格式:
History: 已知的信息
Question: 这里是问题
Final_Answer: 最终的答案


下面正式开始:
History: {history}
Question: {question}
Final_Answer: """

# temporarily unavailable for planning
# sqlite_prompt_sequential_1 = """你是 SQLite 专家。 给定一个输入问题，首先创建一个语法正确的 SQLite 查询语句来运行，然后查看查询结果并给出输入问题的答案。
# 不要查询表中的所有列。 必须只查询回答问题所需的列。
# 请注意仅使用你可以在下表中看到的列名称。 注意不要查询不存在的列。 另外，请注意哪个列在哪个表中。

# 请使用下面这个格式:

# History:之前调用工具输出的信息
# Question:这里是问题
# Error:这里是之前生成的错误输出
# SQLQuery:要执行的SQL查询语句，请注意生成与Error中不同的SQLQuery
# SQLResult:SQL查询语句的执行结果
# Answer:最终的答案

# 注意仅使用下面的表:

# {table_info}


# History:{history}
# Question:{question}
# Error:{error}
# SQLQuery:"""

# sqlite_prompt_sequential_2 = sqlite_prompt_sequential_1 + """{sql_query}
# SQLResult:{sql_result}
# Answer:"""


class Prompt_Sequential:
    def __init__(self):
        pass

    @staticmethod
    def system_prompt_sequential():
        return system_prompt_sequential

    @staticmethod
    def python_prompt_sequential():
        return python_prompt_sequential

    @staticmethod
    def final_answer_prompt_sequential():
        return final_answer_prompt_sequential

    # temporarily unavailable for planning
    # @staticmethod
    # def sqlite_prompt_sequential_1():
    #     return sqlite_prompt_sequential_1

    # @staticmethod
    # def sqlite_prompt_sequential_2():
    #     return sqlite_prompt_sequential_2
    
    def __call__(self, **kwargs):
        return self.system_prompt_sequential().format(**kwargs)

    @property
    def stop(self):
        return {'get_tool': ['\nResult'], 'get_answer': ['\nFinal_Answer']}