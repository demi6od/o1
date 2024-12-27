import logging
import re
import os
import sys
import requests


logger = logging.getLogger('server_api')

PROJECT_DIR = os.path.join(os.path.dirname(__file__), '../..')
sys.path.append(PROJECT_DIR)

from src.utils.utils import service_api

def o1_parse(content):
    if 'final_answer' not in content:
        out = {
            'task_titles': [],
            'final_answer': content
        }
        return out

    # Regex to extract each task's title and the final answer content
    task_titles = re.findall(r'# (step_\d+)[:：]\n(.*?)\n', content, re.DOTALL)
    final_answer_content = re.search(r'# final_answer[:：]\n(.*)', content, re.DOTALL).group(1)

    task_titles = [task_title[1] for task_title in task_titles]
    task_titles = [remove_prefix(task_title) for task_title in task_titles]
    out = {
        'task_titles': task_titles,
        'final_answer': final_answer_content.strip()
    }
    return out

def remove_prefix(s):
    # This pattern matches any text that starts with "子任务", followed by any characters up to ": "
    return re.sub(r"^子任务.*?:\s*", "", s)

def generate(messages,intent_model,model_url):
    url = f"http://10.121.4.11:8001/chat_complete"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "messages": messages,
        "model_name": intent_model,
        "model_url": model_url
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        out = response.json().get('response')
        return out
    else:
        # print(response.json())
        raise Exception(f"Error: {response.json().get('error')}")

