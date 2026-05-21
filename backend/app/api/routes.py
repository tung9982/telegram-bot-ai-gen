from uuid import uuid4
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.schemas.workflow import ExecutionRequest
from app.engine.executor import executor
from app.services.websocket_manager import ws_manager

router = APIRouter()
_run_tasks: dict[str, asyncio.Task] = {}


def _cleanup_task(run_id: str) -> None:
    _run_tasks.pop(run_id, None)


def _schedule_execution(run_id: str, request: ExecutionRequest) -> None:
    task = asyncio.create_task(
        executor.execute(run_id, request.workflow, request.input_payload),
        name=f"workflow:{run_id}",
    )
    task.add_done_callback(lambda _: _cleanup_task(run_id))
    _run_tasks[run_id] = task


@router.get("/health")
async def health():
    return {"ok": True}


@router.post("/workflows/execute")
async def execute_workflow(request: ExecutionRequest):
    run_id = str(uuid4())
    _schedule_execution(run_id, request)
    return {"run_id": run_id, "status": "queued"}


@router.websocket("/ws/{run_id}")
async def ws_run(websocket: WebSocket, run_id: str):
    await ws_manager.connect(run_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(run_id, websocket)
