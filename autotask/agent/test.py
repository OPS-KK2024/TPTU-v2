from autotask.prompt.prompt import Prompt
from autotask.llm.sensechat import SenseChat
from autotask.tool import (Echo, PythonREPL)


class TestAgent():
    def __init__(self, config: dict) -> None:
        self.config = config
        self.prompt = Prompt()
        self.action_llm = SenseChat(config)
        self.summary_llm = SenseChat(config)

    def __call__(self, instruction: str) -> None:
        print(f'User Instruction: {instruction}.')

        retry = 10
        results_history = ""
        action_more_info = ""
        while True:
            try:
                action_prompt = self.prompt.system_prompt().format(question=instruction, error=action_more_info)
                action = self.action_llm(action_prompt, stop=['\nAction Result'])
                # TODO: 如果 action_input 产生有误，没办法解决子问题，暂时还没有优化这种情况
                print('ACTION: ', action)
                action = eval(action)
                tool, query = list(action.items())[0]
                assert tool in ("Echo", "PythonREPL")

                # 手动编码执行tool，保证只要action和action input正确，tool的执行一定正确
                if tool == 'Echo':
                    selected_tool = Echo()
                if tool == 'PythonREPL':
                    selected_tool = PythonREPL(self.config)
                action_result = selected_tool(query)
                print('ACTION_RESULT: ', action_result)
                results_history += '\t子问题:' + str(query) + '  该子问题的答案是:' + str(action_result)
                break
                # action_more_info += '\n你已经通过{tool}完成了子任务{query}。请考虑还要不要生成更多tool和query来完成原始的问题{instruction}，如果不需要'.format(tool=tool, query=query, instruction=instruction)
            except Exception as error:
                # action_more_info += '\n你生成的{action}有问题，具体错误为{error}。请考虑生成更合理的Action来完成原始的问题{instruction}'.format(action=action, error=error, instruction=instruction)
                retry -= 1
                continue
        
        final_answer_prompt = self.prompt.final_answer_prompt()
        final_answer = self.summary_llm(final_answer_prompt.format(history=results_history, question=instruction), stop=['\nHistory'])
        print("Final Answer:\033[95m{}\033[0m".format(final_answer))
        print('\n')

