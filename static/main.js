document.addEventListener('DOMContentLoaded', () => {
    // Chat UI elements
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");

    // Modal UI elements
    const modal = document.getElementById('fir-modal');
    const openModalBtn = document.getElementById('open-modal-btn');
    const closeModalBtn = document.getElementById('close-modal-btn');
    const cancelModalBtn = document.getElementById('cancel-modal-btn');
    const generateBtn = document.getElementById('generate-fir-btn');
    const firDescription = document.getElementById('fir-description');
    const modalStatus = document.getElementById('modal-status');

    // Chat Logic
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        appendMessage(message, "user");
        userInput.value = "";
        userInput.disabled = true;
        sendBtn.disabled = true;

        const loadingId = appendLoading();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });

            const data = await response.json();
            removeMessage(loadingId);
            
            if (response.ok) {
                appendMessage(data.response, "bot");
            } else {
                appendMessage(`Error: ${data.detail || "Failed to get response"}`, "bot");
            }
        } catch (error) {
            removeMessage(loadingId);
            appendMessage("Error: Could not connect to the server.", "bot");
        } finally {
            userInput.disabled = false;
            sendBtn.disabled = false;
            userInput.focus();
        }
    }

    function appendMessage(text, sender) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}-message`;

        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.innerHTML = sender === 'bot' ? '<i class="fa-solid fa-robot"></i>' : '<i class="fa-solid fa-user"></i>';

        const textDiv = document.createElement('div');
        textDiv.className = 'text';
        
        if(sender === 'bot') {
            textDiv.innerHTML = marked.parse(text);
        } else {
            textDiv.textContent = text;
        }

        msgDiv.appendChild(avatar);
        msgDiv.appendChild(textDiv);
        chatBox.appendChild(msgDiv);
        scrollToBottom();
    }

    function appendLoading() {
        const id = 'loading-' + Date.now();
        const msgDiv = document.createElement('div');
        msgDiv.className = `message bot-message`;
        msgDiv.id = id;
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.innerHTML = '<i class="fa-solid fa-robot"></i>';
        const textDiv = document.createElement('div');
        textDiv.className = 'text';
        textDiv.innerHTML = '<i class="fa-solid fa-ellipsis fa-bounce"></i> Thinking...';
        msgDiv.appendChild(avatar);
        msgDiv.appendChild(textDiv);
        chatBox.appendChild(msgDiv);
        scrollToBottom();
        return id;
    }

    function removeMessage(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function scrollToBottom() {
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Modal Logic
    openModalBtn.addEventListener('click', () => {
        modal.classList.add('active');
        firDescription.focus();
    });

    const closeModal = () => {
        modal.classList.remove('active');
        firDescription.value = '';
        modalStatus.className = 'status-msg hidden';
    };

    closeModalBtn.addEventListener('click', closeModal);
    cancelModalBtn.addEventListener('click', closeModal);

    generateBtn.addEventListener('click', async () => {
        const desc = firDescription.value.trim();
        if(!desc) {
            modalStatus.innerHTML = "Please enter an incident description.";
            modalStatus.className = "status-msg error";
            return;
        }

        generateBtn.disabled = true;
        generateBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Generating...';
        modalStatus.innerHTML = "Querying legal AI and drafting PDF...";
        modalStatus.className = "status-msg loading";

        try {
            const response = await fetch('/api/draft_fir', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ incident_description: desc })
            });

            if(response.ok) {
                // Handle PDF Download
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = 'FIR_Draft.pdf';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                closeModal();
            } else {
                const errorData = await response.json();
                modalStatus.innerHTML = `Error: ${errorData.detail || 'Could not generate FIR.'}`;
                modalStatus.className = "status-msg error";
            }
        } catch(e) {
            modalStatus.innerHTML = "Network error. Please try again.";
            modalStatus.className = "status-msg error";
        } finally {
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<i class="fa-solid fa-file-export"></i> Generate PDF';
        }
    });
});
