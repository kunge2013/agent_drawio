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
        this.currentDiagramIds = {
            ui_flow: null,
            business_flow: null
        };

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

            // Update generated content panels
            this.updateContentPanels(response.generated_content);

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
            this.currentDiagramIds = { ui_flow: null, business_flow: null };

            // Clear chat messages except welcome
            this.messagesContainer.innerHTML = `
                <div class="message bot">
                    <div class="message-content">
                        Started a new conversation. Describe your product requirements
                        and I'll help you create prototypes, UI flows, and business process diagrams.
                    </div>
                </div>
            `;

            // Clear content panels
            this.clearContentPanels();

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
                <span style="margin-left: 8px;">AI is thinking...</span>
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

    updateContentPanels(content) {
        // Update prototype panel
        if (content.prototype) {
            document.getElementById('prototype-content').innerHTML =
                this.formatMessage(content.prototype);
        }

        // Update UI flow panel
        if (content.ui_flow) {
            const uiContent = document.getElementById('ui-flow-content');
            uiContent.innerHTML = `
                <p>${content.ui_flow.preview || 'UI flow diagram generated'}</p>
                <div style="margin-top: 12px; padding: 12px; background: #f1f5f9; border-radius: 8px;">
                    <small style="color: #64748b;">Diagram ready for export</small>
                </div>
            `;

            // Store diagram ID for export
            if (content.ui_flow.diagram_id) {
                this.currentDiagramIds.ui_flow = content.ui_flow.diagram_id;
                document.getElementById('exportUiFlow').style.display = 'block';
            }
        }

        // Update business flow panel
        if (content.business_flow) {
            const businessContent = document.getElementById('business-flow-content');
            businessContent.innerHTML = `
                <p>${content.business_flow.preview || 'Business flow diagram generated'}</p>
                <div style="margin-top: 12px; padding: 12px; background: #f1f5f9; border-radius: 8px;">
                    <small style="color: #64748b;">Diagram ready for export</small>
                </div>
            `;

            // Store diagram ID for export
            if (content.business_flow.diagram_id) {
                this.currentDiagramIds.business_flow = content.business_flow.diagram_id;
                document.getElementById('exportBusinessFlow').style.display = 'block';
            }
        }

        // Update documentation panel
        if (content.documentation) {
            document.getElementById('documentation-content').innerHTML =
                this.renderMarkdown(content.documentation);
            document.getElementById('exportDocumentation').style.display = 'block';
        }
    }

    clearContentPanels() {
        document.getElementById('prototype-content').innerHTML =
            '<p class="placeholder">Prototype design will appear here after you send a message.</p>';
        document.getElementById('ui-flow-content').innerHTML =
            '<p class="placeholder">UI flow diagram will appear here.</p>';
        document.getElementById('business-flow-content').innerHTML =
            '<p class="placeholder">Business flow diagram will appear here.</p>';
        document.getElementById('documentation-content').innerHTML =
            '<p class="placeholder">Design documentation will appear here.</p>';

        document.getElementById('exportUiFlow').style.display = 'none';
        document.getElementById('exportBusinessFlow').style.display = 'none';
        document.getElementById('exportDocumentation').style.display = 'none';
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

    renderMarkdown(text) {
        // Escape HTML first
        let formatted = this.escapeHtml(text);

        // Headers
        formatted = formatted.replace(/^#### (.+)$/gm, '<h4>$1</h4>');
        formatted = formatted.replace(/^### (.+)$/gm, '<h3>$1</h3>');
        formatted = formatted.replace(/^## (.+)$/gm, '<h2>$1</h2>');
        formatted = formatted.replace(/^# (.+)$/gm, '<h1>$1</h1>');

        // Bold and italic
        formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        formatted = formatted.replace(/\*(.+?)\*/g, '<em>$1</em>');

        // Code blocks
        formatted = formatted.replace(/```(\w+)?\n([\s\S]+?)```/g, '<pre><code>$2</code></pre>');
        formatted = formatted.replace(/`(.+?)`/g, '<code>$1</code>');

        // Lists
        formatted = formatted.replace(/^\* (.+)$/gm, '<li>$1</li>');
        formatted = formatted.replace(/^(\d+)\. (.+)$/gm, '<li>$2</li>');
        formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

        // Line breaks
        formatted = formatted.replace(/\n\n/g, '</p><p>');
        formatted = '<p>' + formatted + '</p>';

        // Clean up empty paragraphs
        formatted = formatted.replace(/<p>\s*<\/p>/g, '');

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
