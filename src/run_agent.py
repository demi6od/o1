import os
import copy
import sys

PROJECT_DIR = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(PROJECT_DIR)

from src.agent.Agent import Agent

def run_sample(agent):
    know_ids = [
        'sh_bank_2_0_0',
    ]

    # query = '写一份上海银行存款和理财服务详细分析报告'
    # query = '请搜索知识库获取上海银行的详细介绍'
    # query = '请介绍上海银行的最新理财产品情况和相关新闻，用python实现理财收益模拟计算，运行个例子并给出计算结果'
    # query = '请搜索最新的电影'
    # query = '![image](http://10.198.7.37:8000/3.jpg) 盘子上有多少小碗?'
    # query = ' 请编程计算第1000个素数。'
    # query = '请搜索这个问题“今天周几”'
    # query = '搜索最近重要的新闻和今天天气'
    query = "Write a bash script that takes a matrix represented as a string with format '[1,2],[3,4],[5,6]' and prints the transpose in the same format."
    # query = '明天凌晨开会'
    # query = '查看明天的日程'
    # query = '明天上午9和王总开会，下午3和李总开会'
    # query = '删除明天跑步活动'
    # query = '取消明天的会议'
    # query = '更新明天跑步活动10点开始'
    # query = '明天晚上10跑步'
    # query = '类型 搜索引擎 专业知识库 代码解释器 画图工具 0  知识百科   需要    需要   不需要  不需要 1  分析解答   需要    需要   不需要  不需要 2  数理逻辑  不需要   不需要    需要  不需要 3  角色扮演  不需要   不需要   不需要  不需要 4  文学创作  不需要   不需要   不需要  不需要 我有这个表格，以及每种类型的样本数量，怎么用python计算工具调用次数？比如10条知识百科就会有10次搜索，10次知识库的工具调用。请举例计算并返回结果。'
    # query = '计算1到100相邻素数之间的平均距离，分析距离分布的标准差，猜测100到200之间素数的数量，并验证结果。'
    # query = '华住会APP和系统显示晚上十点才退房'
    # system_prompt = CHRONOMATE_SYSTEM_PROMPT
    sample = {
        'previous_turns': [],
        'system_prompt': '请尽量用中文来回答。',
        # 'system_prompt': system_prompt,
        'query': query,
        'know_ids': know_ids,
    }
    print(f'[+] Input: {sample}')

    rsp = agent.interact(**sample)
    agent.show_states()
    agent.reset()
    return rsp

def create_agent():
    sys.argv = ['', 'params/agent.json']
    args = {
        'project_dir': PROJECT_DIR,

        # "working_mode": "plan",
        # "working_mode": "execute",

        # 'role': 'engineer',
        # 'role': 'doctor',
        # 'role': 'financial_expert',
        'role': 'open_domain_expert',
        # 'role': 'bank_expert',

        # 'tools': ["web_search", "text2image"],
        # 'tools': ["web_search", "knowledge_retrieval"],
        # 'tools': ["web_search", "python_interpreter"],
        # 'tools': ["web_search", "python_interpreter", "text2image"],
        # 'tools': ["code_agent"],
        # 'tools': ["web_search"],
        'tools': [],
        # 'tools': ["create_booking", "delete_bookings", "get_bookings", "update_booking"],
        # 'tools': ["vqa_agent"],
        # 'tools': ["knowledge_retrieval"],
        # 'tools': ["python_interpreter"],
    }
    agent = Agent(args)
    print(agent.args)
    return agent

def main():
    agent = create_agent()
    out = run_sample(agent)

    print(f'\n[+] Final output: {out}')
    print('[+] Finish')


if __name__ == '__main__':
    main()
