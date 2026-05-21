from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class ExecutionContext:
    def __init__(self, run_id: str, input_payload: Dict[str, Any], node_outputs: Dict[str, Dict[str, Any]]):
        self.run_id = run_id
        self.input_payload = input_payload
        self.node_outputs = node_outputs


class BaseNode(ABC):
    node_type: str = "base"

    @abstractmethod
    async def execute(self, data: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        raise NotImplementedError
