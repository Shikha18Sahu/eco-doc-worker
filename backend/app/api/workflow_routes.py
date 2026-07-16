import os
import uuid
import shutil

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.state.workflow_state import WorkflowState
from app.graph.workflow_graph import build_graph
from app.db.workflow_repository import WorkflowRepository

router = APIRouter()
app_graph = build_graph()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "uploads")
UPLOAD_DIR = os.path.abspath(UPLOAD_DIR)


@router.post("/workflow/start")
async def start_workflow(file: UploadFile = File(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    document_id = f"doc-{uuid.uuid4().hex[:8]}"
    ext = os.path.splitext(file.filename)[-1] or ".png"
    saved_path = os.path.join(UPLOAD_DIR, f"{document_id}{ext}")

    with open(saved_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    workflow_id = f"wf-{uuid.uuid4().hex[:8]}"

    initial_state = WorkflowState(
        workflow_id=workflow_id,
        document_id=document_id,
    )
    # Stash image path in structured_data temporarily so OCRAgent can find it
    initial_state.structured_data["_image_path"] = saved_path

    result = app_graph.invoke(initial_state)

    # Clean the internal _image_path key before returning to client
    structured_data = dict(result["structured_data"])
    structured_data.pop("_image_path", None)

    return {
        "workflow_id": result["workflow_id"],
        "status": result["status"],
        "next_action": result["next_action"],
        "confidence": result["confidence"],
        "structured_data": structured_data,
        "validation_errors": result["validation_errors"],
        "human_review_required": result["human_review_required"],
    }


@router.get("/workflow/{workflow_id}")
def get_workflow(workflow_id: str):
    row = WorkflowRepository.get(workflow_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return row