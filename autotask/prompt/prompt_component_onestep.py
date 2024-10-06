from langchain.prompts import PromptTemplate
from copy import deepcopy


""" 定义onestep相关的prompt component """


""" Basic Prompt Component """

ROLE_PROMPT_COMP_TEMPLATE = """你是一位策略方面的AI专家。"""
EN_ROLE_PROMPT_COMP_TEMPLATE = """You are an AI expert specialized in strategy."""


TASK_PROMPT_COMP_TEMPLATE = """我会为你提供问题和工具集，你的任务是根据给定的前提条件，将用户的问题分解为更小、可管理的、可按顺序执行的子任务，然后逐步解决子任务，最后合并输出得到结果，从而解决问题。"""
EN_TASK_PROMPT_COMP_TEMPLATE = """I will provide you with a question and a set of tools. Your task is to break down the user's question into smaller, manageable, and sequentially executable subtasks based on given premises, and then solve these subtasks step by step, finally merging the outputs to obtain the result and solve the question."""


TOOLSET_CONSTRAINST_PROMPT_COMP_TEMPLATE = """工具集中的每个工具定义如下:
{toolset}"""
EN_TOOLSET_CONSTRAINST_PROMPT_COMP_TEMPLATE = """Each tool in the toolset is defined as follows:
{toolset}"""


DATASET_CONSTRAINST_PROMPT_COMP_TEMPLATE = """数据库的信息如下:
{table_info}"""
EN_DATASET_CONSTRAINST_PROMPT_COMP_TEMPLATE = """The information of the database is as follows:
{table_info}"""


OUTPUT_CONSTRAINST_PROMPT_COMP_TEMPLATE = """请使用下面这个格式:
Question:这里是问题
Tasks:这里是Python中List类型，List中每一项是一个字典，字典的key表示选择的Tool，value是调用工具时输入的Query。请注意生成与Error中不同的Tool以及Query。
Answer:最终的答案"""
EN_OUTPUT_CONSTRAINST_PROMPT_COMP_TEMPLATE = """Please use the following format:
Question: Here is the question.
Tasks: This is a Python List, where each item is a dictionary. The key of the dictionary represents the selected tool, and the value is the query input when calling the tool. Please note that the generated tool and query should be different from that in the Error.
Answer: The final answer."""


DEMO_PROMPT_COMP_TEMPLATE = """以下是一些将问题映射到工具的示例:
{demonstrations}"""
EN_DEMO_PROMPT_COMP_TEMPLATE = """Here are examples of mapping a question to tasks:
{demonstrations}"""


USER_INST_PROMPT_COMP_TEMPLATE = """下面正式开始:
Question:{question}
Tasks:"""
EN_USER_INST_PROMPT_COMP_TEMPLATE = """Let's begin:
Question:{question}
Tasks:"""

""" Extra Prompt Component """

#################################
# re-iterate modifications

ROLE_TASK_REIT_PROMPT_COMP_TEMPLATE = """在进行问题分解时，请考虑到不同子任务之间的依赖关系，并确定不同子任务所需的工具。请记住，您是最优秀的AI策略专家，将运用您的专业知识提供最佳的规划。"""
EN_ROLE_TASK_REIT_PROMPT_COMP_TEMPLATE = """When decomposing the question, please consider the dependencies between different subtasks and determine the tools required for each subtask. Remember, you are an outstanding AI strategy expert and will apply your expertise to provide the best plan."""


USER_INST_REIT_PROMPT_COMP_TEMPLATE = """你必须要注意的是：你只需回答生成的Tasks，请不要提供其他内容，不要在回答中写解释。生成的Tasks必须严格符合格式要求：必须是Python中List类型，List中每一项是一个字典，字典的key表示选择的Tool（其中Tool必须从工具集里给定的工具中选取），字典的value是调用Tool时输入的Query。"""
EN_USER_INST_REIT_PROMPT_COMP_TEMPLATE = """Please note: You only need to answer the generated Tasks without providing any additional content or explanations. The generated Tasks must strictly adhere to the required format: a Python List, where each item is a dictionary. The key of the dictionary represents the selected tool (which must be chosen from the given toolset), and the value is the query input when calling the tool."""


#################################
# error feedback modifications

OUTPUT_CONSTRAINST_ERROR_FEEDBACK_PROMPT_COMP_TEMPLATE = """请使用下面这个格式:
Question:这里是问题
Error:这里是之前生成的错误输出
Tasks:这里是Python中List类型，List中每一项是一个字典，字典的key表示选择的Tool，value是调用工具时输入的Query。请注意生成与Error中不同的Tool以及Query。
Answer:最终的答案"""
EN_OUTPUT_CONSTRAINST_ERROR_FEEDBACK_PROMPT_COMP_TEMPLATE = """Please use the following format:
Question: Here is the question.
Error: This is the previously generated error output.
Tasks: This is a Python List, where each item is a dictionary. The key of the dictionary represents the selected tool, and the value is the query input when calling the tool. Please note that the generated tool and query should be different from that in the Error.
Answer: The final answer."""

USER_INST_ERROR_FEEDBACK_PROMPT_COMP_TEMPLATE = """下面正式开始:
Question:{question}
Error:{error}
Tasks:"""
EN_USER_INST_ERROR_FEEDBACK_PROMPT_COMP_TEMPLATE = """Let's begin:
Question:{question}
Error:{error}
Tasks:"""


""" Simplified Prompt Component """

SIMP_1_PROMPT_COMP_TEMPLATE = """工具集中的每个工具定义如下:
{toolset}

你的任务是将用户的question分解为更小、可管理的、可按顺序执行的query，并根据query内容找到最匹配的工具类；回复的工具类别必须在提供的工具集中，并且必须按格式回复：“[{{'工具类别': 'query'}},]”。

举例：
{demonstrations}

Question:{question}
Answer:"""


""" toolset definition """

toolset = """SQL生成器: 给定一个输入问题和一个数据库，创建一个语法正确的 SQLite 查询语句。
PythonREPL: 给定一个输入问题和一些信息，生成一段语法正确的 Python 代码。"""
en_toolset = """SQL生成器: Given an input question and a database, create a syntactically correct SQLite query statement.
PythonREPL: Given an input question and some information, generate a piece of syntax-correct Python code."""

#################################
# for bmtools

toolset_bmtools = """Bing_search: 用于进行搜索的 Bing API。
Slides_making: 此工具可以帮助您创建具有文本、段落、图像和漂亮样式的 PPT 幻灯片。
Weather: 用于查找天气信息的插件。"""
en_toolset_bmtools = """Bing_search: The Bing API to use for performing searches.
Slides_making: This tool allows you to create ppt slides with text, paragraph, images, with good looking styles.
Weather: Plugin for look up weather information."""

#################################
# for bmtools_stock

toolset_bmtools_stock = """PRICE: 用于进行股市价格查询的 API，能够返回公司特定日期或日期范围内的每日或每月最高、最低、开盘或收盘价格。
MIN: 参数将是一个数据列表，API将返回列表中数字的最小值。
MAX: 参数将是一个数据列表，API将返回列表中数字的最大值。
AVG: 参数将是一个数据列表，API将返回列表中数字的平均值。
SUM: 参数将是一个数据列表，API将返回列表中数字的总和。
MINUS: 将需要两个数据作为参数，然后返回第一个数据减去第二个数据的结果。
ADD: 将需要两个数据作为参数，然后返回第一个数据加上第二个数据的结果。
DIVIDE: 将需要两个数据作为参数，然后返回第一个数据除以第二个数据的结果。"""

#################################
# for update_bmtools_stock

