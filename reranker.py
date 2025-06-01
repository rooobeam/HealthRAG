import asyncio
from FlagEmbedding import LayerWiseFlagLLMReranker
from huggingface_hub import snapshot_download
import os
from typing import Optional


async def initialize_reranker(
        model_path: str,
        repo_id: str = "BAAI/bge-reranker-v2-minicpm-layerwise",
        use_fp16: bool = True,
) -> LayerWiseFlagLLMReranker:
    if not os.path.exists(model_path):
        os.makedirs(model_path, exist_ok=True)
        print(f"Downloading model {repo_id} to {model_path}...")
        snapshot_download(repo_id=repo_id, local_dir=model_path, )

    print(f"Initializing reranker from: {model_path}")
    return LayerWiseFlagLLMReranker(model_path, use_fp16=use_fp16)


async def rerank(
        reranker: LayerWiseFlagLLMReranker,
        documents: list,
        queries: list
):

    # 1. 为每个查询创建查询-文档对
    # 格式: [[query1, doc1], [query1, doc2], ..., [queryN, docM]]
    pairs = [[query, doc] for query in queries for doc in documents]

    # 2. 批量计算所有查询-文档对的分数
    scores = await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: reranker.compute_score(pairs, cutoff_layers=[28])
    )

    # 3. 将分数按文档分组（一个文档对应多个查询的分数）
    doc_score_map = {}
    for (query, doc), score in zip(pairs, scores):
        if doc not in doc_score_map:
            doc_score_map[doc] = []
        doc_score_map[doc].append(score)

    # 4. 计算每个文档的综合得分（这里使用平均分，可根据需求改为max/sum等）
    # 格式: [(doc1, 综合分1), (doc2, 综合分2), ...]
    combined_scores = [
        (doc, sum(doc_scores) / len(doc_scores))  # 平均分
        for doc, doc_scores in doc_score_map.items()
    ]

    # 5. 按综合分降序排序
    ranked_docs = sorted(combined_scores, key=lambda x: -x[1])

    # 返回排序后的文档列表（不含分数）
    return [doc for doc, _ in ranked_docs]


async def main():
    # Configuration
    MODEL_REPO_ID = "BAAI/bge-reranker-v2-minicpm-layerwise"
    LOCAL_MODEL_PATH = "bge-reranker-v2-minicpm-layerwise"  # Customize this path
    USE_FP16 = True

    # Initialize the reranker
    reranker = await initialize_reranker(
        model_path=LOCAL_MODEL_PATH,
        repo_id=MODEL_REPO_ID,
        use_fp16=USE_FP16,
    )

    documents = [
        "Adam Collis is an American filmmaker and actor.",
        " He attended the Duke University from 1986 to 1990 and the University of California, Los Angeles from 2007 to 2010.",
        " He also studied cinema at the University of Southern California from 1991 to 1997.",
        " Collis first work was the assistant director for the Scott Derrickson's short \"Love in the Ruins\" (1995).",
        " In 1998, he played \"Crankshaft\" in Eric Koyanagi's \"Hundred Percent\".",
        "Ed Wood is a 1994 American biographical period comedy-drama film directed and produced by Tim Burton, and starring Johnny Depp as cult filmmaker Ed Wood.",
        " The film concerns the period in Wood's life when he made his best-known films as well as his relationship with actor Bela Lugosi, played by Martin Landau.",
        " Sarah Jessica Parker, Patricia Arquette, Jeffrey Jones, Lisa Marie, and Bill Murray are among the supporting cast.",
        "Tyler Bates (born June 5, 1965) is an American musician, music producer, and composer for films, television, and video games.",
        " Much of his work is in the action and horror film genres, with films like \"Dawn of the Dead, 300, Sucker Punch,\" and \"John Wick.\"",
        " He has collaborated with directors like Zack Snyder, Rob Zombie, Neil Marshall, William Friedkin, Scott Derrickson, and James Gunn.",
        " With Gunn, he has scored every one of the director's films; including \"Guardians of the Galaxy\", which became one of the highest grossing domestic movies of 2014, and its 2017 sequel.",
        " In addition, he is also the lead guitarist of the American rock band Marilyn Manson, and produced its albums \"The Pale Emperor\" and \"Heaven Upside Down\".",
        "Doctor Strange is a 2016 American superhero film based on the Marvel Comics character of the same name, produced by Marvel Studios and distributed by Walt Disney Studios Motion Pictures.",
        " It is the fourteenth film of the Marvel Cinematic Universe (MCU)."," The film was directed by Scott Derrickson, who wrote it with Jon Spaihts and C. Robert Cargill, and stars Benedict Cumberbatch as Stephen Strange, along with Chiwetel Ejiofor, Rachel McAdams, Benedict Wong, Michael Stuhlbarg, Benjamin Bratt, Scott Adkins, Mads Mikkelsen, and Tilda Swinton.",
        " In \"Doctor Strange\", surgeon Strange learns the mystic arts after a career-ending car accident.",
        "Hellraiser: Inferno (also known as Hellraiser V: Inferno) is a 2000 American horror film.",
        " It is the fifth installment in the \"Hellraiser\" series and the first \"Hellraiser\" film to go straight-to-DVD.",
        " It was directed by Scott Derrickson and released on October 3, 2000.",
        " The film concerns a corrupt detective who discovers Lemarchand's box at a crime scene.",
        " The film's reviews were mixed.",
        "Deliver Us from Evil is a 2014 American supernatural horror film directed by Scott Derrickson and produced by Jerry Bruckheimer.",
        " The film is officially based on a 2001 non-fiction book entitled \"Beware the Night\" by Ralph Sarchie and Lisa Collier Cool, and its marketing campaign highlighted that it was \"inspired by actual accounts\".",
    ]

    query = ["what is Scott Derrickson's nationnality?","what is Ed Wood's nationality?"]

    await rerank(reranker, documents, query)


if __name__ == "__main__":
    asyncio.run(main())
