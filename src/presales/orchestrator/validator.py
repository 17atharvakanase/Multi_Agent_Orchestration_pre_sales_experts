from presales.orchestrator.models import (
    ExecutionPlan
)

from presales.orchestrator.registry import (
    AGENT_REGISTRY
)


class DAGValidationError(Exception):
    pass


class DAGValidator:

    def __init__(self):

        self.available_agents = {
            agent["name"]
            for agent in AGENT_REGISTRY
        }

    def validate(
        self,
        plan: ExecutionPlan
    ):

        self._validate_agents(plan)

        self._validate_dependencies(plan)

        self._validate_cycles(plan)

        return True

    # ------------------------------------------
    # Validate agent names
    # ------------------------------------------

    def _validate_agents(
        self,
        plan: ExecutionPlan
    ):

        for node in plan.nodes:

            if node.agent not in self.available_agents:

                raise DAGValidationError(
                    f"Unknown agent: {node.agent}"
                )

    # ------------------------------------------
    # Validate dependency references
    # ------------------------------------------

    def _validate_dependencies(
        self,
        plan: ExecutionPlan
    ):

        node_ids = {
            node.id
            for node in plan.nodes
        }

        for node in plan.nodes:

            for dependency in node.depends_on:

                if dependency not in node_ids:

                    raise DAGValidationError(
                        f"Node '{node.id}' depends "
                        f"on unknown node '{dependency}'"
                    )

    # ------------------------------------------
    # Detect cycles
    # ------------------------------------------

    def _validate_cycles(
        self,
        plan: ExecutionPlan
    ):

        graph = {
            node.id: node.depends_on
            for node in plan.nodes
        }

        visited = set()

        visiting = set()

        def visit(node):

            if node in visiting:

                raise DAGValidationError(
                    f"Cycle detected involving "
                    f"node '{node}'"
                )

            if node in visited:

                return

            visiting.add(node)

            for dependency in graph[node]:

                visit(dependency)

            visiting.remove(node)

            visited.add(node)

        for node in graph:

            visit(node)