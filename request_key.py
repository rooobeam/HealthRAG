import contextvars
request_id = contextvars.ContextVar('Id of request')

import asyncio
class KeyProvider:
    def __init__(self, api_keys):
        self.api_keys = api_keys
        self._index = 0
        self._lock = asyncio.Lock()

    async def provide(self):
        async with self._lock:
            # 使用取模运算实现轮询
            key = self.api_keys[self._index %  12]
            self._index += 1
            return key


# 全局实例化 KeyProvider
API_KEYS: tuple = (
                  "your key",  
                   )
key_provider = KeyProvider(API_KEYS)