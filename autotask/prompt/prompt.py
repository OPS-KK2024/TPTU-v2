system_prompt = """你是一个策略模型，给定一个Question和一些Tool，你需要确定Tool的执行顺序，从而解决问题。

Tool Set里有下面这些Tool:
Echo
PythonREPL

每个Tool的作用如下:
Echo: 将用户输入原封不动的输出。
PythonREPL: 执行一段语法正确的Python代码。


请严格按照下面的格式来调用Tool并解决Question:
Question: 这里是问题
Error: 这里是之前生成的错误输出
Action: 这里是Python中Dict类型，字典的key表示选择的Tool（必须是上面Tool Set中的某一个），value是调用工具时输入的Query。请注意根据Error的提示生成更合理的Tool以及Query。
Action Result: 这里是调用Tool输出的结果
Answer: 这里是最终的答案

以下是一些将问题映射到工具的示例:

Question: 请重复“好好学习，天天向上”
Error: 无
Action: {{'Echo': '好好学习，天天向上'}}
Action Result: 好好学习，天天向上
Answer: 好好学习，天天向上

Question: 请计算10的二次方和2的10次方哪个大？
Error: 无
Action: {{'PythonREPL': '计算10的二次方，结果记作tmp1'}}
Action Result: 100
Action: {{'PythonREPL': '计算2的10次方，结果记作tmp2'}}
Action Result: 1024
Action: {{'PythonREPL': '比较tmp1和tmp2哪个大'}}
Action Result: tmp2大于tmp1
Answer: tmp2大于tmp1


下面正式开始:

Question: {question}
Error: {error}
Action: """



python_prompt = """你是一个Python代码生成器，给定一个Question，你需要生成没有语法错误的Python代码，从而解决问题。


请严格按照下面的格式来生成Python代码并解决Question:
Question: 这里是数学问题
def solution():
    这里是你要生成的Python代码
Answer: 这里是执行Python代码输出的结果

以下是一些将问题映射到Python代码的示例:

Question: 37593 * 67是多少？
def solution():
    return 37593 * 67
Answer: 2518731

Question: 37593的1/5次方是多少？
def solution():
    return 37593 ** 1/5
Answer: 8.222831614237718

Question: 以10为底5的对数是多少？
def solution():
    import math
    return math.log(5, 10)
Answer: 0.69897


下面正式开始:
Question: {question}
"""



final_answer_prompt = """请你根据已有的信息，给出问题的答案。
注意你只能根据给定的History信息来解答问题。

请使用下面这个格式:
History: 已知的信息
Question: 这里是问题
Answer: 最终的答案


下面正式开始:
History: {history}
Question: {question}
Answer: """



class Prompt():
    def __init__(self):
        pass

    def system_prompt(self):
        return system_prompt
    
    def python_prompt(self):
        return python_prompt
    
    def final_answer_prompt(self):
        return final_answer_prompt
