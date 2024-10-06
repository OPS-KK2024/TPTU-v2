""" 用于定义在评估planning阶段中可能存在的异常 """


# 自定义异常类，表示格式校验出现问题时抛出异常
class FormatException(Exception):
    pass


# 自定义异常类，表示生成的tool错误时抛出的异常
class ToolException(Exception):
    pass


# 自定义异常类，表示生成的格式有误
class FormatException(Exception):
    pass


# 定义输出结果中是否符合格式（Result）
class ReturnFormat:
    def return_format(self, str_info):
        if "Result: [" in str_info:
            return print("")
        elif "Result:[" in str_info:
            return print("")
        elif "[" in str_info:
            return print("")
        else:
            raise FormatException


# 定义工具选择是否正确
class ToolSelect:
    def tool_name(self, toolname):
        if toolname == 'SQL生成器':
            return print("")
        if toolname == 'PythonREPL':
            return print("")
        else:
            raise ToolException
