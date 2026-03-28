from pydantic import BaseModel, Field
from typing import List, Optional


class Decision(BaseModel):
    decision: str = Field(description="What was decided")
    rationale: str = Field(description="Why this was decided")
    owner: Optional[str] = Field(default=None, description="Who owns this decision")


class ActionItem(BaseModel):
    task: str = Field(description="What needs to be done")
    assignee: Optional[str] = Field(default=None, description="Who is responsible")
    deadline: Optional[str] = Field(default=None, description="When it is due")
    priority: Optional[str] = Field(default=None, description="high/medium/low")


class MeetingExtraction(BaseModel):
    summary: str = Field(description="2-3 sentence meeting summary")
    topics: List[str] = Field(description="Main topics discussed")
    decisions: List[Decision]
    action_items: List[ActionItem]
    open_questions: List[str] = Field(
        description="Unresolved questions from the meeting"
    )
    speaker_mapping: dict = Field(
        default_factory=dict,
        description="Map of Speaker N labels to likely real names inferred from context",
    )
