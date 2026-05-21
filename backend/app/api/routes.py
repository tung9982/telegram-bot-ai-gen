from uuid import uuid4
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.schemas.workflow import ExecutionRequest
from app.engine.executor import executor
from app.services.websocket_manager import ws_manager

router = APIRouter()


@router.get("/health")
async def health():
    return {"ok": True}


@router.post("/workflows/execute")
async def execute_workflow(request: ExecutionRequest):
    run_id = str(uuid4())
    outputs = await executor.execute(run_id, request.workflow, request.input_payload)
    return {"run_id": run_id, "outputs": outputs}


@router.websocket("/ws/{run_id}")
async def ws_run(websocket: WebSocket, run_id: str):
    await ws_manager.connect(run_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(run_id, websocket)
