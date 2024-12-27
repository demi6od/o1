import random
import traceback
import os
import sys
import pandas as pd
from tqdm import tqdm

PROJECT_DIR = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(PROJECT_DIR)

from src.agent.Agent import Agent
from src.utils.utils import read_file, write_file


def read_data():
    data_dir = os.path.join(PROJECT_DIR, 'data', 'o1', 'math')
    in_file = os.path.join(data_dir, 'train-00001-of-00005.parquet')
    df = pd.read_parquet(in_file)
    dict_list = df.to_dict(orient="records")
    return dict_list

def create_agent():
    sys.argv = ['', 'params/agent.json']
    args = {
        'debug': False,
        'project_dir': PROJECT_DIR,
        'role': 'open_domain_expert',
        'tools': ['python_interpreter'],
    }
    agent = Agent(args)
    print(agent.args)
    return agent

def main():
    agent = create_agent()

    items = read_data()
    print(len(items))
    items = items[150000:155000]
    for idx, item in enumerate(tqdm(items)):
        del item['messages']
        query = item['problem']
        sample = {
            'previous_turns': [],
            'system_prompt': 'Please try to complete the entire task without asking questions midway.',
            'query': query,
            'know_ids': [],
        }
        print(f'[+] Input {idx}: {sample}')

        try:
            out = agent.interact(**sample)
            item['out'] = out
            agent.show_states()
            print(f'[+] Final output {idx}: {out}')
        except Exception as e:
            print(
                f'[*] agent error:{str(e)}\n'
                f'traceback={traceback.format_exc()}'
            )
            pass

        agent.reset()

        if idx % 200 == 0:
            write_file(agent.args.output_dir, f'out_{idx}.json', items[:(idx + 1)])

    write_file(agent.args.output_dir, f'out_all.json', items)
    print('[+] Finish')


if __name__ == '__main__':
    main()
