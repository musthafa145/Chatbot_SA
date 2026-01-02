const inputBox = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const chatContainer = document.querySelector(".chat-container");
const chatHistory = document.querySelector(".chat-history");
const newChatBtn = document.querySelector(".new-chat-btn");

/* ----------------- STATE ----------------- */
let conversations = {};
let activeChatId = null;
let chatCount = 1;

/* ----------------- INIT ----------------- */
createNewChat();

/* ----------------- CHAT FUNCTIONS ----------------- */

function createNewChat() {
    const chatId = "chat_" + Date.now();
    conversations[chatId] = [];
    activeChatId = chatId;

    renderSidebar(`Chat ${chatCount++}`, chatId);
    loadChat(chatId);
}

function renderSidebar(title, chatId) {
    const chatItem = document.createElement("div");
    chatItem.className = "chat-item active";
    chatItem.textContent = title;
    chatItem.dataset.chatId = chatId;

    chatItem.onclick = () => switchChat(chatId);

    // Remove active class from others
    document.querySelectorAll(".chat-item").forEach(i => i.classList.remove("active"));

    // Stack behavior (most recent on top)
    chatHistory.prepend(chatItem);
}

function switchChat(chatId) {
    activeChatId = chatId;

    document.querySelectorAll(".chat-item").forEach(item => {
        item.classList.toggle("active", item.dataset.chatId === chatId);
    });

    loadChat(chatId);

    // Move selected chat to top (MRU behavior)
    const selectedItem = document.querySelector(`[data-chat-id="${chatId}"]`);
    chatHistory.prepend(selectedItem);
}

function loadChat(chatId) {
    chatContainer.innerHTML = "";
    conversations[chatId].forEach(msg => {
        addMessage(msg.text, msg.sender, false);
    });
}

/* ----------------- MESSAGE FUNCTIONS ----------------- */

function addMessage(message, sender = "user", save = true) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", sender);
    messageDiv.textContent = message;
    chatContainer.appendChild(messageDiv);

    chatContainer.scrollTop = chatContainer.scrollHeight;

    if (save) {
        conversations[activeChatId].push({ sender, text: message });
    }
}

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

/* ----------------- EVENTS ----------------- */

sendButton.addEventListener("click", sendMessage);


// Auto-expand textarea
inputBox.addEventListener("input", () => {
    inputBox.style.height = "auto";
    inputBox.style.height = Math.min(inputBox.scrollHeight, 160) + "px";
});

inputBox.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
        if (e.shiftKey) {
            return; // allow new line
        }
        e.preventDefault(); // stop newline
        sendButton.click();
    }
});



newChatBtn.addEventListener("click", createNewChat);

async function sendMessage() {
    const message = inputBox.value.trim();
    if (!message) return;

    addMessage(message, "user");
    inputBox.value = "";

    const typing = addTypingIndicator();

    try {
        await new Promise(r => setTimeout(r, 700));

        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });

        const data = await response.json();

        chatContainer.removeChild(typing);
        addMessage(data.reply, "bot");

    } catch {
        chatContainer.removeChild(typing);
        addMessage("Server error.", "bot");
    }
}
