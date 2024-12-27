import re
import random
import requests
import base64
import os
import sys
import json
import logging
import pandas as pd
from datetime import datetime
from random import shuffle
import string
from zhon import hanzi
import pytz

logger = logging.getLogger('utils')

PUNC_EN = string.punctuation
PUNC_CN = hanzi.punctuation
PUNC = PUNC_CN + PUNC_EN

class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

def read_args(args=None):
    # Read arguments
    if len(sys.argv) < 2:
        logging.error('[-] Please set params file as first argument')
    with open(sys.argv[1]) as f:
        file_args = json.load(f)
        file_args = DotDict(file_args)

    if args is not None:
        for name, val in args.items():
            file_args[name] = val
    return file_args

def parse_args(args):
    if args.project_dir is None:
        args.project_dir = '../../'

    if args.data_dir is None:
        args.data_dir = os.path.join(args.project_dir, 'data', args.task)

    if args.tool_dir is None:
        args.tool_dir = os.path.join(args.project_dir, 'src', 'agent', 'tools')

    if args.log_prefix is None:
        args.log_prefix = ''

    if args.max_llm_input_tokens is None:
        args.max_llm_input_tokens = 32000

    if args.time_log is None:
        args.time_log = {}

    if args.model_ver is None:
        args.model_ver = args.task
    if args.sub_task is None:
        args.sub_task = ''
    if args.output_dir is None:
        now = datetime.now()
        now_str = str(now).rsplit('.', 1)[0].replace(':', '_').replace(' ', '_')
        args.output_dir = os.path.join(args.project_dir, 'output', args.model_ver, args.sub_task, now_str)
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    if args.working_mode is None:
        args.working_mode = 'plan'
    else:
        assert args.working_mode in ['plan', 'execute']

    # if args.working_mode == 'execute':
    #     args.max_execute_step = args.max_work_step

    if args.debug is None:
        args.debug = True

    args.n_llm_try = 10

    if args.max_gpt_fail is None:
        args.max_gpt_fail = 30

    if args.gpt_vendor is None:
        args.gpt_vendor = 'ms'

    if args.short_mem_capacity is None:
        args.short_mem_capacity = 2
    if args.max_execute_step is None:
        args.max_execute_step = 2
    args.short_mem_capacity = max(args.short_mem_capacity, args.max_execute_step)

    if args.wait_seconds is None:
        args.wait_seconds = 5

    if args.engine is None:
        # args.engine = "SOGOU_FULL"
        args.engine = "BING"

    return args

def find_sublist(lst, pattern):
    if len(pattern) == 0:
        return -1, -1

    start = -1
    end = -1
    for i in range(len(lst)):
        if lst[i:(i + len(pattern))] == pattern:
            start = i
            end = i + len(pattern) - 1
            break
    return start, end

def print_params(model):
    for name, param in model.named_parameters():
        if param.requires_grad:
            logger.info(name)
        else:
            logger.info('no_grad:', name)

def log_config(args, t):
    now = datetime.now()
    args.now = str(now).rsplit('.', 1)[0].replace(':', '_').replace(' ', '_')
    log_name = t + '_' + args.now + '.log'

    handlers = [
        logging.StreamHandler()
    ]
    if t != 'infer':
        handlers.append(logging.FileHandler(os.path.join(args.output_dir, log_name), 'w', encoding='utf-8'))

    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt='%m/%d/%Y %H:%M:%S',
        level=logging.INFO,
        handlers=handlers,
    )

def data_split(tot_data, out_dir, train_ratio=0.95, val_ratio=0.025, is_shuffle=False, save_file=True):
    if is_shuffle:
        shuffle(tot_data)

    tot_len = len(tot_data)
    train_len = int(train_ratio * tot_len)
    val_len = int(val_ratio * tot_len)

    data = {
        'train': tot_data[: train_len],
        'dev': tot_data[train_len: train_len + val_len],
        'test': tot_data[train_len + val_len:]
    }

    if save_file:
        for data_t in ['train', 'dev', 'test']:
            write_file(out_dir, data_t + '.json', data[data_t])
    return data

