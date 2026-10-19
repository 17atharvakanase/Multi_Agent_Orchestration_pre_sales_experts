import json

from crewai import Agent, Task, Crew, Process
from presales.config.llm import get_llm

from presales.orchestrator.models import (
    ExecutionPlan,
)

from presales.orchestrator.registry import (
    AGENT_REGISTRY,
)


class OrchestratorPlanner:

    def __init__(self):

        self.llm = get_llm()

        self.agent = Agent(
            role="Enterprise Workflow Orchestrator",

            goal=(
                "Analyze a presales opportunity and "
                "construct the optimal execution DAG "
                "using the available agents."
            ),

            backstory=(
                "You are an expert enterprise AI "
                "orchestrator. You understand agent "
                "capabilities, input/output contracts, "
                "parallel execution, dependencies, "
                "and workflow optimization."
            ),

            llm=self.llm,

            verbose=True,

            allow_delegation=False,
        )

    def create_plan(
        self,
        company: dict,
    ) -> ExecutionPlan:

        task = Task(

            description=f"""
You must create an execution DAG for this
presales opportunity.

COMPANY:

{json.dumps(company, indent=2)}

AVAILABLE AGENTS:

{json.dumps(AGENT_REGISTRY, indent=2)}

RULES:

1. Only use agents from the registry.

2. Identify which agents are actually required.

3. Agents that do not depend on each other's
   outputs should run in parallel.

4. If an agent requires another agent's output,
   create a dependency.

5. Do not create unnecessary dependencies.

6. Do not create cycles.

7. Every dependency must reference a valid
   node ID.

8. The final workflow should lead toward a
   useful presales recommendation.

9. Explain your reasoning.

Return ONLY valid JSON.

Required format:

{{
    "workflow_id": "string",
    "reasoning": "string",
    "nodes": [
        {{
            "id": "research",
            "agent": "company_research",
            "depends_on": []
        }}
    ]
}}
""",

            expected_output=(
                "A valid JSON execution plan "
                "containing workflow_id, reasoning "
                "and nodes."
            ),

            agent=self.agent,
        )

        crew = Crew(
            agents=[self.agent],

            tasks=[task],

            process=Process.sequential,

            verbose=True,
        )

        result = crew.kickoff()

        raw_output = str(result)

        raw_output = self._clean_json(
            raw_output
        )

        try:

            plan_data = json.loads(
                raw_output
            )

        except json.JSONDecodeError as exc:

            raise ValueError(
                "Orchestrator returned invalid JSON.\n\n"
                f"{raw_output}"
            ) from exc

        return ExecutionPlan.model_validate(
            plan_data
        )

    @staticmethod
    def _clean_json(
        output: str,
    ) -> str:

        output = output.strip()

        if "```json" in output:

            output = output.split(
                "```json",
                1
            )[1]

            output = output.split(
                "```",
                1
            )[0]

        elif "```" in output:

            output = output.split(
                "```",
                1
            )[1]

            output = output.split(
                "```",
                1
            )[0]

        return output.strip()