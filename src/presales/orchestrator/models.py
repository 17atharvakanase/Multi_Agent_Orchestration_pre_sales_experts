from pydantic import BaseModel, Field


class ExecutionNode(BaseModel):

    id: str

    agent: str

    depends_on: list[str] = Field(
        default_factory=list
    )


class ExecutionPlan(BaseModel):

    workflow_id: str

    reasoning: str

    nodes: list[ExecutionNode]