def cut_sentences(para, lang='cn', drop_empty_line=True, strip=True, deduplicate=False, drop_newline=True):
    '''cut_sentences

    :param para: 输入文本
    :param drop_empty_line: 是否丢弃空行
    :param strip: 是否对每一句话做一次strip
    :param deduplicate: 是否对连续标点去重，帮助对连续标点结尾的句子分句
    :return: sentences: list of str
    '''
    if deduplicate:
        para = re.sub(r"([。！？\!\?])\1+", r"\1", para)

    if lang == 'en':
        from nltk import sent_tokenize
        sents = sent_tokenize(para)
        if strip:
            sents = [x.strip() for x in sents]
        if drop_empty_line:
            sents = [x for x in sents if len(x.strip()) > 0]
        return sents
    else:
        para = re.sub('([。！？\?!])([^”’)\]）】])', r"\1[sep]\2", para)  # 单字符断句符
        para = re.sub('(\.{3,})([^”’)\]）】….])', r"\1[sep]\2", para)  # 英文省略号
        para = re.sub('(\…+)([^”’)\]）】….])', r"\1[sep]\2", para)  # 中文省略号
        para = re.sub('([。！？\?!]|\.{3,}|\…+)([”’)\]）】])([^，。！？\?….])', r'\1\2[sep]\3', para)
        # 如果双引号前有终止符，那么双引号才是句子的终点，把分句符[sep]放到双引号后，注意前面的几句都小心保留了双引号
        # 很多规则中会考虑分号;，但是这里我把它忽略不计，破折号、英文双引号等同样忽略，需要的再做些简单调整即可。
        if drop_newline:
            para = para.replace('\n', '')
        sentences = para.split("[sep]")
        if strip:
            sentences = [sent.strip() for sent in sentences]
        if drop_empty_line:
            sentences = [sent for sent in sentences if len(sent.strip()) > 0]
        return sentences

def remove_punctuation(text):
    translator = str.maketrans('', '', PUNC)
    no_punc = text.translate(translator)
    return no_punc

def remove_whilespace(text, space='\s'):
    return text
    text = str(text)
    match_regex = re.compile(u'[\u4e00-\u9fa5。\.,，:：《》、\(\)（）]{1}[' + space + ']+(?<![a-zA-Z])|\d+ +| +\d+|[a-z A-Z]+')
    should_replace_list = match_regex.findall(text)
    order_replace_list = sorted(should_replace_list, key=lambda i:len(i), reverse=True)
    for i in order_replace_list:
        if i == u' ':
            continue
        new_i = i.strip()
        text = text.replace(i, new_i)
    return text

def read_file(in_file, multi_lines=False, errors='ignore'):
    if multi_lines:
        data = []
        for line in open(in_file, 'r', encoding='UTF-8', errors=errors):
            data.append(json.loads(line))
    else:
        with open(in_file, 'r', encoding='UTF-8', errors=errors) as f:
            data = json.load(f)
    print('[+] Read data:', len(data), in_file)
    return data

def write_file(out_dir, file_name, data, multi_lines=False):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    out_file = os.path.join(out_dir, file_name)
    with open(out_file, 'w', encoding='UTF-8') as f:
        if isinstance(data, dict):
            data_len = len(list(data.values())[0])
        else:
            data_len = len(data)
        print('[+] Save data ' + str(data_len) + ' at', out_file)
        if multi_lines:
            for dict_item in data:
                json_str = json.dumps(dict_item, ensure_ascii=False)
                f.write(json_str + '\n')
        else:
            json.dump(data, f, indent=4, ensure_ascii=False)

def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)

def read_dir(in_dir, file_type='json', multi_lines=False):
    files = [f for f in os.listdir(in_dir) if os.path.isfile(os.path.join(in_dir, f))]
    data = []
    for file in files:
        in_file = os.path.join(in_dir, file)
        if file_type == 'json':
            data += read_file(in_file, multi_lines)
        elif file_type == 'df':
            data += read_df(in_file)
    return data

