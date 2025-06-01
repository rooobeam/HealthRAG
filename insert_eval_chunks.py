import os
import re
import asyncio
import json
from typing import List, Dict, Union
from llm import call_llm
from prompt import PROMPTS
from healthrag import healthRAG

async def main():

    rag = healthRAG(
        chunk_size=1024, 
        chunk_overlap=40, 
        doc_json_path="data/docs.json",
        chunk_json_path="data/chunks.json", 
        api_url="https://api.siliconflow.cn/v1/chat/completions",
        insert_model_name="Qwen/Qwen3-8B",
        query_model_name="Qwen/Qwen3-8B",
        entity_db_path="data/entities.json",
        graph_path="data/graph.graphml",
    )

    await rag.insert_chunks("data/yun_wei/corpus.json")

if __name__ == "__main__":
    asyncio.run(main())
