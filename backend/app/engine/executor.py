import asyncio
from collections import defaultdict
import networkx as nx
from app.schemas.workflow import WorkflowDefinition, NodeStatus
from app.engine.registry import registry
from app.nodes.base import ExecutionContext
from app.services.websocket_manager import ws_manager


class WorkflowExecutor:
    async def execute(self, run_id: str, workflow: WorkflowDefinition, input_payload: dict) -> dict:
        graph = nx.DiGraph()
        node_map = {n.id: n for n in workflow.nodes}
        for node in workflow.nodes:
            graph.add_node(node.id)
        for edge in workflow.edges:
            graph.add_edge(edge.source, edge.target)

        order = list(nx.topological_sort(graph))
        outputs = {}
        deps = defaultdict(list)
        for s, t in graph.edges:
            deps[t].append(s)

        for node_id in order:
            await ws_manager.broadcast(run_id, {"type": "node_status", "nodeId": node_id, "status": NodeStatus.RUNNING})
            node_def = node_map[node_id]
            context_outputs = {dep: outputs.get(dep, {}) for dep in deps[node_id]}
            context = ExecutionContext(run_id, input_payload, context_outputs)
            try:
                result = await registry.create(node_def.type).execute(node_def.data, context)
                outputs[node_id] = result
                await ws_manager.broadcast(run_id, {"type": "node_status", "nodeId": node_id, "status": NodeStatus.SUCCESS, "output": result})
            except Exception as exc:
                await ws_manager.broadcast(run_id, {"type": "node_status", "nodeId": node_id, "status": NodeStatus.ERROR, "message": str(exc)})
                raise
            await asyncio.sleep(0)

        await ws_manager.broadcast(run_id, {"type": "workflow_done", "outputs": outputs})
        return outputs


executor = WorkflowExecutor()
