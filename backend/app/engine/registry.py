from typing import Dict, Type
from app.nodes.base import BaseNode
from app.nodes.builtin import PromptNode, DelayNode, MergeNode, APIRequestNode


class NodeRegistry:
    def __init__(self) -> None:
        self._nodes: Dict[str, Type[BaseNode]] = {}

    def register(self, node_cls: Type[BaseNode]) -> None:
        self._nodes[node_cls.node_type] = node_cls

    def create(self, node_type: str) -> BaseNode:
        return self._nodes[node_type]()


registry = NodeRegistry()
for cls in [PromptNode, DelayNode, MergeNode, APIRequestNode]:
    registry.register(cls)
