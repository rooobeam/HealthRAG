from healthrag import healthRAG
import asyncio
from operate import call_llm

async def main():

    rag = healthRAG(
        doc_json_path="data/docs.json", 
        chunk_json_path="data/chunks.json",
        api_url="https://api.siliconflow.cn/v1/chat/completions",
        insert_model_name="Qwen/Qwen3-8B",
        query_model_name="Qwen/Qwen3-32B",
        entity_db_path="data/entities.json",
        graph_path="data/graph.graphml",
    )

    test_path="data/test.json"
    await rag.evaluate(test_path)
    await rag.evaluate_llmonly(test_path)

if __name__ == "__main__":
    asyncio.run(main())

