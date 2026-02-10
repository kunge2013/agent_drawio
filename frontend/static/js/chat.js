/**
 * Chat Interface Module
 * Handles chat message display and user interaction
 */

class ChatInterface {
    constructor() {
        this.messagesContainer = document.getElementById('chatMessages');
        this.userInput = document.getElementById('userInput');
        this.sendButton = document.getElementById('sendMessage');
        this.newConversationButton = document.getElementById('newConversation');
        this.currentConversationId = null;
        this.currentDiagramId = null;
        this.currentFlowXML = null;

        this.init();
    }

    init() {
        // Send message button click
        this.sendButton.addEventListener('click', () => this.sendMessage());

        // Enter key to send (Shift+Enter for new line)
        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // New conversation button
        this.newConversationButton.addEventListener('click', () => this.newConversation());

        // Auto-focus input
        this.userInput.focus();
    }

    async sendMessage() {
        const message = this.userInput.value.trim();
        if (!message) return;

        // Disable input while processing
        this.setInputEnabled(false);

        // Add user message to chat
        this.addMessage(message, 'user');
        this.userInput.value = '';

        // Show typing indicator
        this.showTypingIndicator();

        try {
            const response = await api.sendMessage(message, this.currentConversationId);

            // Update conversation ID
            this.currentConversationId = response.conversation_id;

            // Remove typing indicator
            this.hideTypingIndicator();

            // Add bot response
            this.addMessage(response.message, 'bot');

            // Update business flow diagram
            this.updateBusinessFlow(response.generated_content);

        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage(`Error: ${error.message}`, 'bot', true);
        } finally {
            // Re-enable input
            this.setInputEnabled(true);
            this.userInput.focus();
        }
    }

    async newConversation() {
        try {
            await api.newConversation();
            this.currentConversationId = null;
            this.currentDiagramId = null;
            this.currentFlowXML = null;

            // Clear chat messages except welcome
            this.messagesContainer.innerHTML = `
                <div class="message bot">
                    <div class="message-content">
                        Started a new conversation. Describe your business process
                        and I'll generate a professional flow diagram.
                    </div>
                </div>
            `;

            // Clear diagram
            if (drawioViewer) {
                drawioViewer.clear();
            }

            // Hide export button
            const exportBtn = document.getElementById('exportBusinessFlow');
            if (exportBtn) exportBtn.style.display = 'none';

        } catch (error) {
            this.addMessage(`Error: ${error.message}`, 'bot', true);
        }
    }

    addMessage(content, type, isError = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;

        const innerContent = this.formatMessage(content);
        messageDiv.innerHTML = `
            <div class="message-content ${isError ? 'error-message' : ''}">${innerContent}</div>
        `;

        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'message bot typing-indicator';
        indicator.id = 'typingIndicator';
        indicator.innerHTML = `
            <div class="message-content">
                <span class="loading-spinner"></span>
                <span style="margin-left: 8px;">AI is analyzing...</span>
            </div>
        `;
        this.messagesContainer.appendChild(indicator);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.remove();
        }
    }

    updateBusinessFlow(content) {
        if (!content || !content.business_flow) {
            return;
        }

        const businessFlow = content.business_flow;

        // Store diagram ID for export
        if (businessFlow.diagram_id) {
            this.currentDiagramId = businessFlow.diagram_id;
        }

        // Store XML for rendering and export
        if (businessFlow.xml) {
            this.currentFlowXML = businessFlow.xml;

            // Render the diagram using DrawIO viewer
            if (drawioViewer) {
                drawioViewer.renderFromXML(businessFlow.xml);
            }
        }

        // Show export button
        const exportBtn = document.getElementById('exportBusinessFlow');
        if (exportBtn) exportBtn.style.display = 'block';

        // Show text preview
        const previewDiv = document.getElementById('flow-preview');
        if (previewDiv && businessFlow.preview) {
            previewDiv.innerHTML = `
                <div class="flow-description">
                    <h4>Generated Flow Description</h4>
                    <p>${this.formatMessage(businessFlow.preview)}</p>
                </div>
            `;
            previewDiv.style.display = 'block';
        }
    }

    setInputEnabled(enabled) {
        this.userInput.disabled = !enabled;
        this.sendButton.disabled = !enabled;

        const btnText = this.sendButton.querySelector('.btn-text');
        const btnLoading = this.sendButton.querySelector('.btn-loading');

        if (enabled) {
            btnText.style.display = 'inline';
            btnLoading.style.display = 'none';
        } else {
            btnText.style.display = 'none';
            btnLoading.style.display = 'inline';
        }
    }

    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    formatMessage(text) {
        // Escape HTML
        let formatted = this.escapeHtml(text);

        // Basic formatting
        formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        formatted = formatted.replace(/\*(.+?)\*/g, '<em>$1</em>');
        formatted = formatted.replace(/`(.+?)`/g, '<code>$1</code>');
        formatted = formatted.replace(/\n/g, '<br>');

        return formatted;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize chat interface when DOM is ready
let chat;
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        chat = new ChatInterface();
    });
} else {
    chat = new ChatInterface();
}
