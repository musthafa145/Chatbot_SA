// Get references to input, button, and chat container
const inputBox = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const chatContainer = document.querySelector(".chat-container");

// Function to add a message to chat container
function addMessage(message, sender = "user") {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", sender); // class: user or bot
    messageDiv.textContent = message;
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight; // auto scroll
}

// When send button is clicked
sendButton.addEventListener("click", () => {
    const message = inputBox.value.trim();
    if (message === "") return;

    // Show user message
    addMessage(message, "user");
    console.log("User message:", message);

    inputBox.value = ""; // clear input

    // Dummy bot reply after 1 second
    setTimeout(() => {
        addMessage("I am thinking...", "bot");
    }, 1000);
});