toolset_update_bmtools_stock = """PRICE: 用于进行股市价格查询的 API，能够返回公司特定日期或日期范围内的每日或每月最高、最低、开盘或收盘价格。它包含4个参数，第一个参数是"type1"，表示我们查询的是"DAILY"还是"MONTHLY"信息；第二个参数是"type2"，表示我们需要什么类型的价格信息，包括"open"代表开盘价，"close"代表收盘价，"high"代表最高价，"low"代表最低价，"volume"表示股票交易量。第三个参数是"symbol"，表示我们查询的公司，可以是IBM、Apple、Google等，但每次调用此API只能查询一个公司。第四和第五个参数是可选的，当我们查询日期范围时，将有"date_start"表示查询的起始日期，类似地，我们有第五个参数"date_end"。否则，第四个参数将是"date"，表示我们查询的具体日期，而且不会有第五个参数。
MIN: 参数将是一个数据列表，API将返回列表中数字的最小值。
MAX: 参数将是一个数据列表，API将返回列表中数字的最大值。
AVG: 参数将是一个数据列表，API将返回列表中数字的平均值。
SUM: 参数将是一个数据列表，API将返回列表中数字的总和。
MINUS: 将需要两个数据作为参数，然后返回第一个数据减去第二个数据的结果。
ADD: 将需要两个数据作为参数，然后返回第一个数据加上第二个数据的结果。
DIVIDE: 将需要两个数据作为参数，然后返回第一个数据除以第二个数据的结果。
参数应该位于括号内，API调用应出现在括号之前，例如MIN(a, b)返回a-b，MAX(a, b, c)返回a、b、c中的最大值，PRICE的调用可以作为MIN、MAX、AVG、SUM、MINUS、ADD、DIVIDE API的参数，例如，MIN(PRICE(...), PRICE(...))。不允许使用其他API。"""

#################################
# for update_bmtools_stock_expand

toolset_update_bmtools_stock_expand = """PRICE: 用于进行股市价格查询的 API，能够返回公司特定日期或日期范围内的每日或每月最高、最低、开盘或收盘价格。它包含4个参数，第一个参数是"type1"，表示我们查询的是"DAILY"还是"MONTHLY"信息；第二个参数是"type2"，表示我们需要什么类型的价格信息，包括"open"代表开盘价，"close"代表收盘价，"high"代表最高价，"low"代表最低价，"volume"表示股票交易量。第三个参数是"symbol"，表示我们查询的公司，可以是IBM、Apple、Google等，但每次调用此API只能查询一个公司。第四和第五个参数是可选的，当我们查询日期范围时，将有"date_start"表示查询的起始日期，类似地，我们有第五个参数"date_end"。否则，第四个参数将是"date"，表示我们查询的具体日期，而且不会有第五个参数。
MIN: 参数将是一个数据列表，API将返回列表中数字的最小值。
MAX: 参数将是一个数据列表，API将返回列表中数字的最大值。
AVG: 参数将是一个数据列表，API将返回列表中数字的平均值。
SUM: 参数将是一个数据列表，API将返回列表中数字的总和。
MINUS: 将需要两个数据作为参数，然后返回第一个数据减去第二个数据的结果。
ADD: 将需要两个数据作为参数，然后返回第一个数据加上第二个数据的结果。
DIVIDE: 将需要两个数据作为参数，然后返回第一个数据除以第二个数据的结果。
EXCHANGE_RATE: 此API返回一对实体货币和数字货币的实时汇率。它包含2个参数，第一个参数是"from_currency"，表示我们查询的实体货币，例如美元；第二个参数是"to_currency"，表示我们查询的数字货币，例如比特币。
STOCK_SYMBOL: 此API返回股票市场上指定公司实体的股票代码。它包含1个参数，第一个参数是"entity"，表示我们查询的公司，可以是IBM、Apple、Google等。
FORECAST_PRICE: 用于进行股市价格预测的 API，能够预测给定公司在未来特定日期或日期范围内的每日或每月最高、最低、开盘或收盘价格。它包含4个参数，第一个参数是"type1"，表示我们预测的是"DAILY"还是"MONTHLY"信息；第二个参数是"type2"，表示我们需要预测什么类型的价格信息，包括"open"代表开盘价，"close"代表收盘价，"high"代表最高价，"low"代表最低价，"volume"表示股票交易量。第三个参数是"symbol"，表示我们预测的公司，可以是IBM、Apple、Google等，但每次调用此API只能预测一个公司。第四和第五个参数是可选的，当我们预测日期范围时，将有"date_start"表示预测的起始日期，类似地，我们有第五个参数"date_end"。否则，第四个参数将是"date"，表示我们预测的具体日期，而且不会有第五个参数。
CUMSUM: 参数将是一个数据列表，API将返回列表中数字的累积和。
SUM_POW2: 参数将是一个数据列表，API将返回列表中数字的总和的平方。
SUM_FLOOR: 参数将是一个数据列表，API将返回列表中数字的总和的向下取整。
SUM_CEIL: 参数将是一个数据列表，API将返回列表中数字的总和的向上取整。
AVG_POW2: 参数将是一个数据列表，API将返回列表中数字的平均值的平方。
AVG_FLOOR: 参数将是一个数据列表，API将返回列表中数字的平均值的向下取整。
AVG_CEIL: 参数将是一个数据列表，API将返回列表中数字的平均值的向上取整。
参数应该位于括号内，API调用应出现在括号之前，例如MIN(a, b)返回a-b，MAX(a, b, c)返回a、b、c中的最大值，PRICE和FORECAST_PRICE的调用可以作为MIN、MAX、AVG、SUM、MINUS、ADD、DIVIDE、CUMSUM、SUM_POW2、SUM_FLOOR、SUM_CEIL、AVG_POW2、AVG_FLOOR、AVG_CEIL 这些API的参数，例如，MIN(PRICE(...), PRICE(...))，CUMSUM(FORECAST_PRICE(...), FORECAST_PRICE(...))。不允许使用其他API。"""

#################################
# for bmtools_map

toolset_bmtools_map = """DISTANCE: 用于进行距离查询的 API，能够返回两个地点之间的驾驶距离。
SEARCH: 用于进行地点查询的 API，能够返回在指定知名地点附近的餐厅或洗手间等地点。
ROUTE: 用于进行路线查询的 API，能够返回两个地点之间的驾驶路线。
COORDINATE: 用于进行坐标查询的 API，能够返回特定地点的坐标、经纬度。
MIN: 参数将是一个数据列表，API将返回列表中数字的最小值。
MAX: 参数将是一个数据列表，API将返回列表中数字的最大值。
AVG: 参数将是一个数据列表，API将返回列表中数字的平均值。
SUM: 参数将是一个数据列表，API将返回列表中数字的总和。
NUM: 参数将是一个数据列表，API将返回列表中数字的数量。
MINUS: 将需要两个数据作为参数，API将返回第一个数据减去第二个数据的结果。
ADD: 将需要两个数据作为参数，API将返回第一个数据加上第二个数据的结果。
DIVIDE: 将需要两个数据作为参数，API将返回第一个数据除以第二个数据的结果。"""

#################################
# for centurio

toolset_centurio = """布控-任务管理: 支持新建布控任务，可针对库模块中已创建的人像库、车辆库、船舶库等进行布控；支持设置布控时间、精确/模糊阈值；开启智能布控，可在告警后自动布控相关区域； 支持多种方式选源，细粒度配置任务权限。
入库助手-创建: 创建入库任务、选择人像库对应的布控库/静态库、身份库；从本地上传人像压缩包文件、从服务器选择人像图片文件夹；支持选择是否启动人员去重(包含身份ID去重、人脸比对去重)、选择是否启动自动翻转和强制入库；支持配置/删除/添加/编辑文件命名规则。
智能检索-结果查看: 支持查看布控库、静态库、全息档案的检案结果、人脸抓拍结果、人体抓拍结果；支持通过人脸图片检索出关联的车辆；支持通过人脸/人体图片检索出关联的事件；支持多种细致操作，如过滤排序、详情查看、比中操作、抓拍和轨迹分析等，以及导出收藏和继续检索等后续使用。
布控-结果查看: 支持按任务权限过滤，查看各类告警信息、人像档案、历史告警记录、活动轨迹，进行告警研判、设置处理，并在地图上直观展示告警分布。通过多维度的告警统计分析以及趋势观察，可以全面评估布控质量，发现布控存在的问题，持续优化布控系统。
全息档案-检索结果: 支持按相似度从高到低查看检索结果；支持按有抓拍的档案、标签对检索结果进行筛选并查看；支持查看该档案的抓拍信息；支持每一个检索结果的个人档案详情查看；支持对同一人员存在的多个档案进行合并。
告警中心-布控告警: 可查看已有布控任务的所有历史告警，并通过多种筛选条件进行过滤。可对人体智能布控列表进行编辑。按时间维度进行告警卡片展示（默认），也可以选择按目标人员显示告警。并支持查看历史告警，配置推送设置以及导出告警记录。支持查看多维智能布控列表，可查看开启人体布控的任务和人员。人脸产生告警后支持对单个人开启人体智能告警并在开启后会在人脸告警后的一段时间内在告警点位周围进行人体布控。"""


