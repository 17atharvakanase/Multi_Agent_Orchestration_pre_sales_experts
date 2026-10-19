**Overview**

- **Project:** Presales Multi-Agent Orchestrator — a small framework that ingests a lead from HubSpot, uses an LLM-driven orchestrator to build an execution DAG, and runs specialized agent "crews" (research, technology, solution, strategist) to produce a presales recommendation.

**Architecture**

- **Orchestrator:** Builds an execution plan (DAG) using an LLM-based planner and a registry of available agents. See [src/presales/orchestrator/planner.py](src/presales/orchestrator/planner.py) and [src/presales/orchestrator/registry.py](src/presales/orchestrator/registry.py).
- **Execution Engine:** Runs the DAG in layers, executing ready nodes in parallel and producing rich metadata, reports and artifacts. See [src/presales/orchestrator/executor.py](src/presales/orchestrator/executor.py).
- **Agent Crews:** Agent implementations (wrapping crewai) for different responsibilities: research, technology analysis, solution architecture and presales strategy. See the crews under [src/presales/crews/](src/presales/crews/).
- **Integrations:** HubSpot connector for company ingestion and mapping. See [src/presales/integrations/hubspot/client.py](src/presales/integrations/hubspot/client.py) and [src/presales/integrations/hubspot/mapper.py](src/presales/integrations/hubspot/mapper.py).
- **LLM & Auth:** Helpers to obtain tokens and create LLM clients (Databricks integration). See [src/presales/config/llm.py](src/presales/config/llm.py) and [src/presales/llm/](src/presales/llm/).
- **Observability / Reporting:** ExecutionReporter saves per-run JSON, Markdown and HTML reports and agent outputs under `runs/`. See [src/presales/observability/reporter.py](src/presales/observability/reporter.py).
- **UI:** Streamlit app to browse and inspect run artifacts. See [src/presales/ui/app.py](src/presales/ui/app.py).

**Key Files**

- [main.py](main.py) — simple top-level entry.
- [src/presales/main.py](src/presales/main.py) — launches the `PresalesFlow`.
- [src/presales/flows/presales_flow.py](src/presales/flows/presales_flow.py) — high-level flow orchestration (ingest, plan, execute).
- [src/presales/orchestrator/models.py](src/presales/orchestrator/models.py) — data models for ExecutionPlan / ExecutionNode.
- [src/presales/orchestrator/validator.py](src/presales/orchestrator/validator.py) — DAG validation rules.
- [src/presales/crews/](src/presales/crews/) — implementations of `ResearchCrew`, `TechnologyCrew`, `SolutionArchitectCrew`, and `SynthesisCrew`.

**Workflow (end-to-end)**

1. Ingest: The flow calls the HubSpot integration to load a company profile. See `PresalesFlow.ingest_hubspot` in [src/presales/flows/presales_flow.py](src/presales/flows/presales_flow.py).
2. Plan: `OrchestratorPlanner` uses an LLM to analyze the company and available agents, and returns an `ExecutionPlan` (DAG of `ExecutionNode`s). See [src/presales/orchestrator/planner.py](src/presales/orchestrator/planner.py).
3. Validate: (implicit) The orchestrator/validator ensures agent names are known, dependencies are valid and no cycles exist. See [src/presales/orchestrator/validator.py](src/presales/orchestrator/validator.py).
4. Execute: `GraphExecutor` computes node layers, finds ready nodes, runs them in parallel batches (via `ThreadPoolExecutor`), collects outputs and metadata, and handles failures/blocked nodes. See [src/presales/orchestrator/executor.py](src/presales/orchestrator/executor.py).
5. Agent Crews: Each node maps to a crew kick-off (research, technology, solution, strategist). Crews are implemented with `crewai` and use the project's LLM. See [src/presales/crews/](src/presales/crews/).
6. Report: `ExecutionReporter` writes JSON, Markdown and HTML under `runs/<workflow_id>/` and saves agent outputs. See [src/presales/observability/reporter.py](src/presales/observability/reporter.py).
7. Inspect: Use the Streamlit UI to view runs at `src/presales/ui/app.py` (it reads `runs/`).

**Developer Quickstart**

- Requirements: Python >= 3.12, see `pyproject.toml`.
- Environment: create a `.env` with required variables (example):

```
HUBSPOT_ACCESS_TOKEN=...
DATABRICKS_HOST=...
DATABRICKS_CLIENT_ID=...
DATABRICKS_CLIENT_SECRET=...
LLM_PROVIDER=databricks
```

- Run a local flow (ingest → plan → execute):

```
python -m src.presales.main
```

- Quick LLM test (uses `get_llm`):

```
python test_databricks.py
```

- View UI (Streamlit):

```
streamlit run src/presales/ui/app.py
```

**Notes & Considerations**

- The orchestrator relies on an LLM to produce a valid JSON plan. The planner performs a simple JSON clean-up but malformed LLM output will raise.
- Sensitive credentials (HubSpot token, Databricks secrets) must be provided via environment variables or `.env`.
- Agent tasks use the `crewai` framework and expect `agents.yaml`/`tasks.yaml` files inside each crew folder.
- The `runs/` directory stores executions; the Streamlit UI reads these artifacts to present status, outputs and timelines.

**Next steps / Useful commands**

- Run unit tests (if added): `pytest`.
- Regenerate a run and inspect `runs/<workflow_id>/execution.md` or open the Streamlit UI.
- To extend: add new agents to [src/presales/orchestrator/registry.py](src/presales/orchestrator/registry.py) and implement a corresponding crew under `src/presales/crews/`.

---

Generated by an automated project scan. For questions or edits, open the relevant file under `src/presales/`.
