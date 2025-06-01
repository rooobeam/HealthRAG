import re
import tiktoken
from hashlib import md5
from llm import call_llm
from nano_db import upsert_entity
from prompt import PROMPTS
from collections import defaultdict
from utiles import a_upsert_str2already, str_to_dict
from request_key import request_id, API_KEYS
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import asyncio
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

async def handle_extract(response, chunk_hash):
    """
    从大模型返回的原消息中通过正则匹配取出实体、关系
    """

    chunk_entities = []
    chunk_relations = []
    if response:
        lines = response.split('##') # 根据定界符取出一条记录
    else:
        lines=[]
    for line in lines:
        line = re.search(r"\((.*)\)", line)
        if not line:
            continue

        attributes = [item.strip('"') for item in line.group(1).split('<|>')]
        if attributes[0] == "entity" and len(attributes) == 3:
            chunk_entities.append(
                dict(
                    entity_name=attributes[1].strip(),
                    description=attributes[2],
                    source_chunk=chunk_hash,
                )
            )
        elif attributes[0] == "relationship" and len(attributes) == 6:
            chunk_relations.append(
                dict(
                    source=attributes[1].strip(),
                    target=attributes[2].strip(),
                    description=attributes[3].strip(),
                    source_chunk=chunk_hash,
                )
            )
        else:
            continue
    return chunk_entities, chunk_relations


async def extract_chunk(new_chunks, extract_doc_examples, global_config):
    """
    提取文档中的实体和关系
    """
    unsuccessful_chunk_id = [] # 没成功提取的chunk,response为空
    doc_entities = []
    doc_relations = []

    for chunk_hash, chunk in new_chunks.items():
        # 构建prompt
        extract_doc_prompt = PROMPTS["extract"].format(
            input_text=chunk,
            language=global_config["language"],
            entity_types=PROMPTS["DEFAULT_ENTITY_TYPES"],
            tuple_delimiter=PROMPTS["DEFAULT_TUPLE_DELIMITER"],
            completion_delimiter=PROMPTS["DEFAULT_COMPLETION_DELIMITER"],
            record_delimiter=PROMPTS["DEFAULT_RECORD_DELIMITER"],
            examples=extract_doc_examples,
        )
        api_key=API_KEYS[request_id.get()]
        # 调用llm进行提取
        response = await call_llm(
            prompt=extract_doc_prompt,
            model_name=global_config["insert_model_name"],
            api_key=api_key,
            api_url=global_config["api_url"],
        )

        # ---处理llm的响应---
        chunk_entities, chunk_relations = await handle_extract(response, chunk_hash)
        doc_entities.extend(chunk_entities)
        doc_relations.extend(chunk_relations)

        if response:
            await a_upsert_str2already(global_config["already_processed_path"], chunk_hash)
        else:
            print("response is None")
            print(api_key)
            print(chunk_hash)
            unsuccessful_chunk_id.append(chunk_hash)

    merged = defaultdict(lambda: {"description": [], "source_chunk": set()})

    # 第一步：聚合相同 entity_name 的数据
    for entity in doc_entities:
        name = entity["entity_name"]
        merged[name]["description"].append(entity["description"])
        merged[name]["source_chunk"].add(entity["source_chunk"])
    # 第二步：转换格式
    doc_entities = [
        {
            "entity_name": name,
            "description": " ".join(data["description"]),  # 用空格连接所有 description
            "source_chunk": global_config["CHUNK_SEPARATOR"].join(data["source_chunk"])  # 转为列表并去重
        }
        for name, data in merged.items()
    ]

    # ---存储实体节点---
    merged = defaultdict(lambda: {
        "descriptions": [],
        "source_chunk": set(),
        "source": None,
        "target": None
    })
    # 第一步：聚合相同 (source, target) 的关系
    for rel in doc_relations:
        key = (rel["source"], rel["target"])
        merged[key]["descriptions"].append(rel["description"])
        merged[key]["source_chunk"].add(rel["source_chunk"])
        merged[key]["source"] = rel["source"]  # 保留源节点名称
        merged[key]["target"] = rel["target"]  # 保留目标节点名称
    # 第二步：转换格式
    doc_relations = [
        {
            "source": source,
            "target": target,
            "description": " ".join(data["descriptions"]),  # 合并文本描述
            "source_chunk": global_config["CHUNK_SEPARATOR"].join(data["source_chunk"])  # 去重存储
        }
        for (source, target), data in merged.items()
    ]

    await upsert_entity(doc_entities, global_config["entity_db_path"], global_config)

    return doc_entities, doc_relations, unsuccessful_chunk_id


async def query_refinement(query, global_config, task_id:int=0):
    """
    问题优化，包括简单、多跳、模糊问题
    """
    prompt = PROMPTS["query_refinement"].format(query=query)
    response = await call_llm(
        prompt=prompt,
        model_name=global_config["query_model_name"],
        api_url=global_config["api_url"]
    )

    response = await str_to_dict(response)
    if response is None:
        print("response is None")
        raise ValueError
    print(f"[LOG] {response['type']}, 修正后的query：{response['refined_query']}")
    query_ = response['refined_query']

    if not isinstance(query_, list):
        query_ = [query_]

    return query_


async def build_context(query, nodes, edges, chunks):
    entities_context = "\n".join(
        node["name"] + " Description:" + node.get("description")
        for node in nodes
    )

    text_units_context = "\n".join(
        chunk
        for chunk in chunks
    )

    prompt = PROMPTS["rag_answer"].format(
        query=query,
        history=None,
        entities_context=entities_context,
        text_units_context=text_units_context,
        response_type="Multiple Paragraphs",
        examples=PROMPTS["rag_answer_examples"],
    )
    return prompt

async def docs2chks(docs_path:list[str], chunk_size:int, chunk_overlap:int)->dict:
    # chunked docs
    new_chunks = dict()
    for doc_path in docs_path:
        with open(doc_path, "r", encoding="utf-8") as f:
            doc = f.read()
        encoding = tiktoken.encoding_for_model("gpt-4o")
        tokens = encoding.encode(doc)
        doc_id=md5(doc.encode()).hexdigest()
        for index, start in enumerate(
                range(0, len(tokens), chunk_size - chunk_overlap)
        ):
            chunk_content = encoding.decode(tokens[start: start + chunk_size])

            new_chunks[
                md5(chunk_content.encode()).hexdigest()
            ] = {
                "content": chunk_content,
                "length": min(chunk_size, len(tokens) - start),
                "origin_doc": doc_id,
            }
    return new_chunks

async def draw_cm(y_true, y_pred):
    # 计算混淆矩阵
    cm = confusion_matrix(y_true, y_pred)

    # 绘制热力图
    plt.figure(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=["Predicted 0", "Predicted 1"],
                yticklabels=["Actual 0", "Actual 1"])
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.title("Confusion Matrix")
    plt.show()

async def compute_metrics(y_true, y_pred):
    """计算 Accuracy, Precision, Recall, F1"""
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred),
        "recall": recall_score(y_true, y_pred),
        "f1": f1_score(y_true, y_pred)
    }

if __name__ == "__main__":
    # 真实标签和预测标签
    y_true = [1, 0, 1, 1, 0, 1]
    y_pred = [1, 0, 0, 1, 0, 1]
    asyncio.run(draw_cm(y_true, y_pred))