""" few-shot demos(task planning) """

few_shot_demonstrations = """Question:蔡依林的专辑数量的平方是多少？
Tasks:[{"SQL生成器": "蔡依林的专辑数量是多少？"}, {"PythonREPL": "蔡依林的专辑数量的平方是多少？"}]
Answer:蔡依林的专辑数量的平方是100

Question:先计算40的平方记为A，并找到粉丝总数比A少的所有歌手姓名。
Tasks:[{"PythonREPL": "A为40的平方，A的值是多少？"}, {"SQL生成器": "粉丝总数比A少的所有歌手姓名"}]
Answer:蔡依林"""
en_few_shot_demonstrations = """Question: What is the square of the number of albums by Jolin Tsai?
Tasks: [{"SQL生成器": "What is the number of albums by Jolin Tsai?"}, {"PythonREPL": "What is the square of the number of albums by Jolin Tsai?"}]
Answer: The square of the number of albums by Jolin Tsai is 100.

Question: First, calculate the square of 40 and assign it as A, then find the names of all artists with a total number of fans less than A.
Tasks: [{"PythonREPL": "Let A be the square of 40, what is the value of A?"}, {"SQL生成器": "Find the names of all artists with a total number of fans less than A."}]
Answer: Jolin Tsai."""

few_shot_error_feedback_demonstrations = """Question:蔡依林的专辑数量的平方是多少？
Error:无
Tasks:[{"SQL生成器": "蔡依林的专辑数量是多少？"}, {"PythonREPL": "蔡依林的专辑数量的平方是多少？"}]
Answer:蔡依林的专辑数量的平方是100

Question:先计算40的平方记为A，并找到粉丝总数比A少的所有歌手姓名。
Error:无
Tasks:[{"PythonREPL": "A为40的平方，A的值是多少？"}, {"SQL生成器": "粉丝总数比A少的所有歌手姓名"}]
Answer:蔡依林"""
en_few_shot_error_feedback_demonstrations = """Question: What is the square of the number of albums by Jolin Tsai?
Error: None
Tasks: [{"SQL生成器": "What is the number of albums by Jolin Tsai?"}, {"PythonREPL": "What is the square of the number of albums by Jolin Tsai?"}]
Answer: The square of the number of albums by Jolin Tsai is 100.

Question: First, calculate the square of 40 and assign it as A, then find the names of all artists with a total number of fans less than A.
Error: None
Tasks: [{"PythonREPL": "Let A be the square of 40, what is the value of A?"}, {"SQL生成器": "Find the names of all artists with a total number of fans less than A."}]
Answer: Jolin Tsai."""

simplified_few_shot_demonstrations = """Question:蔡依林的专辑数量的平方是多少？
Answer:[{"SQL生成器": "蔡依林的专辑数量是多少？"}, {"PythonREPL": "蔡依林的专辑数量的平方是多少？"}]

Question:先计算40的平方记为A，并找到粉丝总数比A少的所有歌手姓名。
Answer:[{"PythonREPL": "A为40的平方，A的值是多少？"}, {"SQL生成器": "粉丝总数比A少的所有歌手姓名"}]"""
en_simplified_few_shot_demonstrations = """Question: What is the square of the number of albums by Jolin Tsai?
Answer: [{"SQL生成器": "What is the number of albums by Jolin Tsai?"}, {"PythonREPL": "What is the square of the number of albums by Jolin Tsai?"}]

Question: First, calculate the square of 40 and assign it as A, then find the names of all artists with a total number of fans less than A.
Answer: [{"PythonREPL": "Let A be the square of 40, what is the value of A?"}, {"SQL生成器": "Find the names of all artists with a total number of fans less than A."}]"""

#################################
# for bmtools

few_shot_demonstrations_bmtools = """Question:你能帮我搜索《杀死一只知更鸟》的信息，并创建一个关于它主题和对文学的影响的幻灯片演示吗？
Tasks:[{"Bing_search": "搜索《杀死一只知更鸟》的信息，以及它的主题和对文学的影响"}, {"Slides_making": "创建一个关于它主题和对文学的影响的幻灯片演示"}]
Answer:已完成

Question:我想去约塞米蒂国家公园露营。你能推荐一些风景优美的徒步路线，并提供关于公园费用、许可证和可用露营地的信息吗？并且接下来10天内凯纳奥黑的最低温度平均为多少？
Tasks:[{"Bing_search": "搜索关于风景优美的徒步路线、公园费用、许可证和可用露营地的信息，以便去约塞米蒂国家公园露营"}, {"Weather": "接下来10天内凯纳奥黑的最低温度平均为多少？"}]
Answer:已完成"""
en_few_shot_demonstrations_bmtools = """Question: Can you search for information about the book To Kill a Mockingbird and create a slide presentation about its themes and impact on literature?
Tasks: [{"Bing_search": "search for information about the book To Kill a Mockingbird, as well as its themes and impact on literature"}, {"Slides_making": "create a slide presentation about its themes and impact on literature"}]
Answer: Finished.

Question: I want to go camping in Yosemite National Park. Can you recommend some scenic hiking trails, and provide information on park fees, permits, and available campsites? and what is the average of minimum temperature in Kaneohe for the next 10 days?
Tasks: [{"Bing_search": "search for information about scenic hiking trails, park fees, permits, and available campsites, in order to go camping in Yosemite National Park"}, {"Weather": "what is the average of minimum temperature in Kaneohe for the next 10 days?"}]
Answer: Finished."""

few_shot_error_feedback_demonstrations_bmtools = """Question:你能帮我搜索《杀死一只知更鸟》的信息，并创建一个关于它主题和对文学的影响的幻灯片演示吗？
Error:无
Tasks:[{"Bing_search": "搜索《杀死一只知更鸟》的信息，以及它的主题和对文学的影响"}, {"Slides_making": "创建一个关于它主题和对文学的影响的幻灯片演示"}]
Answer:已完成

Question:我想去约塞米蒂国家公园露营。你能推荐一些风景优美的徒步路线，并提供关于公园费用、许可证和可用露营地的信息吗？并且接下来10天内凯纳奥黑的最低温度平均为多少？
Error:无
Tasks:[{"Bing_search": "搜索关于风景优美的徒步路线、公园费用、许可证和可用露营地的信息，以便去约塞米蒂国家公园露营"}, {"Weather": "接下来10天内凯纳奥黑的最低温度平均为多少？"}]
Answer:已完成"""
en_few_shot_error_feedback_demonstrations_bmtools = """Question: Can you search for information about the book To Kill a Mockingbird and create a slide presentation about its themes and impact on literature?
Error: None
Tasks: [{"Bing_search": "search for information about the book To Kill a Mockingbird, as well as its themes and impact on literature"}, {"Slides_making": "create a slide presentation about its themes and impact on literature"}]
Answer: Finished.

Question: I want to go camping in Yosemite National Park. Can you recommend some scenic hiking trails, and provide information on park fees, permits, and available campsites? and what is the average of minimum temperature in Kaneohe for the next 10 days?
Error: None
Tasks: [{"Bing_search": "search for information about scenic hiking trails, park fees, permits, and available campsites, in order to go camping in Yosemite National Park"}, {"Weather": "what is the average of minimum temperature in Kaneohe for the next 10 days?"}]
Answer: Finished."""

