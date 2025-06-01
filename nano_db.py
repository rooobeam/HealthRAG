# https://pypi.org/project/nano-vectordb/
import asyncio
import os.path
from hashlib import md5
from nano_vectordb import NanoVectorDB
from llm import call_embedding
import random


async def upsert_entity(entities, db_path, global_config):
    """
    把KG中的节点保存，后面检索会用到
    """

    if os.path.exists(db_path) and os.path.getsize(db_path) == 0:
        os.remove(db_path)  # 空的json导致解析错误。直接删掉让nanodb再新建一个

    # nano自动增量更新
    db = NanoVectorDB(embedding_dim=global_config["embedding_dim"], storage_file=db_path)

    for entity in entities:
        res = await call_embedding(
            input=entity["entity_name"] + entity["description"],
            model=global_config["emb_model"],
            url=global_config["emb_url"])  # vector由实体名称+描述得到

        if res is not None:
            insert_data = [
                {
                    "__id__": md5(entity["entity_name"].encode()).hexdigest(),
                    "__name__": entity["entity_name"],
                    "__vector__": res
                }
            ]
            db.upsert(insert_data)
        else:
            return

    db.save()  # 不支持上传列表，但是可以多次upsert，最后save


async def query_entity(query: str, db:NanoVectorDB, top_k=10):
    embedding = await call_embedding(query)
    if embedding is None or None in embedding:
        raise ValueError("Invalid embedding returned")
    entities = db.query(embedding, top_k=top_k)
    result = [
        {
            "name": entity['__name__'],
            "metrics": entity['__metrics__']
        }
        for entity in entities
    ]

    return result


async def init():
    db = NanoVectorDB(embedding_dim=768, storage_file="data/entities.json")
    s = "人民"
    res = db.query(await call_embedding(s), top_k=2)
    a = 1


if __name__ == "__main__":
    asyncio.run(init())