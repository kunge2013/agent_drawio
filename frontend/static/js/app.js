/**
 * Main Application Module
 * Handles tab switching and export functionality
 */

class App {
    constructor() {
        this.currentTab = 'prototype';
        this.init();
    }

    init() {
        this.setupTabs();
        this.setupExportButtons();
    }

    setupTabs() {
        const tabButtons = document.querySelectorAll('.tab-btn');
        const panels = document.querySelectorAll('.panel');

        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const tabName = button.getAttribute('data-tab');
                this.switchTab(tabName);
            });
        });
    }

    switchTab(tabName) {
        // Remove active class from all tabs and panels
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelectorAll('.panel').forEach(panel => {
            panel.classList.remove('active');
        });

        // Add active class to selected tab and panel
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        document.getElementById(`${tabName}-panel`).classList.add('active');

        this.currentTab = tabName;
    }

    setupExportButtons() {
        // UI Flow export
        const uiFlowExport = document.getElementById('exportUiFlow');
        if (uiFlowExport) {
            uiFlowExport.addEventListener('click', () => {
                this.exportDiagram('ui_flow', 'ui_flow_diagram.drawio');
            });
        }

        // Business Flow export
        const businessFlowExport = document.getElementById('exportBusinessFlow');
        if (businessFlowExport) {
            businessFlowExport.addEventListener('click', () => {
                this.exportDiagram('business_flow', 'business_flow_diagram.drawio');
            });
        }

        // Documentation export
        const docExport = document.getElementById('exportDocumentation');
        if (docExport) {
            docExport.addEventListener('click', () => {
                this.exportDocumentation();
            });
        }
    }

    async exportDiagram(type, filename) {
        try {
            // Get diagram ID from chat module
            const diagramId = chat.currentDiagramIds[type];

            if (!diagramId) {
                throw new Error('No diagram available for export');
            }

            await api.exportDiagram(diagramId, filename);

            // Show success message
            this.showNotification('Diagram exported successfully!', 'success');

        } catch (error) {
            this.showNotification(`Export failed: ${error.message}`, 'error');
        }
    }

    exportDocumentation() {
        try {
            const content = document.getElementById('documentation-content').innerText;

            if (!content || content.includes('will appear here')) {
                throw new Error('No documentation available for export');
            }

            // Create blob and download
            const blob = new Blob([content], { type: 'text/markdown' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'design_documentation.md';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            this.showNotification('Documentation exported successfully!', 'success');

        } catch (error) {
            this.showNotification(`Export failed: ${error.message}`, 'error');
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            background: ${type === 'success' ? '#22c55e' : type === 'error' ? '#ef4444' : '#2563eb'};
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;

        // Add animation keyframes
        if (!document.getElementById('notification-styles')) {
            const style = document.createElement('style');
            style.id = 'notification-styles';
            style.textContent = `
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes fadeOut {
                    from { opacity: 1; }
                    to { opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }

        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new App();
    });
} else {
    new App();
}

// Export for access from other modules
if (typeof window !== 'undefined') {
    window.App = App;
}