simplified_few_shot_demonstrations_bmtools = """Question:你能帮我搜索《杀死一只知更鸟》的信息，并创建一个关于它主题和对文学的影响的幻灯片演示吗？
Answer:[{"Bing_search": "搜索《杀死一只知更鸟》的信息，以及它的主题和对文学的影响"}, {"Slides_making": "创建一个关于它主题和对文学的影响的幻灯片演示"}]

Question:我想去约塞米蒂国家公园露营。你能推荐一些风景优美的徒步路线，并提供关于公园费用、许可证和可用露营地的信息吗？并且接下来10天内凯纳奥黑的最低温度平均为多少？
Answer:[{"Bing_search": "搜索关于风景优美的徒步路线、公园费用、许可证和可用露营地的信息，以便去约塞米蒂国家公园露营"}, {"Weather": "接下来10天内凯纳奥黑的最低温度平均为多少？"}]"""
en_simplified_few_shot_demonstrations_bmtools = """Question: Can you search for information about the book To Kill a Mockingbird and create a slide presentation about its themes and impact on literature?
Answer: [{"Bing_search": "search for information about the book To Kill a Mockingbird, as well as its themes and impact on literature"}, {"Slides_making": "create a slide presentation about its themes and impact on literature"}]

Question: I want to go camping in Yosemite National Park. Can you recommend some scenic hiking trails, and provide information on park fees, permits, and available campsites? and what is the average of minimum temperature in Kaneohe for the next 10 days?
Answer: [{"Bing_search": "search for information about scenic hiking trails, park fees, permits, and available campsites, in order to go camping in Yosemite National Park"}, {"Weather": "what is the average of minimum temperature in Kaneohe for the next 10 days?"}]"""

#################################
# for bmtools_stock

few_shot_demonstrations_bmtools_stock = """Question:在2020年2月3号，IBM, Apple, Microsoft三个公司中的开盘价最高的是多少？
Tasks:[{"PRICE": "在2020年2月3号，IBM, Apple, Microsoft三个公司各自的开盘价"}, {"MAX": "这些开盘价的最高值"}]
Answer:已完成

Question:Apple公司从2015年2月1号到2015年3月1号的开盘价之和为多少？
Tasks:[{"PRICE": "Apple公司从2015年2月1号到2015年3月1号的每日开盘价"}, {"SUM": "这些每日开盘价的总和"}]
Answer:已完成

Question:Google在2013年4月5号的开盘价到收盘价的波动比是多少？
Tasks:[{"PRICE": "Google在2013年4月5号的开盘价和收盘价"}, {"MINUS": "Google在2013年4月5号的开盘价到收盘价的波动"}, {"DIVIDE": "Google在2013年4月5号的开盘价到收盘价的百分比波动"}]
Answer:已完成

Question:在2018年9月13号，Amazon, Netflix, Tencent 三个公司中的最低的收盘价是多少？
Tasks:[{"PRICE": "在2018年9月13号，Amazon, Netflix, Tencent 三个公司各自的收盘价"}, {"MIN": "这些收盘价的最低值"}]
Answer:已完成

Question:阿里巴巴2017年2月的交易量总额相比于2016年2月的交易量总额增加了多少？
Tasks:[{"PRICE": "阿里巴巴2017年2月的每日交易量和2016年2月的每日交易量"}, {"SUM": "阿里巴巴2017年2月的交易量总额和2016年2月的交易量总额"}, {"MINUS": "阿里巴巴2017年2月的交易量总额相比于2016年2月的交易量总额的增加"}]
Answer:已完成"""

few_shot_error_feedback_demonstrations_bmtools_stock = """Question:在2020年2月3号，IBM, Apple, Microsoft三个公司中的开盘价最高的是多少？
Error:无
Tasks:[{"PRICE": "在2020年2月3号，IBM, Apple, Microsoft三个公司各自的开盘价"}, {"MAX": "这些开盘价的最高值"}]
Answer:已完成

Question:Apple公司从2015年2月1号到2015年3月1号的开盘价之和为多少？
Error:无
Tasks:[{"PRICE": "Apple公司从2015年2月1号到2015年3月1号的每日开盘价"}, {"SUM": "这些每日开盘价的总和"}]
Answer:已完成

Question:Google在2013年4月5号的开盘价到收盘价的波动比是多少？
Error:无
Tasks:[{"PRICE": "Google在2013年4月5号的开盘价和收盘价"}, {"MINUS": "Google在2013年4月5号的开盘价到收盘价的波动"}, {"DIVIDE": "Google在2013年4月5号的开盘价到收盘价的百分比波动"}]
Answer:已完成

Question:在2018年9月13号，Amazon, Netflix, Tencent 三个公司中的最低的收盘价是多少？
Error:无
Tasks:[{"PRICE": "在2018年9月13号，Amazon, Netflix, Tencent 三个公司各自的收盘价"}, {"MIN": "这些收盘价的最低值"}]
Answer:已完成

Question:阿里巴巴2017年2月的交易量总额相比于2016年2月的交易量总额增加了多少？
Error:无
Tasks:[{"PRICE": "阿里巴巴2017年2月的每日交易量和2016年2月的每日交易量"}, {"SUM": "阿里巴巴2017年2月的交易量总额和2016年2月的交易量总额"}, {"MINUS": "阿里巴巴2017年2月的交易量总额相比于2016年2月的交易量总额的增加"}]
Answer:已完成"""


#################################
# for update_bmtools_stock

few_shot_demonstrations_update_bmtools_stock = """Question:在2020年2月3号，IBM, Apple, Microsoft三个公司中的开盘价最高的是多少？
Tasks:[{"PRICE": "temp1 = PRICE('type1'='DAILY', 'type2'='open', 'symbol'='IBM', 'date'='2020/02/03')"}, {"PRICE": "temp2 = PRICE('typel'='DAILY', 'type2'='open', 'symbol'='Apple', 'date'='2020/02/03')"}, {"PRICE": "temp3 = PRICE('typel'='DAILY', 'type2'='open', 'symbol'='Microsoft', 'date'='2020/02/03')"}, {"MAX": "temp4 = MAX(temp1, temp2, temp3)"}]
Answer:已完成

Question:Apple公司从2015年2月1号到2015年3月1号的开盘价之和为多少？
Tasks:[{"PRICE": "temp1 = PRICE('type1'='DAILY','type2'='open','symbol'='Apple','date_start'='2015/02/01','date_end'='2015/03/01')"}, {"SUM": "temp2 = SUM(temp1)"}]
Answer:已完成

Question:Google在2013年4月5号的开盘价到收盘价的波动比是多少？
Tasks:[{"PRICE": "temp1 = PRICE('type1'='DAILY','type2'='close','symbol'='Google','date'='2013/04/05')"}, {"PRICE": "temp2 = PRICE('type1'='DAILY','type2'='open','symbol'='Google','date'='2013/04/05')"}, {"MINUS": "temp3 = MINUS(temp1, temp2)"}, {"PRICE": "temp4 = PRICE('type1'='DAILY','type2'='open','symbol'='Google','date'='2013/04/05')"}, {"DIVIDE": "temp5 = DIVIDE(temp3, temp4)"}]
Answer:已完成"""

few_shot_error_feedback_demonstrations_update_bmtools_stock = """Question:在2020年2月3号，IBM, Apple, Microsoft三个公司中的开盘价最高的是多少？
Error:无
Tasks:[{"PRICE": "temp1 = PRICE('type1'='DAILY', 'type2'='open', 'symbol'='IBM', 'date'='2020/02/03')"}, {"PRICE": "temp2 = PRICE('typel'='DAILY', 'type2'='open', 'symbol'='Apple', 'date'='2020/02/03')"}, {"PRICE": "temp3 = PRICE('typel'='DAILY', 'type2'='open', 'symbol'='Microsoft', 'date'='2020/02/03')"}, {"MAX": "temp4 = MAX(temp1, temp2, temp3)"}]
Answer:已完成

Question:Apple公司从2015年2月1号到2015年3月1号的开盘价之和为多少？
Error:无
Tasks:[{"PRICE": "temp1 = PRICE('type1'='DAILY','type2'='open','symbol'='Apple','date_start'='2015/02/01','date_end'='2015/03/01')"}, {"SUM": "temp2 = SUM(temp1)"}]
Answer:已完成

Question:Google在2013年4月5号的开盘价到收盘价的波动比是多少？
Error:无
Tasks:[{"PRICE": "temp1 = PRICE('type1'='DAILY','type2'='close','symbol'='Google','date'='2013/04/05')"}, {"PRICE": "temp2 = PRICE('type1'='DAILY','type2'='open','symbol'='Google','date'='2013/04/05')"}, {"MINUS": "temp3 = MINUS(temp1, temp2)"}, {"PRICE": "temp4 = PRICE('type1'='DAILY','type2'='open','symbol'='Google','date'='2013/04/05')"}, {"DIVIDE": "temp5 = DIVIDE(temp3, temp4)"}]
Answer:已完成"""

