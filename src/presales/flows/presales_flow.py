from uuid import uuid4

from crewai.flow.flow import Flow, start, listen

from presales.state import PresalesState

from presales.integrations.hubspot.client import (
    HubSpotClient
)

from presales.integrations.hubspot.mapper import (
    normalize_company
)

from presales.orchestrator.planner import (
    OrchestratorPlanner
)

from presales.orchestrator.executor import (
    GraphExecutor,
)

from presales.orchestrator.models import (
    ExecutionPlan,
)



class PresalesFlow(Flow[PresalesState]):

    # ==========================================
    # STEP 1: GET COMPANY FROM HUBSPOT
    # ==========================================

    @start()
    def ingest_hubspot(self):

        self.state.workflow_id = str(uuid4())

        client = HubSpotClient()

        response = client.list_companies(limit=100)

        companies = response.get("results", [])

        if not companies:
            raise RuntimeError(
                "No companies found in HubSpot"
            )

        # Temporary: process first company
        company = normalize_company(
            companies[1]
        )

        self.state.hubspot_company_id = (
            company["hubspot_company_id"]
        )

        self.state.lead_data = (
            company["company"]
        )

        self.state.current_stage = "ingested"

        print("\n==============================")
        print("HUBSPOT COMPANY INGESTED")
        print("==============================")

        print(
            f"Workflow ID: "
            f"{self.state.workflow_id}"
        )

        print(
            f"HubSpot ID: "
            f"{self.state.hubspot_company_id}"
        )

        print(
            f"Company: "
            f"{self.state.lead_data['name']}"
        )

        print(
            f"Domain: "
            f"{self.state.lead_data['domain']}"
        )

        return self.state


    # ==========================================
    # STEP 2: ORCHESTRATOR CREATES DAG
    # ==========================================
    @listen(ingest_hubspot)
    def create_execution_plan(self):
        print("\n")
        print("╔══════════════════════════════════════╗")
        print("║       🧠 ORCHESTRATOR               ║")
        print("║       BUILDING EXECUTION PLAN       ║")
        print("╚══════════════════════════════════════╝")

        planner = OrchestratorPlanner()
        plan = planner.create_plan(company=self.state.lead_data)
        self.state.execution_plan = plan.model_dump()
        self.state.orchestrator_decision = (plan.reasoning)

        self.state.current_stage = "plan_created"

        print("\n===== EXECUTION PLAN =====")

        for node in plan.nodes:
            print(
                f"{node.id}"
                f"{node.agent}"
                f"| depends_on="
                f"{node.depends_on}"
            )
        print("=====================")
        return plan

    @listen(create_execution_plan)
    def execute_plan(self):

        print("\n")
        print("========================================")
        print("       ⚙️ STARTING GRAPH EXECUTION")
        print("========================================")

        executor = GraphExecutor()
        plan = ExecutionPlan.model_validate(self.state.execution_plan)
        results = executor.execute(
            plan=plan,
            state=self.state,
        )

        self.state.current_stage = (
            "execution_completed"
        )

        self.state.completed_nodes = list(
            results.keys()
        )

        print("\n")
        print("========================================")
        print("       WORKFLOW EXECUTION COMPLETE")
        print("========================================")

        return results