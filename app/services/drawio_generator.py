"""DrawIO generator service for creating DrawIO XML from flow data."""
from typing import Dict, Any, List
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

        # Store all nodes for tracking connections
        nodes: List[Dict[str, Any]] = []
        node_map: Dict[str, str] = {}  # name -> cell_id

        x = 400  # Center position
        y = 50
        y_increment = 100

        # Helper function to add a node
        def add_node(name: str, node_type: str, offset_x: int = 0) -> str:
            nonlocal y
            cell_id = builder.add_node(
                label=name,
                x=x + offset_x,
                y=y,
                width=160 if node_type in ["process", "start", "end"] else 140,
                height=60 if node_type in ["process", "start", "end"] else 80,
                node_type=node_type
            )
            return cell_id

        # Add start node (中文)
        start_id = add_node("开始", "start")
        nodes.append({"id": start_id, "name": "开始", "type": "start"})
        node_map["开始"] = start_id
        y += y_increment

        # Add process nodes
        processes = flow_data.get("processes", [])
        last_node_id = start_id

        for process in processes:
            name = process.get("name", "处理步骤")
            cell_id = add_node(name, "process")
            nodes.append({"id": cell_id, "name": name, "type": "process"})
            node_map[name] = cell_id

            # Connect from previous node
            builder.add_edge(last_node_id, cell_id, "")
            last_node_id = cell_id
            y += y_increment

        # Add decision nodes with branches
        decisions = flow_data.get("decisions", [])
        branch_end_nodes: List[str] = []  # Track nodes that need to connect to end

        for decision in decisions:
            name = decision.get("name", "决策点")
            true_branch = decision.get("true_branch")
            false_branch = decision.get("false_branch")

            # Add decision node
            decision_id = add_node(name, "decision")
            nodes.append({"id": decision_id, "name": name, "type": "decision"})
            node_map[name] = decision_id

            # Connect from previous node
            builder.add_edge(last_node_id, decision_id, "")
            last_node_id = decision_id

            # Add branches if they exist
            if true_branch:
                branch_y = y + y_increment
                true_id = add_node(true_branch, "process", offset_x=-150)
                nodes.append({"id": true_id, "name": true_branch, "type": "process"})
                node_map[true_branch] = true_id
                branch_end_nodes.append(true_id)
                # Connect "是" (Yes) branch
                builder.add_edge(decision_id, true_id, "是")

            if false_branch:
                branch_y = y + y_increment
                false_id = add_node(false_branch, "process", offset_x=150)
                nodes.append({"id": false_id, "name": false_branch, "type": "process"})
                node_map[false_branch] = false_id
                branch_end_nodes.append(false_id)
                # Connect "否" (No) branch
                builder.add_edge(decision_id, false_id, "否")

            if true_branch or false_branch:
                y += y_increment * 2

        # Add end node (中文)
        # If there were branches, move end node down and connect all branch ends to it
        if branch_end_nodes:
            y += y_increment

        end_id = add_node("结束", "end")
        nodes.append({"id": end_id, "name": "结束", "type": "end"})
        node_map["结束"] = end_id

        # Connect the last sequential node to end
        if branch_end_nodes:
            # If there were branches, connect all branch ends to end
            for branch_end_id in branch_end_nodes:
                builder.add_edge(branch_end_id, end_id, "")
        else:
            # No branches, just connect sequentially
            if last_node_id != end_id:
                builder.add_edge(last_node_id, end_id, "")

        return builder.build()