# few_shot_demonstrations_update_bmtools_stock = """Question:在2020年2月3号，IBM, Apple, Microsoft三个公司中的开盘价最高的是多少？
# Tasks:[{"PRICE": "temp1 = PRICE('type1'='DAILY', 'type2'='open', 'symbol'='IBM', 'date'='2020/02/03')"}, {"PRICE": "temp2 = PRICE('typel'='DAILY', 'type2'='open', 'symbol'='Apple', 'date'='2020/02/03')"}, {"PRICE": "temp3 = PRICE('typel'='DAILY', 'type2'='open', 'symbol'='Microsoft', 'date'='2020/02/03')"}, {"MAX": "temp4 = MAX(temp1, temp2, temp3)"}]
# Answer:已完成

# Question:Apple公司从2015年2月1号到2015年3月1号的开盘价之和为多少？
# Tasks:[{"PRICE": "temp1 = PRICE('type1'='DAILY','type2'='open','symbol'='Apple','date_start'='2015/02/01','date_end'='2015/03/01')"}, {"SUM": "temp2 = SUM(temp1)"}]
# Answer:已完成

# Question:Google在2013年4月5号的开盘价到收盘价的波动比是多少？
# Tasks:[{"PRICE": "temp1 = PRICE('type1'='DAILY','type2'='close','symbol'='Google','date'='2013/04/05')"}, {"PRICE": "temp2 = PRICE('type1'='DAILY','type2'='open','symbol'='Google','date'='2013/04/05')"}, {"MINUS": "temp3 = MINUS(temp1, temp2)"}, {"PRICE": "temp4 = PRICE('type1'='DAILY','type2'='open','symbol'='Google','date'='2013/04/05')"}, {"DIVIDE": "temp5 = DIVIDE(temp3, temp4)"}]
# Answer:已完成

# Question:在2018年9月13号，Amazon, Netflix, Tencent 三个公司中的最低的收盘价是多少？
# Tasks:[{"PRICE": "temp1 = PRICE('type1'='DAILY', 'type2'='close', 'symbol'='Amazon', 'date'='2018/09/13')"}, {"PRICE": "temp2 = PRICE('typel'='DAILY', 'type2'='close', 'symbol'='Netflix', 'date'='2018/09/13')"}, {"PRICE": "temp3 = PRICE('typel'='DAILY', 'type2'='close', 'symbol'='Tencent', 'date'='2018/09/13')"}, {"MIN": "temp4 = MIN(temp1, temp2, temp3)"}]
# Answer:已完成

# Question:Alibaba 2017年2月的交易量总额相比于2016年2月的交易量总额增加了多少？
# Tasks:[{"PRICE": "temp1 = PRICE('type1'='DAILY','type2'='volume','symbol'='Alibaba','date_start'='2017/02/01','date_end'='2017/02/28')"}, {"SUM": "temp2 = SUM(temp1)"}, {"PRICE": "temp3 = PRICE('type1'='DAILY','type2'='volume','symbol'='Alibaba','date_start'='2016/02/01','date_end'='2016/02/28')"}, {"SUM": "temp4 = SUM(temp3)"}, {"MINUS": "temp3 = MINUS(temp2, temp4)"}]
# Answer:已完成"""

# few_shot_error_feedback_demonstrations_update_bmtools_stock = """Question:在2020年2月3号，IBM, Apple, Microsoft三个公司中的开盘价最高的是多少？
# Error:无
# Tasks:[{"PRICE": "temp1 = PRICE('type1'='DAILY', 'type2'='open', 'symbol'='IBM', 'date'='2020/02/03')"}, {"PRICE": "temp2 = PRICE('typel'='DAILY', 'type2'='open', 'symbol'='Apple', 'date'='2020/02/03')"}, {"PRICE": "temp3 = PRICE('typel'='DAILY', 'type2'='open', 'symbol'='Microsoft', 'date'='2020/02/03')"}, {"MAX": "temp4 = MAX(temp1, temp2, temp3)"}]
# Answer:已完成

# Question:Apple公司从2015年2月1号到2015年3月1号的开盘价之和为多少？
# Error:无
# Tasks:[{"PRICE": "temp1 = PRICE('type1'='DAILY','type2'='open','symbol'='Apple','date_start'='2015/02/01','date_end'='2015/03/01')"}, {"SUM": "temp2 = SUM(temp1)"}]
# Answer:已完成

# Question:Google在2013年4月5号的开盘价到收盘价的波动比是多少？
# Error:无
# Tasks:[{"PRICE": "temp1 = PRICE('type1'='DAILY','type2'='close','symbol'='Google','date'='2013/04/05')"}, {"PRICE": "temp2 = PRICE('type1'='DAILY','type2'='open','symbol'='Google','date'='2013/04/05')"}, {"MINUS": "temp3 = MINUS(temp1, temp2)"}, {"PRICE": "temp4 = PRICE('type1'='DAILY','type2'='open','symbol'='Google','date'='2013/04/05')"}, {"DIVIDE": "temp5 = DIVIDE(temp3, temp4)"}]
# Answer:已完成

# Question:在2018年9月13号，Amazon, Netflix, Tencent 三个公司中的最低的收盘价是多少？
# Error:无
# Tasks:[{"PRICE": "temp1 = PRICE('type1'='DAILY', 'type2'='close', 'symbol'='Amazon', 'date'='2018/09/13')"}, {"PRICE": "temp2 = PRICE('typel'='DAILY', 'type2'='close', 'symbol'='Netflix', 'date'='2018/09/13')"}, {"PRICE": "temp3 = PRICE('typel'='DAILY', 'type2'='close', 'symbol'='Tencent', 'date'='2018/09/13')"}, {"MIN": "temp4 = MIN(temp1, temp2, temp3)"}]
# Answer:已完成

# Question:Alibaba 2017年2月的交易量总额相比于2016年2月的交易量总额增加了多少？
# Error:无
# Tasks:[{"PRICE": "temp1 = PRICE('type1'='DAILY','type2'='volume','symbol'='Alibaba','date_start'='2017/02/01','date_end'='2017/02/28')"}, {"SUM": "temp2 = SUM(temp1)"}, {"PRICE": "temp3 = PRICE('type1'='DAILY','type2'='volume','symbol'='Alibaba','date_start'='2016/02/01','date_end'='2016/02/28')"}, {"SUM": "temp4 = SUM(temp3)"}, {"MINUS": "temp3 = MINUS(temp2, temp4)"}]
# Answer:已完成"""


#################################
# for update_bmtools_stock_expand

few_shot_demonstrations_update_bmtools_stock_expand = few_shot_demonstrations_update_bmtools_stock

few_shot_error_feedback_demonstrations_update_bmtools_stock_expand = few_shot_error_feedback_demonstrations_update_bmtools_stock


#################################
# for bmtools_map

few_shot_demonstrations_bmtools_map = """Question:告诉我北京和上海之间的距离是多少？
Tasks:[{"DISTANCE": "北京和上海之间的距离"}]
Answer:已完成

Question:白宫附近有哪些餐馆？
Tasks:[{"SEARCH": "白宫附近的餐馆"}]
Answer:已完成

Question:清华大学的经纬度是多少？
Tasks:[{"COORDINATE": "清华大学的经纬度"}]
Answer:已完成

Question:从华盛顿到纽约的路线是什么？
Tasks:[{"ROUTE": "从华盛顿到纽约的路线"}]
Answer:已完成

Question:洛杉矶和旧金山之间的距离是多少？
Tasks:[{"DISTANCE": "洛杉矶和旧金山之间的距离"}]
Answer:已完成

Question:悉尼歌剧院在澳大利亚的坐标是多少？
Tasks:[{"COORDINATE": "悉尼歌剧院在澳大利亚的坐标"}]
Answer:已完成

Question:拉斯维加斯和亚利桑那大峡谷之间的最短驾驶路线是什么？
Tasks:[{"ROUTE": "拉斯维加斯和亚利桑那大峡谷之间的最短驾驶路线"}]
Answer:已完成"""

