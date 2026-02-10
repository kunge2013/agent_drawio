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
        this.graph.setCellsMovable(false);
        this.graph.setConnectable(false);

        // Enable tooltips
        this.graph.setTooltips(true);

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
            const xmlDoc = parser.parseFromString(xmlString, 'text/xml');

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
     * Create a simple flow diagram from JSON data
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
            const x = 250;

            // Add Start node
            const startVertex = this.graph.insertVertex(
                parent, null, 'Start', x, y, 100, 50,
                'rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;fontSize=14;'
            );
            vertexMap['Start'] = startVertex;
            y += 100;

            // Add process nodes
            processes.forEach(process => {
                const vertex = this.graph.insertVertex(
                    parent, null, process.name || 'Process', x, y, 160, 60,
                    'rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=13;'
                );
                vertexMap[process.name] = vertex;

                // Connect from previous node
                const vertexIds = Object.values(vertexMap);
                if (vertexIds.length > 1) {
                    this.graph.insertEdge(
                        parent, null, '', vertexIds[vertexIds.length - 2], vertex,
                        'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;'
                    );
                }
                y += 100;
            });

            // Add decision nodes
            decisions.forEach(decision => {
                const vertex = this.graph.insertVertex(
                    parent, null, decision.name || 'Decision', x, y, 120, 80,
                    'shape=decision;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;'
                );
                vertexMap[decision.name] = vertex;

                // Connect from previous node
                const vertexIds = Object.values(vertexMap);
                if (vertexIds.length > 1) {
                    this.graph.insertEdge(
                        parent, null, '', vertexIds[vertexIds.length - 2], vertex,
                        'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;'
                    );
                }

                y += 80;

                // Add branches
                if (decision.true_branch) {
                    const trueVertex = this.graph.insertVertex(
                        parent, null, decision.true_branch, x - 120, y, 100, 50,
                        'rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;'
                    );
                    vertexMap[decision.true_branch] = trueVertex;
                    this.graph.insertEdge(
                        parent, null, 'Yes', vertex, trueVertex,
                        'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;fontColor=#00CC00;fontStyle=1;'
                    );
                }

                if (decision.false_branch) {
                    const falseVertex = this.graph.insertVertex(
                        parent, null, decision.false_branch, x + 120, y, 100, 50,
                        'rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;'
                    );
                    vertexMap[decision.false_branch] = falseVertex;
                    this.graph.insertEdge(
                        parent, null, 'No', vertex, falseVertex,
                        'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;fontColor=#CC0000;fontStyle=1;'
                    );
                }
                y += 80;
            });

            // Add End node
            const endVertex = this.graph.insertVertex(
                parent, null, 'End', x, y, 100, 50,
                'rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontStyle=1;fontSize=14;'
            );

            // Connect from previous node
            const vertexIds = Object.values(vertexMap);
            if (vertexIds.length > 0) {
                this.graph.insertEdge(
                    parent, null, '', vertexIds[vertexIds.length - 1], endVertex,
                    'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;'
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

    exportToPNG(callback) {
        if (!this.graph) {
            callback(null);
            return;
        }

        try {
            const xml = this.exportToXML();
            if (!xml) {
                callback(null);
                return;
            }

            // Create canvas and export
            const canvas = document.createElement('canvas');
            const img = new Image();

            // Use mxGraph's built-in export
            const bounds = this.graph.getGraphBounds();
            const scale = 1;
            const width = Math.ceil(bounds.width * scale) + 1;
            const height = Math.ceil(bounds.height * scale) + 1;

            canvas.width = width;
            canvas.height = height;

            // Render to canvas
            const ctx = canvas.getContext('2d');
            ctx.scale(scale, scale);

            // Simple SVG-based export
            const svgXml = this.exportToSVG();
            if (svgXml) {
                const svgBlob = new Blob([svgXml], {type: 'image/svg+xml;charset=utf-8'});
                const url = URL.createObjectURL(svgBlob);
                callback(url);
            } else {
                callback(null);
            }

        } catch (error) {
            console.error('Error exporting to PNG:', error);
            callback(null);
        }
    }

    exportToSVG() {
        if (!this.graph) return null;

        try {
            const svgCanvas = this.graph.createSvg();
            return svgCanvas.getXml();
        } catch (error) {
            console.error('Error exporting to SVG:', error);
            return null;
        }
    }
}

// Global instance
let drawioViewer = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    drawioViewer = new DrawIOViewer('drawio-canvas');
});
