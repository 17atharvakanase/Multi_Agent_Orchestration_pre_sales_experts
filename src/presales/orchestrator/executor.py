from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any
from presales.observability.reporter import (
    ExecutionReporter,
)
from presales.orchestrator.models import (
    ExecutionPlan,
    ExecutionNode,
)
from datetime import datetime, timezone
from presales.crews.research.crew import ResearchCrew
from presales.crews.technology.crew import TechnologyCrew
from presales.crews.strategist.crew import SynthesisCrew
from presales.crews.solution.crew import SolutionArchitectCrew


class GraphExecutor:

    def __init__(self):

        # ==========================================
        # AGENT REGISTRY
        # ==========================================

        self.agent_runners = {

            "company_researcher":
                self.run_research,

            "technology_analyst":
                self.run_technology,

            "solution_architect":
                self.run_solution_architect,

            "presales_strategist":
                self.run_strategy,
        }

    # ==================================================
    # MAIN EXECUTION LOOP
    # ==================================================
    def calculate_layers(self,plan: ExecutionPlan,):

         # ------------------------------------------
        # Build node lookup
        # ------------------------------------------

        node_map = {
            node.id: node
            for node in plan.nodes
        }

        layers = {}

        # ------------------------------------------
        # Recursively determine node layer
        # ------------------------------------------

        def get_layer(
            node_id: str,
            visiting: set[str] | None = None,
        ) -> int:

            if visiting is None:
                visiting = set()

            # --------------------------------------
            # Cycle detection
            # --------------------------------------

            if node_id in visiting:

                raise RuntimeError(
                    f"Cycle detected in DAG at node: "
                    f"{node_id}"
                )

            # --------------------------------------
            # Already calculated
            # --------------------------------------

            if node_id in layers:
                return layers[node_id]

            # --------------------------------------
            # Validate node
            # --------------------------------------

            if node_id not in node_map:

                raise RuntimeError(
                    f"Node '{node_id}' does not exist "
                    f"in the execution plan."
                )

            node = node_map[node_id]

            # Add current node to recursion path
            visiting = visiting | {node_id}

            # --------------------------------------
            # No dependencies = Layer 1
            # --------------------------------------

            if not node.depends_on:

                layers[node_id] = 1

                return 1

            # --------------------------------------
            # Validate dependencies
            # --------------------------------------

            dependency_layers = []

            for dependency in node.depends_on:

                if dependency not in node_map:

                    raise RuntimeError(
                        f"Node '{node_id}' depends on "
                        f"unknown node '{dependency}'."
                    )

                dependency_layer = get_layer(
                    dependency,
                    visiting,
                )

                dependency_layers.append(
                    dependency_layer
                )

            # --------------------------------------
            # Current layer is one greater than the
            # deepest dependency
            # --------------------------------------

            current_layer = (
                max(dependency_layers) + 1
            )

            layers[node_id] = current_layer

            return current_layer

        # ------------------------------------------
        # Calculate every node
        # ------------------------------------------

        for node in plan.nodes:

            get_layer(node.id)

        return layers
    
    def execute(self,plan: ExecutionPlan,state,):

        workflow_started_at = datetime.now(
            timezone.utc
        )

        print("\n")
        print("========================================")
        print("          GRAPH EXECUTOR")
        print("========================================")

        completed = set()
        failed = set()
        blocked = set()

        results = {}

        total_nodes = len(plan.nodes)

        # ------------------------------------------
        # Calculate DAG layers
        # ------------------------------------------

        layers = self.calculate_layers(plan)

        print(
            f"Total nodes: {total_nodes}"
        )

        print("\nExecution Layers:")

        for node_id, layer in layers.items():

            print(
                f"  Layer {layer}: {node_id}"
            )

        # ------------------------------------------
        # Execution metadata
        # ------------------------------------------
        current_layer = 0
        execution_metadata = {
            "workflow_id": getattr(
                state,
                "workflow_id",
                "",
            ),

            "status": "running",
            "current_layer": 0,
            "current_nodes": [],
            "layers": {},
            "nodes": {},
            "started_at":
                workflow_started_at.isoformat(),

            "completed_at": None,

            "duration_seconds": None,
            "total_nodes": total_nodes,
            "failed_nodes": [],
            "blocked_nodes": [],
            "completed_nodes": [],
            "execution_order": [],
            "parallel_batches": [],
        }

        # ------------------------------------------
        # Build layer metadata
        # ------------------------------------------

        for node_id, layer in layers.items():

            if layer not in execution_metadata[
                "layers"
            ]:

                execution_metadata[
                    "layers"
                ][layer] = []

            execution_metadata[
                "layers"
            ][layer].append(node_id)

        # ==================================================
        # KEEP EXECUTING UNTIL EVERYTHING IS RESOLVED
        # ==================================================

        while (
            len(completed)
            + len(failed)
            + len(blocked)
            < total_nodes
        ):

            # ------------------------------------------
            # STEP 1
            # Find blocked nodes
            # ------------------------------------------

            blocked_nodes = (
                self.get_blocked_nodes(
                    plan=plan,
                    completed=completed,
                    failed=failed,
                    blocked=blocked,
                )
            )

            for node in blocked_nodes:

                blocked.add(node.id)

                blocked_time = datetime.now(
                    timezone.utc
                )

                results[node.id] = {
                    "status": "blocked",

                    "agent": node.agent,

                    "error": (
                        "One or more dependencies "
                        "failed or were blocked."
                    ),

                    "dependencies":
                        list(node.depends_on),

                    "layer":
                        layers[node.id],

                    "blocked_at":
                        blocked_time.isoformat(),
                }

                # --------------------------------------
                # Metadata
                # --------------------------------------

                execution_metadata[
                    "nodes"
                ][node.id] = results[node.id]

                execution_metadata[
                    "execution_order"
                ].append(node.id)

                print("\n")

                print(
                    f"⛔ BLOCKED: {node.id}"
                )

                print(
                    f"   Agent: {node.agent}"
                )

                print(
                    f"   Layer: {layers[node.id]}"
                )

                print(
                    f"   Dependencies: "
                    f"{node.depends_on}"
                )

            # ------------------------------------------
            # STEP 2
            # Find ready nodes
            # ------------------------------------------

            ready_nodes = self.get_ready_nodes(
                plan=plan,
                completed=completed,
                failed=failed,
                blocked=blocked,
            )

            # ------------------------------------------
            # Nothing left to execute
            # ------------------------------------------

            if not ready_nodes:

                unresolved = [
                    node.id
                    for node in plan.nodes
                    if (
                        node.id not in completed
                        and node.id not in failed
                        and node.id not in blocked
                    )
                ]

                if unresolved:

                    execution_metadata[
                        "status"
                    ] = "stuck"

                    execution_metadata[
                        "unresolved_nodes"
                    ] = unresolved

                    raise RuntimeError(
                        "Graph execution is stuck.\n"
                        f"Unresolved nodes: "
                        f"{unresolved}"
                    )

                break

            # ------------------------------------------
            # STEP 3
            # Display ready nodes
            # ------------------------------------------

            print("\n")
            print("========================================")
            print("READY NODES")
            print("========================================")

            current_parallel_batch = []

            for node in ready_nodes:

                print(
                    f"  🚀 {node.id}"
                    f" → {node.agent}"
                )

                current_parallel_batch.append(
                    node.id
                )

            # ------------------------------------------
            # Store parallel execution batch
            # ------------------------------------------

            execution_metadata[
                "parallel_batches"
            ].append(
                {
                    "layer": max(
                        layers[node.id]
                        for node in ready_nodes
                    ),

                    "nodes":
                        current_parallel_batch,

                    "parallel_count":
                        len(current_parallel_batch),

                    "started_at":
                        datetime.now(
                            timezone.utc
                        ).isoformat(),
                }
            )

            # ------------------------------------------
            # STEP 4
            # Execute READY nodes in parallel
            # ------------------------------------------

            with ThreadPoolExecutor(
                max_workers=len(ready_nodes)
            ) as executor:

                futures = {}

                for node in ready_nodes:

                    future = executor.submit(
                        self.execute_node,
                        node,
                        state,
                        results,
                    )

                    futures[future] = node

                # ------------------------------------------
                # STEP 5
                # Collect results independently
                # ------------------------------------------

                for future in as_completed(
                    futures
                ):

                    node = futures[future]

                    try:

                        result = future.result()

                        results[node.id] = result

                        completed.add(
                            node.id
                        )

                        # ----------------------------------
                        # Metadata
                        # ----------------------------------

                        execution_metadata[
                            "nodes"
                        ][node.id] = {
                            **result,

                            "node_id":
                                node.id,

                            "agent":
                                node.agent,

                            "layer":
                                layers[node.id],

                            "dependencies":
                                list(
                                    node.depends_on
                                ),

                            "status":
                                "completed",
                        }

                        execution_metadata[
                            "execution_order"
                        ].append(
                            node.id
                        )

                        print(
                            f"\n✅ COMPLETED: "
                            f"{node.id}"
                        )

                    except Exception as exc:

                        failed.add(
                            node.id
                        )

                        failed_result = {
                            "status": "failed",

                            "agent":
                                node.agent,

                            "node_id":
                                node.id,

                            "layer":
                                layers[node.id],

                            "dependencies":
                                list(
                                    node.depends_on
                                ),

                            "error":
                                str(exc),

                            "failed_at":
                                datetime.now(
                                    timezone.utc
                                ).isoformat(),
                        }

                        results[node.id] = (
                            failed_result
                        )

                        execution_metadata[
                            "nodes"
                        ][node.id] = (
                            failed_result
                        )

                        execution_metadata[
                            "execution_order"
                        ].append(
                            node.id
                        )

                        print(
                            f"\n❌ FAILED: "
                            f"{node.id}"
                        )

                        print(
                            f"   Agent: "
                            f"{node.agent}"
                        )

                        print(
                            f"   Error: "
                            f"{exc}"
                        )

        # ==================================================
        # FINAL EXECUTION SUMMARY
        # ==================================================

        workflow_completed_at = datetime.now(
            timezone.utc
        )

        duration = (
            workflow_completed_at
            - workflow_started_at
        ).total_seconds()

        # ------------------------------------------
        # Determine final workflow status
        # ------------------------------------------

        if failed:

            workflow_status = "failed"

        elif blocked:

            workflow_status = "partially_completed"

        else:

            workflow_status = "completed"

        execution_metadata[
            "status"
        ] = workflow_status

        execution_metadata[
            "completed_at"
        ] = workflow_completed_at.isoformat()

        execution_metadata[
            "duration_seconds"
        ] = duration

        execution_metadata[
            "completed_nodes"
        ] = list(completed)

        execution_metadata[
            "failed_nodes"
        ] = list(failed)

        execution_metadata[
            "blocked_nodes"
        ] = list(blocked)

        # ------------------------------------------
        # Print summary
        # ------------------------------------------

        print("\n")
        print("========================================")
        print("       GRAPH EXECUTION FINISHED")
        print("========================================")

        print(
            f"Status      : {workflow_status}"
        )

        print(
            f"Duration    : {duration:.2f}s"
        )

        print(
            f"✅ Completed : {list(completed)}"
        )

        print(
            f"❌ Failed    : {list(failed)}"
        )

        print(
            f"⛔ Blocked   : {list(blocked)}"
        )

        # ------------------------------------------
        # Attach metadata to state
        # ------------------------------------------

        state.execution_metadata = (
            execution_metadata
        )

        reporter = ExecutionReporter(workflow_id = execution_metadata["workflow_id"])
        report_paths = reporter.generate(execution_metadata)
        print("\n========================================")
        print("        REPORTS GENERATED")
        print("========================================")

        print(
            f"JSON : {report_paths['execution_json']}"
        )

        print(
            f"MD   : {report_paths['execution_markdown']}"
        )

        print(
            f"HTML : {report_paths['execution_html']}"
        )

        return results

    # ==================================================
    # FIND READY NODES
    # ==================================================

    def get_ready_nodes(
        self,
        plan: ExecutionPlan,
        completed: set[str],
        failed: set[str],
        blocked: set[str],
    ) -> list[ExecutionNode]:

        ready = []

        for node in plan.nodes:

            # Already resolved
            if node.id in completed:
                continue

            if node.id in failed:
                continue

            if node.id in blocked:
                continue

            # ------------------------------------------
            # IMPORTANT:
            # A node is ready ONLY when ALL dependencies
            # have successfully completed.
            # ------------------------------------------

            dependencies_satisfied = all(
                dependency in completed
                for dependency in node.depends_on
            )

            if dependencies_satisfied:

                ready.append(node)

        return ready

    # ==================================================
    # FIND BLOCKED NODES
    # ==================================================

    def get_blocked_nodes(
        self,
        plan: ExecutionPlan,
        completed: set[str],
        failed: set[str],
        blocked: set[str],
    ) -> list[ExecutionNode]:

        blocked_nodes = []

        for node in plan.nodes:

            if node.id in completed:
                continue

            if node.id in failed:
                continue

            if node.id in blocked:
                continue

            # ------------------------------------------
            # If ANY dependency failed or was blocked,
            # this node cannot execute.
            # ------------------------------------------

            dependency_failed = any(
                dependency in failed
                or dependency in blocked
                for dependency in node.depends_on
            )

            if dependency_failed:

                blocked_nodes.append(node)

        return blocked_nodes

    # ==================================================
    # EXECUTE ONE NODE
    # ==================================================

    def execute_node(
        self,
        node: ExecutionNode,
        state,
        results: dict[str, Any],
    ):
        started_at=datetime.now(timezone.utc)
        print("\n")
        print("----------------------------------------")
        print(
            f"STARTING NODE: {node.id}"
        )
        print(
            f"AGENT: {node.agent}"
        )
        print(
            f"DEPENDS ON: {node.depends_on}"
        )
        print("----------------------------------------")

        runner = self.agent_runners.get(
            node.agent
        )

        if runner is None:

            raise ValueError(
                f"No runner registered for "
                f"agent '{node.agent}'"
            )

        try:
            result = runner(
                state=state,
                results=results,
                node=node,
            )

            completed_at=datetime.now(timezone.utc)
            duration=(completed_at-started_at).total_seconds()
            result["started_at"] = (started_at.isoformat())
            result["completed_at"] = (completed_at.isoformat())
            result["duration_seconds"] = duration
            result["node_id"] = node.id
            result["dependencies"] = (list(node.depends_on))
            return result
        except Exception as exc:
            failed_at=datetime.now(timezone.utc)
            duration=(failed_at-started_at).total_seconds()
            raise RuntimeError(
                f"{exc}"
            ) from exc
    # ==================================================
    # RESEARCH AGENT
    # ==================================================

    def run_research(
        self,
        state,
        results,
        node,
    ):

        company = state.lead_data

        print(
            "\n🔬 Research Agent running..."
        )

        result = ResearchCrew().crew().kickoff(
            inputs={
                "company_name":
                    company.get("name"),

                "website":
                    company.get("domain"),
            }
        )

        return {
            "status": "completed",

            "agent":
                "company_researcher",

            "output":
                str(result),
        }

    # ==================================================
    # TECHNOLOGY AGENT
    # ==================================================

    def run_technology(
        self,
        state,
        results,
        node,
    ):

        company = state.lead_data

        print(
            "\n🧠 Technology Agent running..."
        )

        result = TechnologyCrew().crew().kickoff(
            inputs={
                "company_name":
                    company.get("name"),

                "website":
                    company.get("domain"),
                "orchestrator_decision": (
                    state.orchestrator_decision
                ),
            }
        )

        return {
            "status": "completed",

            "agent":
                "technology_analyst",

            "output":
                str(result),
        }

    # ==================================================
    # SOLUTION ARCHITECT
    # ==================================================

    def run_solution_architect(self,state,results,node,):


        print(
            "\n🏗️ Solution Architect Agent running..."
        )

        # ------------------------------------------
        # Collect outputs from all DAG dependencies
        # ------------------------------------------

        dependency_outputs = {}

        for dependency in node.depends_on:

            if dependency not in results:

                raise RuntimeError(
                    f"Missing dependency output: "
                    f"{dependency}"
                )

            dependency_result = results[
                dependency
            ]

            # Results are expected to contain:
            # {
            #     "status": "completed",
            #     "agent": "...",
            #     "output": "..."
            # }

            if not isinstance(
                dependency_result,
                dict
            ):

                raise RuntimeError(
                    f"Invalid result format from "
                    f"dependency '{dependency}'"
                )

            if dependency_result.get(
                "status"
            ) != "completed":

                raise RuntimeError(
                    f"Dependency '{dependency}' "
                    f"did not complete successfully"
                )

            dependency_outputs[
                dependency
            ] = dependency_result.get(
                "output"
            )

        # ------------------------------------------
        # Validate that dependencies actually
        # produced outputs
        # ------------------------------------------

        missing_outputs = [
            dependency
            for dependency, output
            in dependency_outputs.items()
            if output is None
        ]

        if missing_outputs:

            raise RuntimeError(
                "Missing outputs from dependencies: "
                + ", ".join(missing_outputs)
            )

        # ------------------------------------------
        # Company information
        # ------------------------------------------

        company = state.lead_data

        # ------------------------------------------
        # Run Solution Architect
        #
        # IMPORTANT:
        # We do NOT hardcode:
        #
        # research_result
        # technology_result
        #
        # The planner decides the dependencies.
        # The executor passes all of them.
        # ------------------------------------------

        result = (
            SolutionArchitectCrew()
            .crew()
            .kickoff(
                inputs={
                    "company_name":
                        company.get("name"),

                    "dependency_outputs":
                        dependency_outputs,
                }
            )
        )

        # ------------------------------------------
        # Return standardized node result
        # ------------------------------------------

        return {
            "status": "completed",

            "agent":
                "solution_architect",

            "output":
                str(result),

            "dependencies":
                list(node.depends_on),
        }

        # ==================================================
        # PRESALES STRATEGY
        # ==================================================

    def run_strategy(self,state,results,node,):
    

        print(
            "\n🎯 Presales Strategy Agent running..."
        )

        # ------------------------------------------
        # Collect outputs from ALL dependencies
        # dynamically
        # ------------------------------------------

        dependency_outputs = {}

        for dependency in node.depends_on:

            if dependency not in results:
                raise RuntimeError(
                    f"Missing dependency output: "
                    f"{dependency}"
                )

            dependency_result = results[
                dependency
            ]

            # --------------------------------------
            # Validate dependency result
            # --------------------------------------

            if not isinstance(
                dependency_result,
                dict
            ):
                raise RuntimeError(
                    f"Invalid result format from "
                    f"dependency '{dependency}'"
                )

            if dependency_result.get(
                "status"
            ) != "completed":
                raise RuntimeError(
                    f"Dependency '{dependency}' "
                    f"did not complete successfully"
                )

            output = dependency_result.get(
                "output"
            )

            if output is None:
                raise RuntimeError(
                    f"Dependency '{dependency}' "
                    f"completed without an output"
                )

            # --------------------------------------
            # Store ONLY the actual output
            # --------------------------------------

            dependency_outputs[
                dependency
            ] = output

        # ------------------------------------------
        # Company information
        # ------------------------------------------

        company = state.lead_data

        # ------------------------------------------
        # Run Presales Strategist
        # ------------------------------------------

        result = (
            SynthesisCrew()
            .crew()
            .kickoff(
                inputs={
                    "company_name":
                        company.get("name"),

                    "dependency_outputs":
                        dependency_outputs,

                    "orchestrator_decision":
                        state.orchestrator_decision,
                }
            )
        )

        # ------------------------------------------
        # Standardized node result
        # ------------------------------------------

        return {
            "status": "completed",

            "agent":
                "presales_strategist",

            "output":
                str(result),

            "dependencies":
                list(node.depends_on),
        }

    def get_dependency_outputs(self,node: ExecutionNode,results: dict[str, Any],) -> dict[str, Any]:

        dependency_outputs = {}

        for dependency in node.depends_on:

            if dependency not in results:

                raise RuntimeError(
                    f"Missing dependency output: "
                    f"{dependency}"
                )

            dependency_result = results[dependency]

            if (
                not isinstance(
                    dependency_result,
                    dict,
                )
                or "output" not in dependency_result
            ):
                raise RuntimeError(
                    f"Invalid output from dependency "
                    f"'{dependency}'"
                )

            dependency_outputs[
                dependency
            ] = dependency_result["output"]

        return dependency_outputs