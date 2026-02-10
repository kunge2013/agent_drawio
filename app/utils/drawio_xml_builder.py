"""DrawIO XML builder for creating DrawIO compatible diagram files."""
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from typing import Optional


class DrawIOXMLBuilder:
    """
    Builder class for creating DrawIO compatible XML files.
    Based on mxGraphModel format used by DrawIO.
    """

    def __init__(self):
        self.diagram = Element("mxGraphModel")
        self.diagram.set("dx", "1200")
        self.diagram.set("dy", "800")
        self.diagram.set("grid", "1")
        self.diagram.set("gridSize", "10")
        self.diagram.set("guides", "1")
        self.diagram.set("tooltips", "1")
        self.diagram.set("connect", "1")
        self.diagram.set("arrows", "1")
        self.diagram.set("fold", "1")
        self.diagram.set("page", "1")
        self.diagram.set("pageScale", "1")
        self.diagram.set("pageWidth", "1169")
        self.diagram.set("pageHeight", "827")
        self.diagram.set("math", "0")
        self.diagram.set("shadow", "0")

        self.root = SubElement(self.diagram, "root")
        self._add_default_cells()

        self.cell_counter = 0

    def _add_default_cells(self):
        """Add default mxCell elements required by DrawIO."""
        # Root cell
        mx_cell = SubElement(self.root, "mxCell")
        mx_cell.set("id", "0")

        # Default parent
        mx_cell = SubElement(self.root, "mxCell")
        mx_cell.set("id", "1")
        mx_cell.set("parent", "0")

    def add_node(
        self,
        label: str,
        x: int,
        y: int,
        width: int = 120,
        height: int = 60,
        style: str = "rounded=1;whiteSpace=wrap;html=1;",
        node_type: str = "process"
    ) -> str:
        """
        Add a node to the diagram.

        Args:
            label: Text label for the node
            x, y: Position coordinates
            width, height: Node dimensions
            style: mxGraph style string
            node_type: Type of node (start, end, process, decision)

        Returns:
            Cell ID of the created node
        """
        self.cell_counter += 1
        cell_id = str(self.cell_counter + 1)

        # Apply default styles based on node type
        if node_type == "start":
            style = "ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;"
        elif node_type == "end":
            style = "ellipse;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;"
        elif node_type == "decision":
            style = "rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;"
        elif node_type == "process":
            style = "rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;"
        elif node_type == "screen":
            style = "rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;"

        mx_cell = SubElement(self.root, "mxCell")
        mx_cell.set("id", cell_id)
        mx_cell.set("value", label)
        mx_cell.set("style", style)
        mx_cell.set("vertex", "1")
        mx_cell.set("parent", "1")

        mx_geometry = SubElement(mx_cell, "mxGeometry")
        mx_geometry.set("x", str(x))
        mx_geometry.set("y", str(y))
        mx_geometry.set("width", str(width))
        mx_geometry.set("height", str(height))
        mx_geometry.set("as", "geometry")

        return cell_id

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        label: str = "",
        style: str = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;",
        edge_type: str = "arrow"
    ) -> str:
        """
        Add an edge (arrow) between two nodes.

        Args:
            source_id: ID of source node
            target_id: ID of target node
            label: Optional label for the edge
            style: mxGraph style string
            edge_type: Type of edge (arrow, dashed)

        Returns:
            Cell ID of the created edge
        """
        self.cell_counter += 1
        cell_id = str(self.cell_counter + 1)

        if edge_type == "dashed":
            style = style + "dashed=1;"

        mx_cell = SubElement(self.root, "mxCell")
        mx_cell.set("id", cell_id)
        mx_cell.set("value", label)
        mx_cell.set("style", style)
        mx_cell.set("edge", "1")
        mx_cell.set("parent", "1")
        mx_cell.set("source", source_id)
        mx_cell.set("target", target_id)

        mx_geometry = SubElement(mx_cell, "mxGeometry")
        mx_geometry.set("relative", "1")
        mx_geometry.set("as", "geometry")

        return cell_id

    def add_swimlane(
        self,
        label: str,
        x: int,
        y: int,
        width: int = 300,
        height: int = 400
    ) -> str:
        """Add a swimlane container for grouping related nodes."""
        self.cell_counter += 1
        cell_id = str(self.cell_counter + 1)

        style = "swimlane;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;"

        mx_cell = SubElement(self.root, "mxCell")
        mx_cell.set("id", cell_id)
        mx_cell.set("value", label)
        mx_cell.set("style", style)
        mx_cell.set("vertex", "1")
        mx_cell.set("parent", "1")

        mx_geometry = SubElement(mx_cell, "mxGeometry")
        mx_geometry.set("x", str(x))
        mx_geometry.set("y", str(y))
        mx_geometry.set("width", str(width))
        mx_geometry.set("height", str(height))
        mx_geometry.set("as", "geometry")

        return cell_id

    def add_container(
        self,
        label: str,
        x: int,
        y: int,
        width: int = 200,
        height: int = 150
    ) -> str:
        """Add a container for grouping UI elements."""
        self.cell_counter += 1
        cell_id = str(self.cell_counter + 1)

        style = "whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;rounded=1;"

        mx_cell = SubElement(self.root, "mxCell")
        mx_cell.set("id", cell_id)
        mx_cell.set("value", label)
        mx_cell.set("style", style)
        mx_cell.set("vertex", "1")
        mx_cell.set("parent", "1")

        mx_geometry = SubElement(mx_cell, "mxGeometry")
        mx_geometry.set("x", str(x))
        mx_geometry.set("y", str(y))
        mx_geometry.set("width", str(width))
        mx_geometry.set("height", str(height))
        mx_geometry.set("as", "geometry")

        return cell_id

    def build(self) -> str:
        """
        Build and return the complete DrawIO XML string.

        Returns:
            DrawIO compatible XML string
        """
        # Wrap in mxfile structure
        mxfile = Element("mxfile")
        mxfile.set("host", "app.diagrams.net")
        mxfile.set("modified", "2025-01-01T00:00:00.000Z")
        mxfile.set("agent", "DrawIO Agent")
        mxfile.set("version", "22.1.0")

        diagram = SubElement(mxfile, "diagram")
        diagram.set("id", "diagram")
        diagram.set("name", "Generated Diagram")

        # Add the mxGraphModel
        diagram.append(self.diagram)

        # Pretty print the XML
        rough_xml = tostring(mxfile, encoding="unicode")
        pretty_xml = minidom.parseString(rough_xml).toprettyxml(indent="  ")

        return pretty_xml

    def save(self, filename: str):
        """Save the diagram to a file."""
        xml_content = self.build()
        with open(filename, "w", encoding="utf-8") as f:
            f.write(xml_content)