def o1_run(req):
    messages = req['messages']
    out_msg = generate(messages, 'qwen', '103.177.28.206:22222')

    # content = "# step_1:\n子任务1:(Ⅰ) 求序列 {a<sub>n</sub>} 的通项公式\n我们接下来求解序列 \\(\\{a_n\\}\\) 的通项公式。\n\n根据题目给出的条件，我们有：\n\\[ a_{n+1} + S_{n+1} = 1 \\]\n其中，\\( S_{n+1} = a_1 + a_2 + \\cdots + a_n + a_{n+1} \\)，所以可以重写为：\n\\[ a_{n+1} + (S_n + a_{n+1}) = 1 \\]\n也即：\n\\[ S_n + 2a_{n+1} = 1 \\]\n\n于是可以解得：\n\\[ a_{n+1} = \\frac{1 - S_n}{2} \\]\n\n因为已知 \\( a_1 = \\frac{1}{2} \\)，所以：\n\\[ S_1 = \\frac{1}{2} \\]\n\n对于 \\( n = 2 \\)，有：\n\\[ a_2 = \\frac{1 - S_1}{2} = \\frac{1 - \\frac{1}{2}}{2} = \\frac{1}{4} \\]\n\\[ S_2 = a_1 + a_2 = \\frac{1}{2} + \\frac{1}{4} = \\frac{3}{4} \\]\n\n对于 \\( n = 3 \\)，有：\n\\[ a_3 = \\frac{1 - S_2}{2} = \\frac{1 - \\frac{3}{4}}{2} = \\frac{1}{8} \\]\n\\[ S_3 = a_1 + a_2 + a_3 = \\frac{1}{2} + \\frac{1}{4} + \\frac{1}{8} = \\frac{7}{8} \\]\n\n因此，观察到 \\( a_n = \\frac{1}{2^n} \\)。\n\n验证：使用数学归纳法：\n假设对 \\( n = k \\) 时成立，即 \\( a_k = \\frac{1}{2^k} \\)，则\n\\[ S_k = \\frac{1}{2} + \\frac{1}{4} + \\cdots + \\frac{1}{2^k} = 1 - \\frac{1}{2^k} \\]\n\n对于 \\( n = k+1 \\)：\n\\[ a_{k+1} = \\frac{1 - S_k}{2} = \\frac{1 - (1 - \\frac{1}{2^k})}{2} = \\frac{1}{2^{k+1}} \\]\n\n于是，递推成立，因此对任意 \\( n \\), 有 \\( a_n = \\frac{1}{2^n} \\)。\n\n**总结**：\\(\\{a_n\\}\\) 的通项公式为 \\( a_n = \\frac{1}{2^n} \\)。\n\n# step_2:\n子任务2.1: 计算 b<sub>n</sub> 的表达式\n要计算 \\( b_n = \\log_2 a_n \\)，我们已知 \\( a_n = \\frac{1}{2^n} \\)。\n\n所以，\n\n\\[\nb_n = \\log_2 \\left( \\frac{1}{2^n} \\right)\n\\]\n\n根据对数性质，得出：\n\n\\[\nb_n = \\log_2 1 - \\log_2 (2^n) = 0 - n = -n\n\\]\n\n因此，\\( b_n = -n \\)。\n\n# step_3:\n子任务2.2: 计算给定式子的和\n好的，我们现在要计算和式：\n\n\\[\n\\frac{1}{b_1 b_2} + \\frac{1}{b_2 b_3} + \\cdots + \\frac{1}{b_n b_{n+1}}\n\\]\n\n我们已知 \\( b_n = -n \\)，因此可以改写为：\n\n\\[\nb_n = \\log_2 a_n = \\log_2 \\left(\\frac{1}{2^n}\\right) = -n\n\\]\n\n因此：\n\n\\[\n\\frac{1}{b_1 b_2} = \\frac{1}{(-1)(-2)} = \\frac{1}{2}\n\\]\n\n\\[\n\\frac{1}{b_2 b_3} = \\frac{1}{(-2)(-3)} = \\frac{1}{6}\n\\]\n\n一般项为：\n\n\\[\n\\frac{1}{b_k b_{k+1}} = \\frac{1}{(-k)(-(k+1))} = \\frac{1}{k(k+1)}\n\\]\n\n考察整个和式：\n\n\\[\n\\sum_{k=1}^{n} \\frac{1}{k(k+1)}\n\\]\n\n可以用分式拆分方法：\n\n\\[\n\\frac{1}{k(k+1)} = \\frac{1}{k} - \\frac{1}{k+1}\n\\]\n\n因此，和式变为：\n\n\\[\n\\sum_{k=1}^{n} \\left(\\frac{1}{k} - \\frac{1}{k+1}\\right)\n\\]\n\n这是一个望远镜求和，很多项会相互抵消，剩下的部分是：\n\n\\[\n1 - \\frac{1}{n+1} = \\frac{n}{n+1}\n\\]\n\n所以，给定式子的和为：\n\n\\[\n\\frac{n}{n+1}\n\\]\n\n# final_answer：\n在给定问题中，我们需要对序列 \\(\\{a_n\\}\\) 及其相关求和问题进行分析和解决。\n\n### (Ⅰ) 求序列 \\(\\{a_n\\}\\) 的通项公式\n\n给定条件：\n- 序列的元素都是正数。\n- 前 \\(n\\) 项的和为 \\(S_n\\)。\n- 对于任何 \\(n \\in \\mathbb{N}^*\\)，满足 \\(a_{n+1} + S_{n+1} = 1\\)。\n- 初始条件 \\(a_1 = \\frac{1}{2}\\)。\n\n我们从 \\(a_1\\) 开始分析：\n\n1. \\(S_1 = a_1 = \\frac{1}{2}\\)。\n2. 根据关系 \\(a_{n+1} + S_{n+1} = 1\\)，可以写成：\n   \\[\n   a_{n+1} + S_n + a_{n+1} = 1 \\implies 2a_{n+1} + S_n = 1\n   \\]\n3. 通过递推公式可以得到：\n   \\[\n   a_2 = 1 - 2a_1 = 1 - 2 \\times \\frac{1}{2} = \\frac{1}{4}\n   \\]\n\n根据已知条件尝试推出通项公式进行验证：\n\n通过数学归纳法假设，对于 \\(n\\),\n\\[\na_n = \\frac{1}{2^n}\n\\]\n\n验证 \\(n = 1\\) 时成立。\n\n假设对于 \\(n = k\\) 成立：\\(a_k = \\frac{1}{2^k}\\)，那么验证 \\(n = k+1\\) 成立：\n\n\\[\nS_k = \\frac{1}{2} + \\frac{1}{4} + \\cdots + \\frac{1}{2^k} = 1 - \\frac{1}{2^k}\n\\]\n\n递推公式：\n\\[\n2a_{k+1} + (1 - \\frac{1}{2^k}) = 1 \\implies 2a_{k+1} = \\frac{1}{2^k} \\implies a_{k+1} = \\frac{1}{2^{k+1}}\n\\]\n\n因此，\\(\\{a_n\\}\\) 的通项公式为：\n\\[\na_n = \\frac{1}{2^n}\n\\]\n\n### (Ⅱ) 求和问题\n\n定义 \\(b_n = \\log_2 a_n\\)，则有：\n\\[\na_n = \\frac{1}{2^n} \\implies b_n = \\log_2 \\left(\\frac{1}{2^n}\\right) = -n\n\\]\n\n我们需要计算的和为：\n\\[\n\\sum_{k=1}^{n} \\frac{1}{b_k b_{k+1}}\n\\]\n\n带入表达式 \\(b_k = -k\\)，\\(b_{k+1} = -(k+1)\\)，结果变为：\n\\[\n\\sum_{k=1}^{n} \\frac{1}{(-k)(-(k+1))} = \\sum_{k=1}^{n} \\frac{1}{k(k+1)}\n\\]\n\n利用拆分：\n\\[\n\\frac{1}{k(k+1)} = \\frac{1}{k} - \\frac{1}{k+1}\n\\]\n\n于是和式为望远镜求和：\n\\[\n\\sum_{k=1}^{n} \\left( \\frac{1}{k} - \\frac{1}{k+1} \\right) = \\left(1 - \\frac{1}{2}\\right) + \\left(\\frac{1}{2} - \\frac{1}{3}\\right) + \\cdots + \\left(\\frac{1}{n} - \\frac{1}{n+1}\\right)\n\\]\n\n所有中间项相消，最后结果为：\n\\[\n1 - \\frac{1}{n+1} = \\frac{n}{n+1}\n\\]\n\n因此，求和结果为：\n\\[\n\\sum_{k=1}^{n} \\frac{1}{b_k b_{k+1}} = \\frac{n}{n+1}\n\\]\n\n这就是“总任务”的详细解答和步骤。\n"
    o1_dict = o1_parse(out_msg['content'])
    out = {
        'o1_dict': o1_dict,
    }
    return out
