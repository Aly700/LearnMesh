from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.models.content import ContentKind
from app.schemas.content import ContentSummaryRead


class ProgressStatus(str, Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"


class ProgressUpsert(BaseModel):
    content_type: ContentKind
    content_id: int = Field(ge=1)
    status: ProgressStatus


class ProgressRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    content_type: str
    content_id: int
    status: str
    updated_at: datetime


class ProgressListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    content_type: str
    content_id: int
    status: str
    updated_at: datetime
    content: ContentSummaryRead
