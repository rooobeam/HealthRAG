# https://networkx.org/documentation/stable/tutorial.html
import asyncio

import networkx as nx
import os
import itertools


async def init_graph(graph_path):
    if not os.path.exists(graph_path) or os.path.getsize(graph_path) == 0:
        G = nx.Graph()
    else:
        G = nx.read_graphml(graph_path)
    return G


async def load_graph(graph_path):
    if not os.path.exists(graph_path) or os.path.getsize(graph_path) == 0:
        return None
    G = nx.read_graphml(graph_path) 
    return G


async def save_graph(G, graph_path):
    os.makedirs(os.path.dirname(graph_path), exist_ok=True) 
    nx.write_graphml(G, graph_path)


async def update_graph(G, doc_entities, doc_relations, CHUNK_SEPARATOR):
    """
    生成或更新知识图谱（节点/边必须包含所有字段，否则跳过）
    """

    # 定义节点和边的必填字段
    REQUIRED_NODE_FIELDS = {"entity_name", "description"}  # 节点的必填字段
    REQUIRED_EDGE_FIELDS = {"source", "target", "description", "source_chunk"}  # 边的必填字段

    # 添加关系边（仅当包含所有必填字段时）
    for entity in doc_entities:
        # 检查是否包含所有必填字段
        if not REQUIRED_NODE_FIELDS.issubset(entity.keys()):
            raise ValueError
        # 检查字段值是否非空（None 或 "" 视为无效）
        if any(not entity[field] for field in REQUIRED_NODE_FIELDS):
            raise ValueError

        node_name = entity["entity_name"]
        new_description = entity["description"]
        new_source_chunk = entity["source_chunk"]

        # 检查节点是否存在
        if G.has_node(node_name):
            # 合并description
            existing_desc = G.nodes[node_name].get("description", "")
            merged_desc = f"{existing_desc} {new_description}".strip()

            # 合并 source_chunk 并转为字符串
            existing_chunks = G.nodes[node_name].get("source_chunk", "")
            merged_set = set(existing_chunks.split(CHUNK_SEPARATOR)) | {new_source_chunk}
            merged_chunks = CHUNK_SEPARATOR.join(merged_set)

            G.nodes[node_name].update({
                "description": merged_desc,
                "source_chunk": merged_chunks  # 存储为字符串
            })
        else:
            # 添加新节点，属性初始化为列表
            G.add_node(node_name, description=new_description, source_chunk=new_source_chunk)

    for relation in doc_relations:
        # 检查必填字段和值...
        # 检查是否包含所有必填字段
        if not REQUIRED_EDGE_FIELDS.issubset(relation.keys()):
            raise ValueError
        # 提取source, target, attrs...

        source = relation["source"]
        target = relation["target"]
        new_description = relation["description"]
        new_source_chunk = relation["source_chunk"]

        # 检查边是否存在
        if G.has_edge(source, target):
            # 合并description
            existing_desc = G.edges[source, target].get("description", "")
            merged_desc = f"{existing_desc} {new_description}".strip()

            # 合并 source_chunk 并转为字符串
            existing_chunks = G.edges[source, target].get("source_chunk", "")
            merged_set = set(existing_chunks.split(CHUNK_SEPARATOR)) | {new_source_chunk}
            merged_chunks = CHUNK_SEPARATOR.join(merged_set)

            G.edges[source, target].update({
                "description": merged_desc,
                "source_chunk": merged_chunks  # 存储为字符串
            })
        else:
            # 添加新边，属性初始化为列表
            G.add_edge(source, target, description=new_description, source_chunk=new_source_chunk)


async def get_graph_data(G, nodes):
    """
    检查传入节点之间的直接关系，返回节点信息、边信息和相关source_chunk
    """

    if len(nodes) == 0:
        print("[WRONG] 没有要查的关键词")
        return [], [], []

    # 结果数据
    unique_nodes = []
    unique_edges = []

    # 先收集所有节点信息
    nodes_seen = set()
    for node in nodes:
        if node not in G:
            continue  # 跳过图中不存在的节点

        if node not in nodes_seen:
            nodes_seen.add(node)
            unique_nodes.append({
                "name": node,
                **G.nodes[node]
            })

    # 收集所有结点所在边的源chunks，这里可以考虑取结点源chunks
    # source_chunks = {data["source_chunk"] for u, v, data in G.edges(data=True) if u in nodes_seen or v in nodes_seen}
    source_chunks = {
        chunk_id
        for data in (
            data
            for u, v, data in G.edges(data=True)
            if u in nodes_seen or v in nodes_seen
        )
        for chunk_id in data["source_chunk"].split("||")  # 用分隔符拆分
    }

    # 转换为列表形式
    source_chunk_list = list(source_chunks)
    # print(unique_nodes, unique_edges, source_chunk_list)
    return unique_nodes, unique_edges, source_chunk_list

async def main():
    q = ["Mme. Loisel(person)", "The Ministry(organization)"]
    G = await init_graph("data/graph.graphml")
    await get_graph_data(G, q)


if __name__ == "__main__":
    asyncio.run(main())
