from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class WorkflowStatus(str, Enum):
    RECEIVED = "received"
    CHECKING_QUALITY = "checking_quality"
    RUNNING_OCR = "running_ocr"
    EXTRACTING = "extracting"
    VALIDATING = "validating"
    SCORING_CONFIDENCE = "scoring_confidence"
    DECIDING = "deciding"
    APPROVED = "approved"
    AWAITING_USER_INPUT = "awaiting_user_input"
    ESCALATED = "escalated"
    FAILED = "failed"


class NextAction(str, Enum):
    APPROVE = "approve"
    RETRY_OCR = "retry_ocr"
    ASK_USER = "ask_user"
    ESCALATE = "escalate"
    NONE = "none"


class HistoryEntry(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent: str
    input_summary: str
    output_summary: str
    decision: Optional[str] = None
    confidence: Optional[float] = None
    duration_ms: Optional[float] = None
    error: Optional[str] = None


class WorkflowState(BaseModel):
    workflow_id: str
    document_id: str

    status: WorkflowStatus = WorkflowStatus.RECEIVED
    current_step: str = "received"

    retry_count: int = 0
    max_retries: int = 1

    raw_ocr_text: Optional[str] = None
    structured_data: dict[str, Any] = Field(default_factory=dict)

    confidence: Optional[float] = None
    validation_errors: list[str] = Field(default_factory=list)

    next_action: NextAction = NextAction.NONE
    human_review_required: bool = False

    history: list[HistoryEntry] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def add_history(self, entry: HistoryEntry) -> None:
        self.history.append(entry)
        self.updated_at = datetime.utcnow()