few_shot_error_feedback_demonstrations_bmtools_map = """Question:告诉我北京和上海之间的距离是多少？
Error:无
Tasks:[{"DISTANCE": "北京和上海之间的距离"}]
Answer:已完成

Question:白宫附近有哪些餐馆？
Error:无
Tasks:[{"SEARCH": "白宫附近的餐馆"}]
Answer:已完成

Question:清华大学的经纬度是多少？
Error:无
Tasks:[{"COORDINATE": "清华大学的经纬度"}]
Answer:已完成

Question:从华盛顿到纽约的路线是什么？
Error:无
Tasks:[{"ROUTE": "从华盛顿到纽约的路线"}]
Answer:已完成

Question:洛杉矶和旧金山之间的距离是多少？
Error:无
Tasks:[{"DISTANCE": "洛杉矶和旧金山之间的距离"}]
Answer:已完成

Question:悉尼歌剧院在澳大利亚的坐标是多少？
Error:无
Tasks:[{"COORDINATE": "悉尼歌剧院在澳大利亚的坐标"}]
Answer:已完成

Question:拉斯维加斯和亚利桑那大峡谷之间的最短驾驶路线是什么？
Error:无
Tasks:[{"ROUTE": "拉斯维加斯和亚利桑那大峡谷之间的最短驾驶路线"}]
Answer:已完成"""


#################################
# for centurio

few_shot_demonstrations_centurio = """Question:监控GB关注人员是否离开顺德大良。
Tasks:[{"库管理-创建": "创建布控库"}, {"入库助手-创建": "创建入库任务，往指定的库中上传/批量上传目标对象的图片/特征"}, {"布控-任务管理": "新建布控任务，选择布控库，选择视图源，当GB关注人员离开顺德大良时推送预警，设置完成后提交创建布控任务"}, {"布控-结果查看": "选中查看布控库的告警结果"}]
Answer:已完成

Question:有一张嫌疑车辆图片，想确认嫌疑人。
Tasks:[{"全息档案-档案检索": "上传嫌疑车辆照片进行检索"}, {"全息档案-检索结果": "搜出车辆档案"}, {"全息档案-个人档案详情": "查看嫌疑车辆关联的人档"}]
Answer:已完成"""

few_shot_error_feedback_demonstrations_centurio = """Question:监控GB关注人员是否离开顺德大良。
Error:无
Tasks:[{"库管理-创建": "创建布控库"}, {"入库助手-创建": "创建入库任务，往指定的库中上传/批量上传目标对象的图片/特征"}, {"布控-任务管理": "新建布控任务，选择布控库，选择视图源，当GB关注人员离开顺德大良时推送预警，设置完成后提交创建布控任务"}, {"布控-结果查看": "选中查看布控库的告警结果"}]
Answer:已完成

Question:有一张嫌疑车辆图片，想确认嫌疑人。
Error:无
Tasks:[{"全息档案-档案检索": "上传嫌疑车辆照片进行检索"}, {"全息档案-检索结果": "搜出车辆档案"}, {"全息档案-个人档案详情": "查看嫌疑车辆关联的人档"}]
Answer:已完成"""





""" Prompt Config """

PROMPT_COMPONENT_CONFIG = {
    'zh':{
        '-1': SIMP_1_PROMPT_COMP_TEMPLATE, 
        '0': DATASET_CONSTRAINST_PROMPT_COMP_TEMPLATE, 
        '1': ROLE_PROMPT_COMP_TEMPLATE, 
        '2': TASK_PROMPT_COMP_TEMPLATE, 
        '3': TOOLSET_CONSTRAINST_PROMPT_COMP_TEMPLATE, 
        '4': OUTPUT_CONSTRAINST_PROMPT_COMP_TEMPLATE, 
        '5': DEMO_PROMPT_COMP_TEMPLATE, 
        '6': USER_INST_PROMPT_COMP_TEMPLATE, 
        '7_1': ROLE_TASK_REIT_PROMPT_COMP_TEMPLATE, 
        '7_2': USER_INST_REIT_PROMPT_COMP_TEMPLATE, 
        '8_1': OUTPUT_CONSTRAINST_ERROR_FEEDBACK_PROMPT_COMP_TEMPLATE, 
        '8_2': USER_INST_ERROR_FEEDBACK_PROMPT_COMP_TEMPLATE, 
    },
    'en':{
        '0': EN_DATASET_CONSTRAINST_PROMPT_COMP_TEMPLATE, 
        '1': EN_ROLE_PROMPT_COMP_TEMPLATE, 
        '2': EN_TASK_PROMPT_COMP_TEMPLATE, 
        '3': EN_TOOLSET_CONSTRAINST_PROMPT_COMP_TEMPLATE, 
        '4': EN_OUTPUT_CONSTRAINST_PROMPT_COMP_TEMPLATE, 
        '5': EN_DEMO_PROMPT_COMP_TEMPLATE, 
        '6': EN_USER_INST_PROMPT_COMP_TEMPLATE, 
        '7_1': EN_ROLE_TASK_REIT_PROMPT_COMP_TEMPLATE, 
        '7_2': EN_USER_INST_REIT_PROMPT_COMP_TEMPLATE, 
        '8_1': EN_OUTPUT_CONSTRAINST_ERROR_FEEDBACK_PROMPT_COMP_TEMPLATE, 
        '8_2': EN_USER_INST_ERROR_FEEDBACK_PROMPT_COMP_TEMPLATE, 
    },
}

DELIMITER = '\n\n'

""" Prompt Instance """

#################################
# Basic Prompt Component Combination

baseline_prompt = PromptTemplate(
                        input_variables=["toolset", "question"],
                        template=DELIMITER.join([\
                            PROMPT_COMPONENT_CONFIG['zh']['2'], \
                            PROMPT_COMPONENT_CONFIG['zh']['3'], \
                            PROMPT_COMPONENT_CONFIG['zh']['4'], \
                            PROMPT_COMPONENT_CONFIG['zh']['6'], \
                                ]),
                        )

role_baseline_prompt = PromptTemplate(
                        input_variables=["toolset", "question"],
                        template=DELIMITER.join([\
                            PROMPT_COMPONENT_CONFIG['zh']['1'], \
                            PROMPT_COMPONENT_CONFIG['zh']['2'], \
                            PROMPT_COMPONENT_CONFIG['zh']['3'], \
                            PROMPT_COMPONENT_CONFIG['zh']['4'], \
                            PROMPT_COMPONENT_CONFIG['zh']['6'], \
                                ]),
                        )

baseline_few_shot_prompt = PromptTemplate(
                        input_variables=["toolset", "demonstrations", "question"],
                        template=DELIMITER.join([\
                            PROMPT_COMPONENT_CONFIG['zh']['2'], \
                            PROMPT_COMPONENT_CONFIG['zh']['3'], \
                            PROMPT_COMPONENT_CONFIG['zh']['4'], \
                            PROMPT_COMPONENT_CONFIG['zh']['5'], \
                            PROMPT_COMPONENT_CONFIG['zh']['6'], \
                                ]),
                        )

new_baseline_prompt = PromptTemplate(
                        input_variables=["toolset", "demonstrations", "question"],
                        template=DELIMITER.join([\
                            PROMPT_COMPONENT_CONFIG['zh']['1'], \
                            PROMPT_COMPONENT_CONFIG['zh']['2'], \
                            PROMPT_COMPONENT_CONFIG['zh']['3'], \
                            PROMPT_COMPONENT_CONFIG['zh']['4'], \
                            PROMPT_COMPONENT_CONFIG['zh']['5'], \
                            PROMPT_COMPONENT_CONFIG['zh']['6'], \
                                ]),
                        )

#################################
# Extra Prompt Component Combination

baseline_highlight_prompt = PromptTemplate(
                        input_variables=["toolset", "question"],
                        template=DELIMITER.join([\
                            PROMPT_COMPONENT_CONFIG['zh']['2'], \
                            PROMPT_COMPONENT_CONFIG['zh']['7_1'], \
                            PROMPT_COMPONENT_CONFIG['zh']['3'], \
                            PROMPT_COMPONENT_CONFIG['zh']['4'], \
                            PROMPT_COMPONENT_CONFIG['zh']['7_2'], \
                            PROMPT_COMPONENT_CONFIG['zh']['6'], \
                                ]),
                        )

