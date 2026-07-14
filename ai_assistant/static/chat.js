document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("chat-form");
  const input = document.getElementById("message-input");
  const messages = document.getElementById("messages");

  function addMessage(text, className) {
    const message = document.createElement("div");
    message.className = className;
    message.textContent = text;
    messages.appendChild(message);
    messages.scrollTop = messages.scrollHeight;
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const userMessage = input.value.trim();
    if (!userMessage) return;

    addMessage(userMessage, "user-message");
    input.value = "";

    try {
      const response = await fetch("/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: userMessage }),
      });

      const data = await response.json();
      addMessage(data.reply || "No reply received.", "assistant-message");
    } catch (error) {
      addMessage("Error talking to the server.", "assistant-message");
      console.error("Chat error:", error);
    }
  });
});