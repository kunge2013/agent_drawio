/**
 * DrawIO Viewer - Renders DrawIO XML using mxGraph
 */
class DrawIOViewer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.graph = null;
        this.currentDiagramId = null;

        if (!this.container) {
            console.error('Container not found:', containerId);
            return;
        }

        this.initGraph();
    }

    initGraph() {
        // Check if mxGraph is loaded
        if (typeof mxGraph === 'undefined') {
            console.error('mxGraph is not loaded. Make sure mxClient.min.js is included.');
            return;
        }

        // Create graph
        this.container.innerHTML = '';
        this.graph = new mxGraph(this.container);

        // Configure graph
        this.graph.setCellsEditable(false);
        this.graph.setCellsSelectable(true);
        this.graph.setCellsMovable(true);
        this.graph.setConnectable(false);
        this.graph.setPanning(true);
        this.graph.setTooltips(true);

        // Enable panning with right mouse button
        this.graph.panningHandler.useLeftButtonForPanning = true;
        this.graph.panningHandler.usePopupTrigger = false;

        // Set default styles
        this.graph.getStylesheet().putDefaultVertexStyle(
            mxUtils.clone(this.graph.getStylesheet().getDefaultVertexStyle())
        );
        this.graph.getStylesheet().putDefaultEdgeStyle(
            mxUtils.clone(this.graph.getStylesheet().getDefaultEdgeStyle())
        );

        // Add panning
        new mxRubberband(this.graph);

        // Center and zoom
        this.centerGraph();
    }

    centerGraph() {
        if (!this.graph) return;
        this.graph.center(true, true, 0.1, 0.1);
        this.graph.zoomTo(0.8);
    }

    /**
     * Parse DrawIO XML and render it
     */
    renderFromXML(xmlString) {
        if (!this.graph) {
            console.error('Graph not initialized');
            return;
        }

        try {
            // Create XML document
            const parser = new DOMParser();
            const xmlDoc = parser.parseFromString(xmlString, "text/xml");

            // Get the mxGraphModel
            const modelNode = xmlDoc.getElementsByTagName('mxGraphModel')[0];
            if (!modelNode) {
                console.error('No mxGraphModel found in XML');
                return;
            }

            // Decode and render
            const codec = new mxCodec(xmlDoc);
            this.graph.getModel().beginUpdate();
            try {
                const node = codec.decode(modelNode);
                this.graph.getModel().setRoot(node);
            } finally {
                this.graph.getModel().endUpdate();
            }

            this.centerGraph();
            this.showContainer();

        } catch (error) {
            console.error('Error rendering DrawIO XML:', error);
            this.showError('Failed to render diagram');
        }
    }

    /**
     * Create a simple flow diagram from JSON data (fallback)
     */
    renderFromJSON(flowData) {
        if (!this.graph) {
            console.error('Graph not initialized');
            return;
        }

        try {
            const parent = this.graph.getDefaultParent();
            this.graph.getModel().beginUpdate();

            const processes = flowData.processes || [];
            const decisions = flowData.decisions || [];
            const vertexMap = {};

            let y = 50;
            const x = 400;

            // Chinese labels
            const startLabel = "开始";
            const endLabel = "结束";

            // Add Start node
            const startVertex = this.graph.insertVertex(
                parent, null, startLabel, x, y, 100, 50,
                'ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;fontSize=14;'
            );
            vertexMap[startLabel] = startVertex;
            y += 100;

            // Add process nodes
            let lastVertex = startVertex;
            for (const process of processes) {
                const name = process.name || "处理步骤";
                const vertex = this.graph.insertVertex(
                    parent, null, name, x, y, 160, 60,
                    'rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=13;'
                );
                vertexMap[name] = vertex;

                // Connect from previous node
                this.graph.insertEdge(
                    parent, null, '', lastVertex, vertex,
                    'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;'
                );
                lastVertex = vertex;
                y += 100;
            }

            // Add decision nodes
            const branchEnds = [];
            for (const decision of decisions) {
                const name = decision.name || "决策点";
                const vertex = this.graph.insertVertex(
                    parent, null, name, x, y, 120, 80,
                    'shape=decision;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;'
                );
                vertexMap[name] = vertex;

                // Connect from previous node
                this.graph.insertEdge(
                    parent, null, '', lastVertex, vertex,
                    'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;'
                );
                lastVertex = vertex;

                y += 80;

                // Add branches
                if (decision.true_branch) {
                    const trueName = decision.true_branch;
                    const trueVertex = this.graph.insertVertex(
                        parent, null, trueName, x - 150, y, 120, 50,
                        'rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;'
                    );
                    vertexMap[trueName] = trueVertex;
                    branchEnds.push(trueVertex);
                    // Connect "是" (Yes) branch
                    this.graph.insertEdge(
                        parent, null, '是', vertex, trueVertex,
                        'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;fontColor=#00CC00;fontStyle=1;'
                    );
                }

                if (decision.false_branch) {
                    const falseName = decision.false_branch;
                    const falseVertex = this.graph.insertVertex(
                        parent, null, falseName, x + 150, y, 120, 50,
                        'rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;'
                    );
                    vertexMap[falseName] = falseVertex;
                    branchEnds.push(falseVertex);
                    // Connect "否" (No) branch
                    this.graph.insertEdge(
                        parent, null, '否', vertex, falseVertex,
                        'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;fontColor=#CC0000;fontStyle=1;'
                    );
                }
                y += 80;
            }

            // Add End node
            if (branchEnds.length > 0) {
                y += 50;
            }

            const endVertex = this.graph.insertVertex(
                parent, null, endLabel, x, y, 100, 50,
                'ellipse;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontStyle=1;fontSize=14;'
            );

            // Connect to end
            if (branchEnds.length > 0) {
                // Connect all branch ends to end node
                for (const branchEnd of branchEnds) {
                    this.graph.insertEdge(
                        parent, null, '', branchEnd, endVertex,
                        'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;'
                    );
                }
            } else {
                // Direct connection
                this.graph.insertEdge(
                    parent, null, '', lastVertex, endVertex,
                    'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;'
                );
            }

            this.graph.getModel().endUpdate();
            this.centerGraph();
            this.showContainer();

        } catch (error) {
            console.error('Error rendering flow from JSON:', error);
            this.showError('Failed to render diagram');
        }
    }

    showContainer() {
        this.container.style.display = 'block';
        const placeholder = document.getElementById('flow-placeholder');
        if (placeholder) placeholder.style.display = 'none';
    }

    hideContainer() {
        this.container.style.display = 'none';
        const placeholder = document.getElementById('flow-placeholder');
        if (placeholder) placeholder.style.display = 'block';
    }

    showError(message) {
        this.container.innerHTML = `<div class="error-message">${message}</div>`;
    }

    clear() {
        if (this.graph) {
            this.graph.getModel().clear();
        }
        this.hideContainer();
    }

    exportToXML() {
        if (!this.graph) return null;

        const codec = new mxCodec();
        const model = this.graph.getModel();
        const node = codec.encode(model);
        return mxUtils.getXml(node);
    }
}

// Global instance
let drawioViewer = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    drawioViewer = new DrawIOViewer('drawio-canvas');
});
