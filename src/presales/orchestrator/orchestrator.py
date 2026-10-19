from pydantic import BaseModel, Field
from typing import Any


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


class Orchestrator:

    def __init__(self, llm):
        self.llm = llm

    def create_plan(
        self,
        company: dict[str, Any],
        agents: list[dict[str, Any]],
    ) -> ExecutionPlan:

        prompt = f"""
You are an enterprise presales workflow orchestrator expert.

Your job is to construct an execution DAG.

COMPANY:
{company}

AVAILABLE AGENTS:
{agents}

Rules:

1. Identify which agents are required.
2. Agents with no dependency on each other should run
   in parallel.
3. If an agent requires another agent's output,
   add that agent to depends_on.
4. DO NOT create unnecessary dependencies.
5. DO NOT create cycles.
6. Every dependency must reference another node.
7. The final plan must be executable.
8. Explain why you selected the dependencies.
"""

        response = self.llm.call(
            prompt
        )

        return ExecutionPlan.model_validate(
            response
        )