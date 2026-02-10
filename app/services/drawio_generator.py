"""DrawIO generator service for creating DrawIO XML from flow data."""
from typing import Dict, Any
from app.utils.drawio_xml_builder import DrawIOXMLBuilder


class DrawIOGenerator:
    """Service for generating DrawIO XML from structured flow data."""

    def generate_business_flow_diagram(self, flow_data: Dict[str, Any]) -> str:
        """
        Generate a business process flow diagram in DrawIO XML format.

        Args:
            flow_data: Dictionary containing business process flow

        Returns:
            DrawIO XML string
        """
        builder = DrawIOXMLBuilder()

        node_positions = {}
        x = 250
        y = 50
        y_increment = 120

        # Add start node
        start_id = builder.add_node("Start", x=x, y=y, node_type="start")
        node_positions["Start"] = start_id
        y += y_increment

        # Add process nodes
        processes = flow_data.get("processes", [])
        for process in processes:
            cell_id = builder.add_node(
                label=process.get("name", "Process"),
                x=x,
                y=y,
                width=180,
                height=60,
                node_type="process"
            )
            node_positions[process["name"]] = cell_id
            y += y_increment

        # Add decision nodes
        decisions = flow_data.get("decisions", [])
        for decision in decisions:
            cell_id = builder.add_node(
                label=decision.get("name", "Decision"),
                x=x,
                y=y,
                width=150,
                height=80,
                node_type="decision"
            )
            node_positions[decision["name"]] = cell_id

            # Add branches if they exist
            if decision.get("true_branch"):
                true_y = y + y_increment
                true_id = builder.add_node(
                    label=decision["true_branch"],
                    x=x - 150,
                    y=true_y,
                    width=140,
                    height=60,
                    node_type="process"
                )
                node_positions[decision["true_branch"]] = true_id
                builder.add_edge(cell_id, true_id, "Yes")

            if decision.get("false_branch"):
                false_y = y + y_increment
                false_id = builder.add_node(
                    label=decision["false_branch"],
                    x=x + 150,
                    y=false_y,
                    width=140,
                    height=60,
                    node_type="process"
                )
                node_positions[decision["false_branch"]] = false_id
                builder.add_edge(cell_id, false_id, "No")

            y += y_increment * 2

        # Add end node
        end_id = builder.add_node("End", x=x, y=y, node_type="end")
        node_positions["End"] = end_id

        # Connect nodes in sequence
        all_ids = list(node_positions.values())
        for i in range(len(all_ids) - 1):
            builder.add_edge(all_ids[i], all_ids[i + 1])

        return builder.build()
