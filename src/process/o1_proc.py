import os
import sys
import re
from tqdm import tqdm

import pandas as pd

PROJECT_DIR = os.path.join(os.path.dirname(__file__), '../..')
sys.path.append(PROJECT_DIR)

from src.utils.utils import write_file, read_file, read_dir

def merge_o1():
    in_dir = os.path.join(PROJECT_DIR, 'data', 'o1', 'NuminaMath-CoT', 'raw_2')
    data = read_dir(in_dir)
    no_out = 0
    samples = []
    for item in tqdm(data):
        out = item.get('out', None)
        if out is None:
            no_out += 1
            # print(item)
            continue

        sub_tasks = out['sub_tasks']
        o1_rsp = ''
        for idx, sub_task_dict in enumerate(sub_tasks):
            sub_task = sub_task_dict['sub_task']
            result = sub_task_dict['result']
            o1_rsp += (
                f"# step_{idx + 1}:\n"
                f"{sub_task}\n"
                f"{result}\n"
                f"\n"
            )
        final_answer = '# final_answer' + out['rsp'].split('[最终结果]')[-1]
        o1_rsp += final_answer
        item['o1_rsp'] = o1_rsp
        samples.append(item)

    print(f'no_out = {no_out}')

    out_dir = os.path.join(PROJECT_DIR, 'data', 'o1', 'NuminaMath-CoT', 'clean_2')
    write_file(out_dir, 'o1_sft.json', samples)


def main():
    merge_o1()

    print('[+] Finish')


if __name__ == '__main__':
    main()
