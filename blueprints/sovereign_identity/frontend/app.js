const DOM = {
    chatContainer: document.getElementById('chat-container'),
    userInput: document.getElementById('user-input'),
    sendBtn: document.getElementById('send-btn'),
    contextContent: document.getElementById('context-content'),
    librarianContent: document.getElementById('librarian-content'),
    copyContextBtn: document.getElementById('copy-context-btn')
};

// System State
let messageHistory = []; // Stores context payload

// --- Chat Logic ---

async function sendMessage() {
    const text = DOM.userInput.value.trim();
    if (!text) return;

    // UI Updates
    appendMessage('user', text);
    DOM.userInput.value = '';
    adjustTextareaHeight();

    // Update Context Panel (Scientific Mode)
    messageHistory.push({ role: "user", content: text });
    updateContextPanel();

    // Prepare Assistant Message Placeholder
    const assistantMsgDiv = appendMessage('assistant', '');
    let assistantText = "";

    try {
        const response = await fetch('/v1/chat/completions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                // Config will determine model on backend, or we can send it here.
                // Sending "gemini/gemini-pro" as per last test.
                model: "gemini/gemini-1.5-flash",
                messages: messageHistory,
                stream: true
            })
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Server Error ${response.status}: ${errorText}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const dataStr = line.replace('data: ', '').trim();
                    if (dataStr === '[DONE]') break;
                    try {
                        const data = JSON.parse(dataStr);
                        const content = data.choices[0]?.delta?.content || '';
                        assistantText += content;
                        assistantMsgDiv.textContent = assistantText; // Simple text render for now
                        // Scroll to bottom
                        DOM.chatContainer.scrollTop = DOM.chatContainer.scrollHeight;
                    } catch (e) {
                        console.warn("Stream parse error", e);
                    }
                }
            }
        }

    } catch (e) {
        assistantMsgDiv.textContent += `\n[Error: ${e.message}]`;
        assistantMsgDiv.style.color = "#ff4444";
    }

    // Finalize History
    messageHistory.push({ role: "assistant", content: assistantText });
    updateContextPanel();

    // Trigger memory refresh
    fetchMemory();
}

function appendMessage(role, text) {
    const div = document.createElement('div');
    div.classList.add('message', role);
    div.textContent = text;
    DOM.chatContainer.appendChild(div);
    DOM.chatContainer.scrollTop = DOM.chatContainer.scrollHeight;
    return div;
}

function updateContextPanel() {
    // Pretty print the messages array in the left panel
    DOM.contextContent.textContent = JSON.stringify(messageHistory, null, 2);
}

// --- Librarian Logic (Memory Polling) ---

async function fetchMemory() {
    try {
        const response = await fetch('/v1/memory');
        if (!response.ok) return;
        const memoryData = await response.json(); // Expecting list of cards

        DOM.librarianContent.innerHTML = "";

        if (memoryData.length === 0) {
            DOM.librarianContent.innerHTML = '<div class="placeholder">No active cards.</div>';
            return;
        }

        memoryData.forEach(card => {
            const el = document.createElement('div');
            el.className = 'log-entry';
            /* 
               Assuming card structure: { entity_id, bio, core_directive, etc. }
               Displaying raw-ish for scientific transparency
            */
            const summary = `[${card.entity_id}] P:${card.priority || 1}`;
            const details = document.createElement('div');
            details.textContent = JSON.stringify(card, null, 2);
            details.style.display = 'none'; // Click to expand? For now just dump summary + bio

            el.innerHTML = `
                <div style="color:#0f0; font-weight:bold">${summary}</div>
                <div style="color:#888">${card.bio || card.content || 'No content'}</div>
            `;
            DOM.librarianContent.appendChild(el);
        });

    } catch (e) {
        console.error("Librarian fetch failed:", e);
    }
}

// --- Utilities ---

function adjustTextareaHeight() {
    DOM.userInput.style.height = 'auto';
    DOM.userInput.style.height = DOM.userInput.scrollHeight + 'px';
}

// --- Event Listeners ---

DOM.sendBtn.addEventListener('click', sendMessage);

DOM.userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

DOM.userInput.addEventListener('input', adjustTextareaHeight);

// Toggle Scientific Mode (Ctrl+Shift+M)
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.shiftKey && e.key === 'M') {
        document.body.classList.toggle('scientific-mode');
        console.log("Mode toggled:", document.body.classList.contains('scientific-mode') ? "Scientific" : "User");
    }
});

// Copy Context
if (DOM.copyContextBtn) {
    DOM.copyContextBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(JSON.stringify(messageHistory, null, 2));
        alert("Context copied to clipboard");
    });
}

// --- Init ---
// Poll memory every 5s
setInterval(fetchMemory, 5000);
fetchMemory(); // Initial fetch
