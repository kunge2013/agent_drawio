/**
 * API Client for DrawIO Agent
 * Handles all communication with the backend API
 */

const API_BASE = '/api/v1';

const api = {
    /**
     * Send a message to the AI and get response
     * @param {string} message - User message content
     * @param {number|null} conversationId - Conversation ID (null for new conversation)
     * @returns {Promise<Object>} Response with message and generated content
     */
    async sendMessage(message, conversationId = null) {
        const response = await fetch(`${API_BASE}/chat/message`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                conversation_id: conversationId
            })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Failed to send message');
        }

        return await response.json();
    },

    /**
     * Create a new conversation
     * @returns {Promise<Object>} New conversation data
     */
    async newConversation() {
        const response = await fetch(`${API_BASE}/chat/conversation`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title: 'New Conversation'
            })
        });

        if (!response.ok) {
            throw new Error('Failed to create conversation');
        }

        return await response.json();
    },

    /**
     * Get conversation details
     * @param {number} conversationId - Conversation ID
     * @returns {Promise<Object>} Conversation data
     */
    async getConversation(conversationId) {
        const response = await fetch(`${API_BASE}/chat/conversation/${conversationId}`);

        if (!response.ok) {
            throw new Error('Failed to fetch conversation');
        }

        return await response.json();
    },

    /**
     * Export diagram as DrawIO file
     * @param {number} diagramId - Diagram ID to export
     * @param {string} filename - Filename for download
     */
    async exportDiagram(diagramId, filename = 'diagram.drawio') {
        const response = await fetch(`${API_BASE}/export/drawio/${diagramId}`);

        if (!response.ok) {
            throw new Error('Failed to export diagram');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    },

    /**
     * Get all diagrams for a design
     * @param {number} designId - Design ID
     * @returns {Promise<Object>} Design with diagrams
     */
    async getDesignDiagrams(designId) {
        const response = await fetch(`${API_BASE}/export/design/${designId}/all`);

        if (!response.ok) {
            throw new Error('Failed to fetch design diagrams');
        }

        return await response.json();
    },

    /**
     * Check API health
     * @returns {Promise<Object>} Health status
     */
    async healthCheck() {
        const response = await fetch(`${API_BASE}/`);

        if (!response.ok) {
            throw new Error('Health check failed');
        }

        return await response.json();
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
}
