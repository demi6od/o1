import os
import time
import base64
import sys
import json
import requests

PROJECT_DIR = os.path.join(os.path.dirname(__file__), '../..')
sys.path.append(PROJECT_DIR)

from src.utils.utils import read_file, read_dir

moe_url = 'http://10.198.7.37:12039/moe'
g_logs = []
debug = True

def run_turn(input_samp):
    global g_logs
    sample = {
        'messages': input_samp['messages'],
        'debug': debug
    }

    log_str = json.dumps(sample, indent=4, ensure_ascii=False)
    print(f'[+] Input: {log_str}')
    g_logs.append(log_str)

    r = requests.post(moe_url, json=sample, timeout=300)
    response = r.json()
    rsp = response

    log_str = json.dumps(rsp, indent=4, ensure_ascii=False)
    print(f'[+] Output: {log_str}')
    g_logs.append(log_str)

def regression_test():
    in_dir = os.path.join(PROJECT_DIR, 'data', 'moe_regression_test')
    samples = read_dir(in_dir)
    for sample in samples:
        run_turn(sample)
        time.sleep(1)

def run_badcase():
    data_dir = os.path.join(PROJECT_DIR, 'data', 'badcase')
    in_file = os.path.join(data_dir, '信息提取-badcase.txt')
    with open(in_file, 'r', encoding='utf-8') as file:
        test_querys = [line.strip() for line in file if line.strip()]

    for query in test_querys:
        run_turn(query)

    out_file = os.path.join(data_dir, 'results.txt')
    with open(out_file, 'w', encoding='utf-8') as output_file:
        for log in g_logs:
            output_file.write(log + '\n')

def main():
    query = '画一幅山水画'
    # run_turn(query)

    regression_test()

    # run_badcase()
    print('[+] Finish')


if __name__ == '__main__':
    main()
