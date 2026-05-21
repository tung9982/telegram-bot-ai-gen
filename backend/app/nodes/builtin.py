import asyncio
import httpx
from .base import BaseNode, ExecutionContext


class PromptNode(BaseNode):
    node_type = "prompt"

    async def execute(self, data, context):
        return {"prompt": data.get("prompt", "")}


class DelayNode(BaseNode):
    node_type = "delay"

    async def execute(self, data, context):
        await asyncio.sleep(float(data.get("seconds", 1)))
        return {"delayed": True}


class MergeNode(BaseNode):
    node_type = "merge"

    async def execute(self, data, context):
        merged = {}
        for _, output in context.node_outputs.items():
            merged.update(output)
        return merged


class APIRequestNode(BaseNode):
    node_type = "api_request"

    async def execute(self, data, context):
        url = data["url"]
        method = data.get("method", "GET")
        async with httpx.AsyncClient(timeout=40) as client:
            resp = await client.request(method, url, json=data.get("body"))
            resp.raise_for_status()
            return {"status_code": resp.status_code, "response": resp.json() if resp.content else {}}
