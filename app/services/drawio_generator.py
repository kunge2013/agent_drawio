"""DrawIO generator service for creating DrawIO XML from flow data."""
from typing import Dict, Any, List
from app.utils.drawio_xml_builder import DrawIOXMLBuilder


class DrawIOGenerator:
    """Service for generating DrawIO XML from structured flow data."""

    def generate_ui_flow_diagram(self, flow_data: Dict[str, Any]) -> str:
        """
        Generate a UI flow diagram in DrawIO XML format.

        Args:
            flow_data: Dictionary containing nodes and edges from LLM

        Returns:
            DrawIO XML string
        """
        builder = DrawIOXMLBuilder()

        nodes = flow_data.get("nodes", [])
        edges = flow_data.get("edges", [])

        node_positions = {}
        x_offset = 50
        y_offset = 50
        x_increment = 200
        y_increment = 150

        # Add nodes
        for idx, node in enumerate(nodes):
            row = idx // 4
            col = idx % 4

            x = x_offset + (col * x_increment)
            y = y_offset + (row * y_increment)

            node_type = self._determine_node_type(node)
            cell_id = builder.add_node(
                label=node.get("name", "Node"),
                x=x,
                y=y,
                width=150,
                height=80,
                node_type=node_type
            )
            node_positions[node["name"]] = cell_id

        # Add edges
        for edge in edges:
            source_id = node_positions.get(edge["from"])
            target_id = node_positions.get(edge["to"])

            if source_id and target_id:
                builder.add_edge(
                    source_id=source_id,
                    target_id=target_id,
                    label=edge.get("label", "")
                )

        return builder.build()

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

    def generate_prototype_diagram(self, prototype_data: Dict[str, Any]) -> str:
        """
        Generate a prototype wireframe diagram.

        Args:
            prototype_data: Prototype design data

        Returns:
            DrawIO XML string
        """
        builder = DrawIOXMLBuilder()

        screens = prototype_data.get("screens", [])
        x_offset = 50
        y_offset = 50
        x_spacing = 350
        y_spacing = 400

        for idx, screen in enumerate(screens):
            row = idx // 3
            col = idx % 3

            x = x_offset + (col * x_spacing)
            y = y_offset + (row * y_spacing)

            screen_name = screen.get("name", f"Screen {idx + 1}")

            # Add screen container
            container_id = builder.add_container(
                label=screen_name,
                x=x,
                y=y,
                width=280,
                height=350
            )

        return builder.build()

    def _determine_node_type(self, node: Dict[str, Any]) -> str:
        """
        Determine the node type based on node properties.

        Args:
            node: Node dictionary

        Returns:
            Node type string
        """
        node_type = node.get("type", "screen").lower()

        if node_type in ["start", "begin"]:
            return "start"
        elif node_type in ["end", "finish", "terminate"]:
            return "end"
        elif node_type in ["decision", "branch", "choice"]:
            return "decision"
        else:
            return "screen"
