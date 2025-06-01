import aiohttp
import json
import asyncio
from openai import OpenAI
import numpy as np
import requests
from request_key import request_id, API_KEYS, key_provider

async def call_llm(
    prompt: str,
    model_name: str,
    api_url: str="https://api.siliconflow.cn/v1/chat/completions",
    api_key: str=None,
    temperature: float = 0.7,
    max_tokens: int = 8192,
    timeout: int = 180,  # 超时控制
    **kwargs
):
    # api_key=API_KEYS[request_id.get()] if api_key is None else api_key
    api_key=await key_provider.provide() if api_key is None else api_key
    print(api_key)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
        **kwargs
    }

    try:
        result = requests.request("POST", api_url, json=payload, headers=headers)
        if result.status_code != 200:
            print(f"result.status_code != 200, {result.text}")
            return None
        result = json.loads(result.text)
        # 更健壮的响应解析
        try:
            return result['choices'][0]['message']['content']
        except (KeyError, IndexError) as e:
            print(f"[ERROR] 解析响应失败: {str(e)}")
            print(f"完整响应: {result}")
            return None
    except asyncio.TimeoutError:
        print(f"[TIMEOUT] 请求超时 (URL: {api_url})")
        return None
    except aiohttp.ClientError as e:
        print(f"[NETWORK] 请求失败: {str(e)}")
        return None
    except json.JSONDecodeError:
        print("[ERROR] 响应不是有效的JSON")
        return None

async def call_embedding(
        input,
        model="netease-youdao/bce-embedding-base_v1",
        api_key=None,
        url="https://api.siliconflow.cn/v1/embeddings",
):
    payload = {
        "input": input,
        "encoding_format": "float",
        "model": model
    }

    api_key=await key_provider.provide() if api_key is None else api_key
    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json"
    }
    response = requests.request("POST", url, json=payload, headers=headers)
    if response.text is None:
        response = requests.request("POST", url, json=payload, headers=headers)
    content=json.loads(response.text)
    if isinstance(content, dict) and content["data"] is not None:
        response_data = content["data"]
    else:
        return None # 外面接收到 None会处理
    embedding_data = response_data[0]["embedding"]
    return np.array(embedding_data)

if __name__ == "__main__":
    prompt = "你是谁"

    r = asyncio.run(
        call_llm(
            prompt=prompt,
            model_name="THUDM/GLM-4-32B-0414",
            api_url="https://api.siliconflow.cn/v1/chat/completions"
        )
    )

    print(r)
    r = asyncio.run(
        call_embedding(
            input=prompt,
        )
    )
    print(r)
