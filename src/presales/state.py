from typing import Any
from pydantic import BaseModel, Field


class PresalesState(BaseModel):

    workflow_id: str = ""

    current_stage: str = "initialized"

    hubspot_company_id: str = ""

    lead_data: dict[str, Any] = Field(
        default_factory=dict
    )

    execution_plan: dict[str, Any] = Field(
        default_factory=dict
    )

    # Orchestrator intelligence
    workflow_type: str | None = None

    orchestrator_decision: dict[str, Any] = Field(
        default_factory=dict
    )


    # Execution graph
    active_nodes: list[str] = Field(
        default_factory=list
    )

    completed_nodes: list[str] = Field(
        default_factory=list
    )

    failed_nodes: list[str] = Field(
        default_factory=list
    )

    # Agent outputs
    research_result: dict[str, Any] = Field(
        default_factory=dict
    )

    technology_result: dict[str, Any] = Field(
        default_factory=dict
    )

    synthesis_result: dict[str, Any] = Field(
        default_factory=dict
    )

    solution_result: dict[str, Any] = Field(
        default_factory=dict
    )

    cost_result: dict[str, Any] = Field(
        default_factory=dict
    )

    validation_result: dict[str, Any] = Field(
        default_factory=dict
    )

    human_feedback: str | None = None

    errors: list[str] = Field(
        default_factory=list
    )

    execution_metadata: dict[str, Any] = Field(
    default_factory=dict
    )
    
    retry_count: int = 0

    revision_count: int = 0