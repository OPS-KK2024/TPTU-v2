# 提取tool并转化为list
def get_tool_list(answers):
    tools = []
    for answer in answers:
        for tool, query in answer.items():
            # 解析得到对应的tool、query
            tools.append(tool)
    return tools


