from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class NodeStatus(str, Enum):
    IDLE = "idle"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    CANCELED = "canceled"


class WorkflowNode(BaseModel):
    id: str
    type: str
    data: Dict[str, Any] = Field(default_factory=dict)


class WorkflowEdge(BaseModel):
    id: str
    source: str
    target: str


class WorkflowDefinition(BaseModel):
    id: str
    name: str
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExecutionRequest(BaseModel):
    workflow: WorkflowDefinition
    input_payload: Dict[str, Any] = Field(default_factory=dict)


class NodeExecutionUpdate(BaseModel):
    run_id: str
    node_id: str
    status: NodeStatus
    progress: float = 0.0
    message: Optional[str] = None
    output: Optional[Dict[str, Any]] = None
