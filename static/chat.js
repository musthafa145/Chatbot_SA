// Get references to input, button, and chat container
const inputBox = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const chatContainer = document.querySelector(".chat-container");

// Function to add a message to chat container
function addMessage(message, sender = "user") {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", sender); // user or bot
    messageDiv.textContent = message;
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Function to handle sending message
async function sendMessage() {
    const message = inputBox.value.trim();
    if (message === "") return;

    // Show user message
    addMessage(message, "user");
    inputBox.value = "";

    // Add typing indicator
    const typingDiv = document.createElement("div");
    typingDiv.classList.add("message", "bot");
    typingDiv.textContent = "Bot is typing...";
    chatContainer.appendChild(typingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    try {
        // Simulate typing delay (1 second)
        await new Promise(resolve => setTimeout(resolve, 1000));

        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();

        // Remove typing indicator
        chatContainer.removeChild(typingDiv);

        // Show bot reply
        addMessage(data.reply, "bot");

    } catch (error) {
        console.error("Error:", error);
        chatContainer.removeChild(typingDiv);
        addMessage("Error connecting to server.", "bot");
    }
}

// Send message on button click
sendButton.addEventListener("click", sendMessage);

// Send message on Enter key press
inputBox.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
        e.preventDefault(); // Prevent newline
        sendMessage();
    }
});
