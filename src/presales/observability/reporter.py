import json
from pathlib import Path
from datetime import datetime


class ExecutionReporter:

    def __init__(
        self,
        workflow_id: str,
        base_dir: str = "runs",
    ):

        self.workflow_id = workflow_id

        self.run_dir = (
            Path(base_dir)
            / workflow_id
        )

        self.agents_dir = (
            self.run_dir
            / "agents"
        )

        self.outputs_dir = (
            self.run_dir
            / "outputs"
        )

        # Create directories
        self.agents_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.outputs_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ==================================================
    # JSON
    # ==================================================

    def save_json(
        self,
        execution: dict,
    ):

        path = (
            self.run_dir
            / "execution.json"
        )

        self._write_json(
            path,
            execution,
        )

        return path

    # ==================================================
    # Individual Agent JSON
    # ==================================================

    def save_agent_reports(
        self,
        execution: dict,
    ):

        nodes = execution.get(
            "nodes",
            {},
        )

        paths = {}

        for node_id, metadata in nodes.items():

            safe_name = self._safe_filename(
                node_id
            )

            path = (
                self.agents_dir
                / f"{safe_name}.json"
            )

            agent_data = {
                "workflow_id":
                    execution.get(
                        "workflow_id"
                    ),

                "node_id":
                    node_id,

                "agent":
                    metadata.get(
                        "agent"
                    ),

                "status":
                    metadata.get(
                        "status"
                    ),

                "layer":
                    metadata.get(
                        "layer"
                    ),

                "dependencies":
                    metadata.get(
                        "dependencies",
                        [],
                    ),

                "started_at":
                    metadata.get(
                        "started_at"
                    ),

                "completed_at":
                    metadata.get(
                        "completed_at"
                    ),

                "duration_seconds":
                    metadata.get(
                        "duration_seconds"
                    ),

                "error":
                    metadata.get(
                        "error"
                    ),

                "output":
                    metadata.get(
                        "output"
                    ),
            }

            self._write_json(
                path,
                agent_data,
            )

            paths[node_id] = path

        return paths

    # ==================================================
    # Agent Output TXT files
    # ==================================================

    def save_agent_outputs(
        self,
        execution: dict,
    ):

        nodes = execution.get(
            "nodes",
            {},
        )

        paths = {}

        for node_id, metadata in nodes.items():

            output = metadata.get(
                "output"
            )

            if output is None:
                continue

            safe_name = self._safe_filename(
                node_id
            )

            path = (
                self.outputs_dir
                / f"{safe_name}.txt"
            )

            path.write_text(
                str(output),
                encoding="utf-8",
            )

            paths[node_id] = path

        return paths

    # ==================================================
    # MARKDOWN REPORT
    # ==================================================

    def save_markdown(
        self,
        execution: dict,
    ):

        lines = []

        workflow_id = execution.get(
            "workflow_id",
            self.workflow_id,
        )

        status = execution.get(
            "status",
            "unknown",
        )

        duration = execution.get(
            "duration_seconds"
        )

        # ------------------------------------------
        # Header
        # ------------------------------------------

        lines.append(
            "# Presales Workflow Execution"
        )

        lines.append("")

        lines.append(
            f"**Workflow ID:** `{workflow_id}`"
        )

        lines.append(
            f"**Status:** `{status}`"
        )

        if duration is not None:

            lines.append(
                f"**Duration:** "
                f"`{duration:.2f} seconds`"
            )

        lines.append("")

        # ------------------------------------------
        # Company
        # ------------------------------------------

        company = execution.get(
            "company"
        )

        if company:

            lines.append(
                "## Company"
            )

            lines.append("")

            for key, value in (
                company.items()
            ):

                lines.append(
                    f"- **{key}:** {value}"
                )

            lines.append("")

        # ------------------------------------------
        # Execution Layers
        # ------------------------------------------

        lines.append(
            "## Execution Layers"
        )

        lines.append("")

        layers = execution.get(
            "layers",
            {},
        )

        for layer, nodes in sorted(
            layers.items(),
            key=lambda item: int(
                item[0]
            ),
        ):

            lines.append(
                f"### Layer {layer}"
            )

            lines.append("")

            for node_id in nodes:

                lines.append(
                    f"- `{node_id}`"
                )

            lines.append("")

        # ------------------------------------------
        # Parallel Batches
        # ------------------------------------------

        lines.append(
            "## Parallel Execution"
        )

        lines.append("")

        batches = execution.get(
            "parallel_batches",
            [],
        )

        if not batches:

            lines.append(
                "No parallel execution recorded."
            )

            lines.append("")

        else:

            for index, batch in enumerate(
                batches,
                start=1,
            ):

                nodes = batch.get(
                    "nodes",
                    [],
                )

                lines.append(
                    f"### Batch {index}"
                )

                lines.append("")

                lines.append(
                    f"- Layer: "
                    f"`{batch.get('layer')}`"
                )

                lines.append(
                    f"- Parallel agents: "
                    f"`{batch.get('parallel_count')}`"
                )

                lines.append("")

                for node in nodes:

                    lines.append(
                        f"- `{node}`"
                    )

                lines.append("")

        # ------------------------------------------
        # Agent Metadata
        # ------------------------------------------

        lines.append(
            "## Agent Execution"
        )

        lines.append("")

        lines.append(
            "| Node | Agent | Status | Layer | "
            "Duration | Dependencies |"
        )

        lines.append(
            "|---|---|---|---:|---:|---|"
        )

        nodes = execution.get(
            "nodes",
            {},
        )

        for node_id, metadata in (
            nodes.items()
        ):

            dependencies = metadata.get(
                "dependencies",
                [],
            )

            dependency_text = (
                ", ".join(dependencies)
                if dependencies
                else "-"
            )

            duration_value = metadata.get(
                "duration_seconds"
            )

            duration_text = (
                f"{duration_value:.2f}s"
                if isinstance(
                    duration_value,
                    (int, float),
                )
                else "-"
            )

            lines.append(
                f"| `{node_id}` "
                f"| `{metadata.get('agent', '-')}` "
                f"| `{metadata.get('status', '-')}` "
                f"| {metadata.get('layer', '-')} "
                f"| {duration_text} "
                f"| {dependency_text} |"
            )

        lines.append("")

        # ------------------------------------------
        # Agent Outputs
        # ------------------------------------------

        lines.append(
            "## Agent Outputs"
        )

        lines.append("")

        for node_id, metadata in (
            nodes.items()
        ):

            output = metadata.get(
                "output"
            )

            if not output:
                continue

            lines.append(
                f"### {node_id}"
            )

            lines.append("")

            lines.append(
                "```text"
            )

            lines.append(
                str(output)
            )

            lines.append(
                "```"
            )

            lines.append("")

        # ------------------------------------------
        # Errors
        # ------------------------------------------

        failed_nodes = execution.get(
            "failed_nodes",
            [],
        )

        if failed_nodes:

            lines.append(
                "## Failed Nodes"
            )

            lines.append("")

            for node_id in failed_nodes:

                metadata = nodes.get(
                    node_id,
                    {},
                )

                lines.append(
                    f"### `{node_id}`"
                )

                lines.append("")

                lines.append(
                    metadata.get(
                        "error",
                        "Unknown error",
                    )
                )

                lines.append("")

        # ------------------------------------------
        # Write file
        # ------------------------------------------

        path = (
            self.run_dir
            / "execution.md"
        )

        path.write_text(
            "\n".join(lines),
            encoding="utf-8",
        )

        return path

    # ==================================================
    # HTML REPORT
    # ==================================================

    def save_html(
        self,
        execution: dict,
    ):

        workflow_id = execution.get(
            "workflow_id",
            self.workflow_id,
        )

        status = execution.get(
            "status",
            "unknown",
        )

        duration = execution.get(
            "duration_seconds"
        )

        layers = execution.get(
            "layers",
            {},
        )

        nodes = execution.get(
            "nodes",
            {},
        )

        html = []

        html.append(
            "<!DOCTYPE html>"
        )

        html.append(
            "<html>"
        )

        html.append(
            "<head>"
        )

        html.append(
            "<meta charset='UTF-8'>"
        )

        html.append(
            "<meta name='viewport' "
            "content='width=device-width, "
            "initial-scale=1.0'>"
        )

        html.append(
            f"<title>Presales Workflow "
            f"{workflow_id}</title>"
        )

        html.append(
            """
            <style>

            body {
                font-family:
                    Arial, sans-serif;

                background:
                    #f5f7fa;

                margin: 0;
                padding: 30px;
                color: #1f2937;
            }

            .container {
                max-width: 1400px;
                margin: auto;
            }

            .header {
                background: white;
                padding: 25px;
                border-radius: 12px;
                margin-bottom: 20px;
                box-shadow:
                    0 2px 8px
                    rgba(0,0,0,0.08);
            }

            .status {
                display: inline-block;
                padding: 6px 12px;
                border-radius: 20px;
                background: #dcfce7;
                color: #166534;
                font-weight: bold;
            }

            .layer {
                background: white;
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 20px;
                box-shadow:
                    0 2px 8px
                    rgba(0,0,0,0.08);
            }

            .nodes {
                display: flex;
                gap: 20px;
                flex-wrap: wrap;
            }

            .node {
                background: #ffffff;
                border: 2px solid #d1d5db;
                border-radius: 10px;
                padding: 18px;
                min-width: 220px;
            }

            .node.completed {
                border-color: #22c55e;
            }

            .node.failed {
                border-color: #ef4444;
            }

            .node.blocked {
                border-color: #6b7280;
            }

            .node-title {
                font-size: 18px;
                font-weight: bold;
            }

            .agent {
                color: #6b7280;
                margin-top: 5px;
            }

            .metadata {
                margin-top: 12px;
                font-size: 14px;
            }

            table {
                width: 100%;
                border-collapse:
                    collapse;
                background: white;
            }

            th, td {
                padding: 12px;
                border-bottom:
                    1px solid #e5e7eb;
                text-align: left;
            }

            th {
                background:
                    #f9fafb;
            }

            .output {
                background: #111827;
                color: #f9fafb;
                padding: 15px;
                border-radius: 8px;
                white-space: pre-wrap;
                overflow-x: auto;
            }

            </style>
            """
        )

        html.append(
            "</head>"
        )

        html.append(
            "<body>"
        )

        html.append(
            "<div class='container'>"
        )

        # ------------------------------------------
        # Header
        # ------------------------------------------

        html.append(
            "<div class='header'>"
        )

        html.append(
            "<h1>Presales Workflow Execution</h1>"
        )

        html.append(
            f"<p><strong>Workflow:</strong> "
            f"{workflow_id}</p>"
        )

        html.append(
            f"<p><strong>Status:</strong> "
            f"<span class='status'>"
            f"{status}</span></p>"
        )

        if duration is not None:

            html.append(
                f"<p><strong>Duration:</strong> "
                f"{duration:.2f} seconds</p>"
            )

        html.append(
            "</div>"
        )

        # ------------------------------------------
        # DAG Layers
        # ------------------------------------------

        html.append(
            "<h2>Execution DAG</h2>"
        )

        for layer_number, node_ids in sorted(
            layers.items(),
            key=lambda item: int(
                item[0]
            ),
        ):

            html.append(
                "<div class='layer'>"
            )

            html.append(
                f"<h3>Layer "
                f"{layer_number}</h3>"
            )

            html.append(
                "<div class='nodes'>"
            )

            for node_id in node_ids:

                metadata = nodes.get(
                    node_id,
                    {},
                )

                status_value = metadata.get(
                    "status",
                    "unknown",
                )

                css_class = (
                    status_value
                    if status_value
                    in {
                        "completed",
                        "failed",
                        "blocked",
                    }
                    else ""
                )

                html.append(
                    f"<div class='node "
                    f"{css_class}'>"
                )

                html.append(
                    f"<div class='node-title'>"
                    f"{node_id}</div>"
                )

                html.append(
                    f"<div class='agent'>"
                    f"{metadata.get('agent', '-')}"
                    f"</div>"
                )

                html.append(
                    "<div class='metadata'>"
                )

                html.append(
                    f"Status: "
                    f"<strong>"
                    f"{status_value}"
                    f"</strong><br>"
                )

                html.append(
                    f"Duration: "
                    f"{metadata.get('duration_seconds', '-')}"
                    f"s<br>"
                )

                dependencies = metadata.get(
                    "dependencies",
                    [],
                )

                html.append(
                    f"Dependencies: "
                    f"{', '.join(dependencies) if dependencies else '-'}"
                )

                html.append(
                    "</div>"
                )

                html.append(
                    "</div>"
                )

            html.append(
                "</div>"
            )

            html.append(
                "</div>"
            )

        # ------------------------------------------
        # Agent Metadata Table
        # ------------------------------------------

        html.append(
            "<h2>Agent Metadata</h2>"
        )

        html.append(
            "<table>"
        )

        html.append(
            """
            <tr>
                <th>Node</th>
                <th>Agent</th>
                <th>Status</th>
                <th>Layer</th>
                <th>Duration</th>
                <th>Dependencies</th>
            </tr>
            """
        )

        for node_id, metadata in (
            nodes.items()
        ):

            dependencies = metadata.get(
                "dependencies",
                [],
            )

            html.append(
                "<tr>"
            )

            html.append(
                f"<td>{node_id}</td>"
            )

            html.append(
                f"<td>{metadata.get('agent', '-')}</td>"
            )

            html.append(
                f"<td>{metadata.get('status', '-')}</td>"
            )

            html.append(
                f"<td>{metadata.get('layer', '-')}</td>"
            )

            html.append(
                f"<td>{metadata.get('duration_seconds', '-')}s</td>"
            )

            html.append(
                f"<td>{', '.join(dependencies) if dependencies else '-'}</td>"
            )

            html.append(
                "</tr>"
            )

        html.append(
            "</table>"
        )

        # ------------------------------------------
        # Outputs
        # ------------------------------------------

        html.append(
            "<h2>Agent Outputs</h2>"
        )

        for node_id, metadata in (
            nodes.items()
        ):

            output = metadata.get(
                "output"
            )

            if not output:
                continue

            html.append(
                f"<div class='layer'>"
            )

            html.append(
                f"<h3>{node_id}</h3>"
            )

            html.append(
                "<div class='output'>"
            )

            html.append(
                self._escape_html(
                    str(output)
                )
            )

            html.append(
                "</div>"
            )

            html.append(
                "</div>"
            )

        html.append(
            "</div>"
        )

        html.append(
            "</body>"
        )

        html.append(
            "</html>"
        )

        path = (
            self.run_dir
            / "execution.html"
        )

        path.write_text(
            "\n".join(html),
            encoding="utf-8",
        )

        return path

    # ==================================================
    # SAVE EVERYTHING
    # ==================================================

    def generate(
        self,
        execution: dict,
    ):

        json_path = self.save_json(
            execution
        )

        markdown_path = (
            self.save_markdown(
                execution
            )
        )

        html_path = (
            self.save_html(
                execution
            )
        )

        agent_paths = (
            self.save_agent_reports(
                execution
            )
        )

        output_paths = (
            self.save_agent_outputs(
                execution
            )
        )

        return {
            "run_directory":
                self.run_dir,

            "execution_json":
                json_path,

            "execution_markdown":
                markdown_path,

            "execution_html":
                html_path,

            "agent_reports":
                agent_paths,

            "agent_outputs":
                output_paths,
        }

    # ==================================================
    # HELPERS
    # ==================================================

    @staticmethod
    def _write_json(
        path: Path,
        data: dict,
    ):

        with open(
            path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=2,
                ensure_ascii=False,
                default=str,
            )

    @staticmethod
    def _safe_filename(
        value: str,
    ):

        return "".join(
            char
            if char.isalnum()
            or char in (
                "-",
                "_",
            )
            else "_"
            for char in value
        )

    @staticmethod
    def _escape_html(
        value: str,
    ):

        return (
            value
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#039;")
        )