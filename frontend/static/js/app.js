/**
 * Main Application Module
 * Handles export functionality
 */

class App {
    constructor() {
        this.init();
    }

    init() {
        this.setupExportButton();
    }

    setupExportButton() {
        // Business Flow export
        const businessFlowExport = document.getElementById('exportBusinessFlow');
        if (businessFlowExport) {
            businessFlowExport.addEventListener('click', () => {
                this.exportBusinessFlow();
            });
        }
    }

    exportBusinessFlow() {
        try {
            // Use the stored XML from chat module
            const xml = chat.currentFlowXML;

            if (!xml) {
                throw new Error('No diagram available for export');
            }

            // Create blob and download
            const blob = new Blob([xml], { type: 'application/xml' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `business_flow_${Date.now()}.drawio`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            this.showNotification('Diagram exported successfully!', 'success');

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
            font-size: 14px;
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