new_baseline_highlight_prompt = PromptTemplate(
                        input_variables=["toolset", "demonstrations", "question"],
                        template=DELIMITER.join([\
                            PROMPT_COMPONENT_CONFIG['zh']['1'], \
                            PROMPT_COMPONENT_CONFIG['zh']['2'], \
                            PROMPT_COMPONENT_CONFIG['zh']['7_1'], \
                            PROMPT_COMPONENT_CONFIG['zh']['3'], \
                            PROMPT_COMPONENT_CONFIG['zh']['4'], \
                            PROMPT_COMPONENT_CONFIG['zh']['5'], \
                            PROMPT_COMPONENT_CONFIG['zh']['7_2'], \
                            PROMPT_COMPONENT_CONFIG['zh']['6'], \
                                ]),
                        )

baseline_history_prompt = PromptTemplate(
                        input_variables=["toolset", "question", "error"],
                        template=DELIMITER.join([\
                            PROMPT_COMPONENT_CONFIG['zh']['2'], \
                            PROMPT_COMPONENT_CONFIG['zh']['3'], \
                            PROMPT_COMPONENT_CONFIG['zh']['8_1'], \
                            PROMPT_COMPONENT_CONFIG['zh']['8_2'], \
                                ]),
                        )

new_baseline_history_prompt = PromptTemplate(
                        input_variables=["toolset", "demonstrations", "question", "error"],
                        template=DELIMITER.join([\
                            PROMPT_COMPONENT_CONFIG['zh']['1'], \
                            PROMPT_COMPONENT_CONFIG['zh']['2'], \
                            PROMPT_COMPONENT_CONFIG['zh']['3'], \
                            PROMPT_COMPONENT_CONFIG['zh']['8_1'], \
                            PROMPT_COMPONENT_CONFIG['zh']['5'], \
                            PROMPT_COMPONENT_CONFIG['zh']['8_2'], \
                                ]),
                        )

#################################
# Prompt Component Combination Methods

en_baseline_prompt = PromptTemplate(
                        input_variables=["toolset", "question"],
                        template=DELIMITER.join([\
                            PROMPT_COMPONENT_CONFIG['en']['2'], \
                            PROMPT_COMPONENT_CONFIG['en']['3'], \
                            PROMPT_COMPONENT_CONFIG['en']['4'], \
                            PROMPT_COMPONENT_CONFIG['en']['6'], \
                                ]),
                        )

en_new_baseline_prompt = PromptTemplate(
                        input_variables=["toolset", "demonstrations", "question"],
                        template=DELIMITER.join([\
                            PROMPT_COMPONENT_CONFIG['en']['1'], \
                            PROMPT_COMPONENT_CONFIG['en']['2'], \
                            PROMPT_COMPONENT_CONFIG['en']['3'], \
                            PROMPT_COMPONENT_CONFIG['en']['4'], \
                            PROMPT_COMPONENT_CONFIG['en']['5'], \
                            PROMPT_COMPONENT_CONFIG['en']['6'], \
                                ]),
                        )

baseline_order_1_prompt = PromptTemplate(
                        input_variables=["toolset", "question"],
                        template=DELIMITER.join([\
                            PROMPT_COMPONENT_CONFIG['zh']['3'], \
                            PROMPT_COMPONENT_CONFIG['zh']['2'], \
                            PROMPT_COMPONENT_CONFIG['zh']['4'], \
                            PROMPT_COMPONENT_CONFIG['zh']['6'], \
                                ]),
                        )

new_baseline_order_1_prompt = PromptTemplate(
                        input_variables=["toolset", "demonstrations", "question"],
                        template=DELIMITER.join([\
                            PROMPT_COMPONENT_CONFIG['zh']['1'], \
                            PROMPT_COMPONENT_CONFIG['zh']['3'], \
                            PROMPT_COMPONENT_CONFIG['zh']['2'], \
                            PROMPT_COMPONENT_CONFIG['zh']['4'], \
                            PROMPT_COMPONENT_CONFIG['zh']['5'], \
                            PROMPT_COMPONENT_CONFIG['zh']['6'], \
                                ]),
                        )

#################################
# Simplified Prompt Component Combination

simplified_1_prompt = PromptTemplate(
                        input_variables=["toolset", "demonstrations", "question"],
                        template=PROMPT_COMPONENT_CONFIG['zh']['-1'],
                        )



""" Prompt class Definition """

