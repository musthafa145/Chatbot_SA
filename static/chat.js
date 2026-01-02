const inputBox = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const chatContainer = document.querySelector(".chat-container");

/* ===== Add message bubble ===== */
function addMessage(message, sender = "user") {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", sender);
    messageDiv.textContent = message;
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

/* ===== Typing indicator ===== */
function addTypingIndicator() {
    const typingDiv = document.createElement("div");
    typingDiv.classList.add("message", "bot");

    const typingInner = document.createElement("div");
    typingInner.classList.add("typing");
    typingInner.innerHTML = "<span></span><span></span><span></span>";

    typingDiv.appendChild(typingInner);
    chatContainer.appendChild(typingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    return typingDiv;
}

/* ===== Send message logic ===== */
async function sendMessage() {
    const message = inputBox.value.trim();
    if (message === "") return;

    // Remove empty state on first message
    const emptyState = document.querySelector(".empty-state");
    if (emptyState) emptyState.remove();

    addMessage(message, "user");
    inputBox.value = "";

    const typingIndicator = addTypingIndicator();

    try {
        // Small delay for realistic typing feel
        await new Promise(resolve => setTimeout(resolve, 800));

        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });

        const data = await response.json();

        chatContainer.removeChild(typingIndicator);
        addMessage(data.reply, "bot");

    } catch (error) {
        chatContainer.removeChild(typingIndicator);
        addMessage("Server error. Try again.", "bot");
    }
}

/* ===== Button click ===== */
sendButton.addEventListener("click", sendMessage);

/* ===== Enter key support ===== */
inputBox.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        sendMessage();
    }
});
