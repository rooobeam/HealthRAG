import numpy as np
from typing import List, Dict, Tuple, Optional
import os
from FlagEmbedding import BGEM3FlagModel
import asyncio
import pickle


async def initialize_retriever(model_path: str = "bge-m3", index_path: Optional[str] = "data/colbert_index.pkl") -> Dict:
    """在插入或检索之前，初始化检索器"""
    if not os.path.exists(model_path):  # 没有模型，自动下载
        from huggingface_hub import snapshot_download
        snapshot_download(repo_id="BAAI/bge-m3", local_dir=model_path)

    if not os.path.exists(index_path) or os.path.getsize(index_path) == 0:
        print("[LOG] 新建检索器...")
        return {
            'model': BGEM3FlagModel(model_path, use_fp16=True),
            'documents': [],
            'doc_vectors': [],
            'compressed_index': None,
            'compressor': None
        }

    else:
        print("[LOG] 加载检索器index...")
        with open(index_path, 'rb') as f:
            retriever_data = pickle.load(f)
        retriever_data['model'] = BGEM3FlagModel(model_path, use_fp16=True)
        return retriever_data



async def encode_documents(model: BGEM3FlagModel, documents: List[str], batch_size: int = 16) -> List[np.ndarray]:
    """以Colbert形式加密文档"""
    doc_vectors = []
    # print(f"[LOG] Encoding {len(documents)} documents...")
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        output = model.encode(batch, return_colbert_vecs=True)
        doc_vectors.extend([np.array(vec, dtype=np.float32) for vec in output['colbert_vecs']])
    return doc_vectors



async def update_index(retriever_data: Dict, new_documents: List[str], index_path: str) -> Dict:
    """更新索引，同时保存"""
    model = retriever_data['model']
    new_vectors = await encode_documents(model, new_documents)
    retriever_data['doc_vectors'].extend(new_vectors)
    retriever_data['documents'].extend(new_documents)

    save_data = {
        key: value for key, value in retriever_data.items()
        if key != 'model'
    }
    with open(index_path, 'wb') as f:
        pickle.dump(save_data, f)


async def maxsim(query_vec: np.ndarray, doc_vec: np.ndarray) -> float:
    """安全的MaxSim计算"""
    if query_vec.ndim == 1:
        query_vec = query_vec[np.newaxis, :]
    if doc_vec.ndim == 1:
        doc_vec = doc_vec[np.newaxis, :]

    query_norm = query_vec / (np.linalg.norm(query_vec, axis=1, keepdims=True) + 1e-8)
    doc_norm = doc_vec / (np.linalg.norm(doc_vec, axis=1, keepdims=True) + 1e-8)
    sim_matrix = np.dot(query_norm, doc_norm.T)
    return np.sum(np.max(sim_matrix, axis=1))


async def search(retriever_data: Dict, query_text: str, top_k: int = 5) -> List[Tuple[int, float]]:
    """搜索"""
    model = retriever_data['model']
    output = await asyncio.to_thread(
        model.encode,
        query_text,  # 注意：这里传入单个查询
        return_dense=False,
        return_sparse=False,
        return_colbert_vecs=True
    )
    query_vec = output['colbert_vecs'][0]

    scores = []
    for i, doc_vec in enumerate(retriever_data['doc_vectors']):
        score = await maxsim(query_vec, doc_vec)
        scores.append((i, score))

    return sorted(scores, key=lambda x: x[1], reverse=True)[:top_k]


async def main():
    retriever = await initialize_retriever(model_path="bge-m3", index_path="data/colbert_index.pkl")

    documents = [
        "BGE-M3 supports dense, sparse and multi-vector retrieval",
        "ColBERTv2 achieves fine-grained matching with token-level vectors",
        "The missing necklace was found in the dressing room",
        "Pandas are native to central China's mountainous regions"
    ]

    await update_index(retriever, documents, "data/colbert_index.pkl")

    query = "whose necklace was missing?"
    print(f"Query: {query}")
    results = await search(retriever, query)

    for idx, score in results:
        print(f"\nScore: {score:.4f}")
        print(retriever['documents'][idx])


if __name__ == "__main__":
    asyncio.run(main())