def read_df(in_file):
    if '~$' in in_file:
        return []

    if '.xls' in in_file:
        print(f'[+] Read excel from {in_file}')
        df_dic = pd.read_excel(in_file, sheet_name=None)
        data = []
        for key, df in df_dic.items():
            print(f'[+] Read sheet {key}: {len(df)}')
            df = df.fillna('')
            data += df.to_dict('records')
    elif '.csv' in in_file:
        print(f'[+] Read csv from {in_file}')
        df = pd.read_csv(in_file)
        df = df.fillna('')
        data = df.to_dict('records')
    else:
        print(f'[-] ERROR: read_df file type error: {in_file}')
        return []
    return data

def write_df(out_dir, file_name, data):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    out_file = os.path.join(out_dir, file_name)
    data_len = len(data)
    print('[+] Save data ' + str(data_len) + ' at', out_file)
    data.to_excel(out_file)

def get_time(time_zone="Asia/Shanghai"):
    tz = pytz.timezone(time_zone)
    now = datetime.now(tz)
    formatted_time = now.strftime("%Y-%m-%d %A %H:%M %p %Z")
    return formatted_time

def download_and_convert_to_base64(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        image_base64 = base64.b64encode(response.content).decode('utf-8')
        return image_base64
    except Exception as e:
        print(f"[-] Download image failed, err={str(e)}, url={url}")
        return url

def generate_rand_id():
    length = 8

    # Define the character set (uppercase + lowercase + digits)
    char_set = string.ascii_letters + string.digits

    # Generate a random string of the specified length
    rand_id = ''.join(random.choice(char_set) for _ in range(length))
    return rand_id

def batchify(samples, batch_size, shuffle=False):
    """ Batchify samples with a batch size """

    if shuffle:
        random.shuffle(samples)

    batch_lst = []
    for i in range(0, len(samples), batch_size):
        batch = samples[i:(i + batch_size)]
        batch_lst.append(batch)

    assert(sum([len(batch) for batch in batch_lst]) == len(samples))
    return batch_lst

def service_api(url, sample, timeout=600):
    try:
        r = requests.post(url, json=sample, timeout=timeout)
        response = r.json()
    except Exception as e:
        err_msg = f'[-] Server error: {str(e)}'
        print(err_msg)
        raise Exception(err_msg)

    if response['status'] != 'OK' or 'response' not in response:
        err_msg = f'[-] Server error: {response["status"]}'
        print(err_msg)
        raise Exception(err_msg)

    resp = response['response']
    return resp

def detect_language(text):
    has_chinese = False
    has_english = False

    for char in text:
        if '\u4e00' <= char <= '\u9fff':
            has_chinese = True
        elif '\u0000' <= char <= '\u007f':
            has_english = True

    if has_chinese and has_english:
        return "mix"
    elif has_chinese:
        return "cn"
    elif has_english:
        return "en"
    else:
        return "other"

def chat2llm(messages):
    start_token = '<|im_start|>'
    end_token = '<|im_end|>'

    llm_str = ''
    for message in messages:
        role = message['role']
        llm_str += (
            f"{start_token}{role}\n"
            f"{message['content']}{end_token}\n"
        )

    llm_str = llm_str + f'{start_token}assistant\n'
    return llm_str

def reindex_search_results(messages):
    last_user_idx = -1
    for idx, message in enumerate(messages):
        if message['role'] == 'user':
            last_user_idx = idx

    previous_turns = messages[:(last_user_idx + 1)]
    last_turn = messages[(last_user_idx + 1):]
    search_res_idx = 1
    for message in last_turn:
        if not (message['role'] == 'tool' and message['name'] == 'web_search'):
            continue

        results = eval(message['content'])
        new_results = []
        for idx, result in enumerate(results):
            if not result.startswith('<|'):
                result = f'<|{search_res_idx}|>: ' + result
                search_res_idx += 1
            new_results.append(result)
        message['content'] = '\n\n'.join(new_results)
    return previous_turns + last_turn




