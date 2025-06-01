import json
from pathlib import Path
import pickle
import os

async def a_upsert_json(file_path:str, new_inf:dict):

    # 确保文件存在（若不存在则创建空字典）
    path = Path(file_path)
    if not path.exists():
        with open(path, "w", encoding="utf-8") as f:
            json.dump({}, f)  # 初始化空 JSON 文件

    # 读取json
    try:
        with open(path, "r", encoding="utf-8") as f:
            record = json.load(f)
    except json.JSONDecodeError:
        # 处理文件内容非法的情况（如空文件或损坏）
        record = {}

    # update
    record.update(new_inf)

    # 写入
    with open(path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=4, ensure_ascii=False)  # 保持美观格式

async def a_upsert_str2already(file_path:str, processed_chk_id:str):
    # processed_chk_id提取了的chunk的hash id
    already_path = Path(file_path)

    # 异步检查文件是否存在
    if not already_path.exists():
        with open(already_path, "wb") as f:
            pickle.dump(set(), f)  # 异步初始化空文件

    try:
        # 异步读取文件
        with open(already_path, "rb") as f:
            content = f.read()
            already = pickle.loads(content) if content else {}
    except (EOFError, pickle.UnpicklingError):
        already = set()

    # 更新数据
    already.add(processed_chk_id)

    # 异步写入更新
    with open(already_path, "wb") as f:
        pickle.dump(already, f)

def load_already_chunks(already_path:str)->set:
    # set{id}路径
    # 加载已处理chunks
    if os.path.exists(already_path):
        with open(already_path, 'rb') as f:
            content = f.read()
            already_processed = pickle.loads(content) if content else set()
    else:
        already_processed = set()

    return already_processed

# load json file
async def a_load_json_file(file_path:str):
    if not os.path.exists(file_path):
        print("json不存在,返回空字典")
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        content = json.load(f)
    return content

# load str to dict
async def str_to_dict(s:str):
    if s is None:return None
    s=s.strip()
    s=s.lstrip()
    try:
        return json.loads(s)
    except json.JSONDecodeError as e:
        print(f"解析失败: {e}, 字符串为“{s}”")
        return None