class Prompt_Component_OneStep:
    def __init__(self, prompt_name):
        self.prompt_config = {
            # <<<<<<<<<<<<<<<<<<<<<<<< default >>>>>>>>>>>>>>>>>>>>>>>>
            #################################
            # Basic Prompt Component Combination
            'baseline': 
                {
                    'prompt': baseline_prompt,
                    'inner_kwargs': {
                        'toolset': toolset,
                        },
                    'stop': ['\nAnswer'],
                },
            'role_baseline': 
                {
                    'prompt': role_baseline_prompt,
                    'inner_kwargs': {
                        'toolset': toolset,
                        },
                    'stop': ['\nAnswer'],
                },
            'baseline_few_shot': 
                {
                    'prompt': baseline_few_shot_prompt,
                    'inner_kwargs': {
                        'toolset': toolset,
                        'demonstrations': few_shot_demonstrations,
                        },
                    'stop': ['\nAnswer'],
                },
            'new_baseline': 
                {
                    'prompt': new_baseline_prompt,
                    'inner_kwargs': {
                        'toolset': toolset,
                        'demonstrations': few_shot_demonstrations,
                        },
                    'stop': ['\nAnswer'],
                },
            #################################
            # Extra Prompt Component Combination
            'baseline_highlight': 
                {
                    'prompt': baseline_highlight_prompt,
                    'inner_kwargs': {
                        'toolset': toolset,
                        },
                    'stop': ['\nAnswer'],
                },
            'new_baseline_highlight': 
                {
                    'prompt': new_baseline_highlight_prompt,
                    'inner_kwargs': {
                        'toolset': toolset,
                        'demonstrations': few_shot_demonstrations,
                        },
                    'stop': ['\nAnswer'],
                },
            'baseline_history': 
                {
                    'prompt': baseline_history_prompt,
                    'inner_kwargs': {
                        'toolset': toolset,
                        },
                    'stop': ['\nAnswer'],
                },
            'new_baseline_history': 
                {
                    'prompt': new_baseline_history_prompt,
                    'inner_kwargs': {
                        'toolset': toolset,
                        'demonstrations': few_shot_error_feedback_demonstrations,
                        },
                    'stop': ['\nAnswer'],
                },
                #################################
                # Prompt Component Combination Methods
            'en_baseline': 
                {
                    'prompt': en_baseline_prompt,
                    'inner_kwargs': {
                        'toolset': en_toolset,
                        },
                    'stop': ['\nAnswer'],
                },
            'en_new_baseline': 
                {
                    'prompt': en_new_baseline_prompt,
                    'inner_kwargs': {
                        'toolset': en_toolset,
                        'demonstrations': en_few_shot_demonstrations,
                        },
                    'stop': ['\nAnswer'],
                },
            'baseline_order_1': 
                {
                    'prompt': baseline_order_1_prompt,
                    'inner_kwargs': {
                        'toolset': toolset,
                        },
                    'stop': ['\nAnswer'],
                },
            'new_baseline_order_1': 
                {
                    'prompt': new_baseline_order_1_prompt,
                    'inner_kwargs': {
                        'toolset': toolset,
                        'demonstrations': few_shot_demonstrations,
                        },
                    'stop': ['\nAnswer'],
                },
            #################################
            # Simplified Prompt Component Combination
            'simplified_1': 
                {
                    'prompt': simplified_1_prompt,
                    'inner_kwargs': {
                        'toolset': toolset,
                        'demonstrations': simplified_few_shot_demonstrations,
                        },
                    'stop': ['\nQuestion'],
                },
        }
        
        p_names = list(self.prompt_config)
        # for bmtools
        for p in p_names:
            new_p = p + '_bmtools'
            self.prompt_config[new_p] = deepcopy(self.prompt_config[p])
            if 'toolset' in self.prompt_config[new_p]['inner_kwargs']:
                if self.prompt_config[new_p]['inner_kwargs']['toolset'] == toolset:
                    self.prompt_config[new_p]['inner_kwargs']['toolset'] = toolset_bmtools
                elif self.prompt_config[new_p]['inner_kwargs']['toolset'] == en_toolset:
                    self.prompt_config[new_p]['inner_kwargs']['toolset'] = en_toolset_bmtools
            
            if 'demonstrations' in self.prompt_config[new_p]['inner_kwargs']:
                if self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == few_shot_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = few_shot_demonstrations_bmtools
                elif self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == few_shot_error_feedback_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = few_shot_error_feedback_demonstrations_bmtools
                elif self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == en_few_shot_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = en_few_shot_demonstrations_bmtools
                elif self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == en_few_shot_error_feedback_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = en_few_shot_error_feedback_demonstrations_bmtools
                elif self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == simplified_few_shot_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = simplified_few_shot_demonstrations_bmtools
                elif self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == en_simplified_few_shot_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = en_simplified_few_shot_demonstrations_bmtools
        # for bmtools_stock
        for p in p_names:
            new_p = p + '_bmtools_stock'
            self.prompt_config[new_p] = deepcopy(self.prompt_config[p])
            if 'toolset' in self.prompt_config[new_p]['inner_kwargs']:
                if self.prompt_config[new_p]['inner_kwargs']['toolset'] == toolset:
                    self.prompt_config[new_p]['inner_kwargs']['toolset'] = toolset_bmtools_stock
                elif self.prompt_config[new_p]['inner_kwargs']['toolset'] == en_toolset:
                    self.prompt_config[new_p]['inner_kwargs']['toolset'] = None
            
            if 'demonstrations' in self.prompt_config[new_p]['inner_kwargs']:
                if self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == few_shot_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = few_shot_demonstrations_bmtools_stock
                elif self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == few_shot_error_feedback_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = few_shot_error_feedback_demonstrations_bmtools_stock
                elif self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == en_few_shot_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = None
                elif self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == en_few_shot_error_feedback_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = None
                elif self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == simplified_few_shot_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = None
                elif self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == en_simplified_few_shot_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = None
        # for update_bmtools_stock
        for p in p_names:
            new_p = p + '_update_bmtools_stock'
            self.prompt_config[new_p] = deepcopy(self.prompt_config[p])
            if 'toolset' in self.prompt_config[new_p]['inner_kwargs']:
                if self.prompt_config[new_p]['inner_kwargs']['toolset'] == toolset:
                    self.prompt_config[new_p]['inner_kwargs']['toolset'] = toolset_update_bmtools_stock
                elif self.prompt_config[new_p]['inner_kwargs']['toolset'] == en_toolset:
                    self.prompt_config[new_p]['inner_kwargs']['toolset'] = None
            
            if 'demonstrations' in self.prompt_config[new_p]['inner_kwargs']:
                if self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == few_shot_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = few_shot_demonstrations_update_bmtools_stock
                elif self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == few_shot_error_feedback_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = few_shot_error_feedback_demonstrations_update_bmtools_stock
                elif self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == en_few_shot_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = None
                elif self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == en_few_shot_error_feedback_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = None
                elif self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == simplified_few_shot_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = None
                elif self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == en_simplified_few_shot_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = None
        # for update_bmtools_stock_expand
        for p in p_names:
            new_p = p + '_update_bmtools_stock_expand'
            self.prompt_config[new_p] = deepcopy(self.prompt_config[p])
            if 'toolset' in self.prompt_config[new_p]['inner_kwargs']:
                if self.prompt_config[new_p]['inner_kwargs']['toolset'] == toolset:
                    self.prompt_config[new_p]['inner_kwargs']['toolset'] = toolset_update_bmtools_stock_expand
                elif self.prompt_config[new_p]['inner_kwargs']['toolset'] == en_toolset:
                    self.prompt_config[new_p]['inner_kwargs']['toolset'] = None
            
            if 'demonstrations' in self.prompt_config[new_p]['inner_kwargs']:
                if self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == few_shot_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = few_shot_demonstrations_update_bmtools_stock_expand
                elif self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == few_shot_error_feedback_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = few_shot_error_feedback_demonstrations_update_bmtools_stock_expand
                elif self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == en_few_shot_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = None
                elif self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == en_few_shot_error_feedback_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = None
                elif self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == simplified_few_shot_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = None
                elif self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == en_simplified_few_shot_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = None
        # for bmtools_map
        for p in p_names:
            new_p = p + '_bmtools_map'
            self.prompt_config[new_p] = deepcopy(self.prompt_config[p])
            if 'toolset' in self.prompt_config[new_p]['inner_kwargs']:
                if self.prompt_config[new_p]['inner_kwargs']['toolset'] == toolset:
                    self.prompt_config[new_p]['inner_kwargs']['toolset'] = toolset_bmtools_map
                elif self.prompt_config[new_p]['inner_kwargs']['toolset'] == en_toolset:
                    self.prompt_config[new_p]['inner_kwargs']['toolset'] = None
            
            if 'demonstrations' in self.prompt_config[new_p]['inner_kwargs']:
                if self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == few_shot_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = few_shot_demonstrations_bmtools_map
                elif self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == few_shot_error_feedback_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = few_shot_error_feedback_demonstrations_bmtools_map
                elif self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == en_few_shot_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = None
                elif self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == en_few_shot_error_feedback_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = None
                elif self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == simplified_few_shot_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = None
                elif self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == en_simplified_few_shot_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = None
        # for centurio
        for p in p_names:
            new_p = p + '_centurio'
            self.prompt_config[new_p] = deepcopy(self.prompt_config[p])
            if 'toolset' in self.prompt_config[new_p]['inner_kwargs']:
                if self.prompt_config[new_p]['inner_kwargs']['toolset'] == toolset:
                    self.prompt_config[new_p]['inner_kwargs']['toolset'] = toolset_centurio
                elif self.prompt_config[new_p]['inner_kwargs']['toolset'] == en_toolset:
                    self.prompt_config[new_p]['inner_kwargs']['toolset'] = None
            
            if 'demonstrations' in self.prompt_config[new_p]['inner_kwargs']:
                if self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == few_shot_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = few_shot_demonstrations_centurio
                elif self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == few_shot_error_feedback_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = few_shot_error_feedback_demonstrations_centurio
                elif self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == en_few_shot_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = None
                elif self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == en_few_shot_error_feedback_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = None
                elif self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == simplified_few_shot_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = None
                elif self.prompt_config[new_p]['inner_kwargs']['demonstrations'] == en_simplified_few_shot_demonstrations:
                    self.prompt_config[new_p]['inner_kwargs']['demonstrations'] = None
        
        assert prompt_name in self.prompt_config, f'No prompt_name {prompt_name} in Prompt_Component_OneStep.'
        self.prompt = self.prompt_config[prompt_name]['prompt']
        assert isinstance(self.prompt_config[prompt_name]['stop'], list)
        self._stop = self.prompt_config[prompt_name]['stop']
        self.inner_kwargs = {k: v for k, v in self.prompt_config[prompt_name]['inner_kwargs'].items() if k in self.prompt.input_variables}
        print(f'**** Prompt_Component_OneStep ({prompt_name}) has been successfully initialized ****')
        print(f'**** {len(self.prompt_config)} build_in prompt_names ({list(self.prompt_config)}) ****')
        print(f'**** stop ({self.stop})  ****')
        print(f"**** prompt content\n{self.__call__(**{'question': 'xxxx', 'error': 'xxxx',**self.inner_kwargs})}\n ****")
        # raise Exception()
    
    def __call__(self, **kwargs):
        prompt_kwargs = deepcopy(self.inner_kwargs)
        for k in kwargs:
            if k in self.prompt.input_variables:
                prompt_kwargs[k] = kwargs[k]
        return self.prompt.format(**prompt_kwargs)
    
    @property
    def stop(self):
        return self._stop
