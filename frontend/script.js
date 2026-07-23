const API_BASE_URL = "";
const SESSION_STORAGE_KEY = "rankridge_chat_id";

let currentChatId = getOrCreateSessionChatId();
let isStreaming = false;
let currentAbortController = null;

const chatMessages = document.getElementById("chat-messages");
const messageInput = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");


function generateChatId() {
  return "chat_" + Date.now();
}


function getOrCreateSessionChatId() {
  // sessionStorage survives page reloads/navigation within the same tab,
  // but clears automatically when the tab/browser closes — so a returning
  // visitor always starts a brand new conversation.
  const existingId = sessionStorage.getItem(SESSION_STORAGE_KEY);

  if (existingId) {
    return existingId;
  }

  const newId = generateChatId();
  sessionStorage.setItem(SESSION_STORAGE_KEY, newId);
  return newId;
}


function getEmptyStateHTML() {
  return `
    <div id="empty-state" class="empty-state">
      <h1>How can I help you today?</h1>
      <p>Start a new conversation by typing a message below.</p>
    </div>
  `;
}


function showEmptyState() {
  chatMessages.innerHTML = getEmptyStateHTML();
}


function formatMessageContent(content) {
  if (!content) return "";
  return marked.parse(content);
}


function enhanceCodeBlocks(container) {
  const codeBlocks = container.querySelectorAll("pre");

  codeBlocks.forEach((pre) => {
    if (pre.parentElement.classList.contains("code-block-wrapper")) {
      return;
    }

    const wrapper = document.createElement("div");
    wrapper.classList.add("code-block-wrapper");

    const copyBtn = document.createElement("button");
    copyBtn.classList.add("copy-code-btn");
    copyBtn.textContent = "Copy";

    copyBtn.addEventListener("click", async () => {
      const codeText = pre.innerText;

      try {
        await navigator.clipboard.writeText(codeText);
        copyBtn.textContent = "Copied!";
        copyBtn.classList.add("copied");

        setTimeout(() => {
          copyBtn.textContent = "Copy";
          copyBtn.classList.remove("copied");
        }, 1500);
      } catch (error) {
        console.error("Failed to copy code:", error);
      }
    });

    pre.parentNode.insertBefore(wrapper, pre);
    wrapper.appendChild(copyBtn);
    wrapper.appendChild(pre);
  });
}


function renderAssistantContent(container, content) {
  container.innerHTML = `<div class="message-content">${formatMessageContent(content)}</div>`;
  enhanceCodeBlocks(container);
}


// The assistant message wraps a logo avatar next to a bubble. Streaming and
// rendering must target the bubble, never the whole message (which would wipe
// the avatar). This helper returns the correct render target for any message.
function getRenderTarget(messageDiv) {
  return messageDiv.querySelector(".msg-bubble") || messageDiv;
}


function addMessageToUI(role, content) {
  const emptyState = document.getElementById("empty-state");
  if (emptyState) {
    emptyState.remove();
  }

  const messageDiv = document.createElement("div");
  messageDiv.classList.add("message");
  messageDiv.dataset.role = role;

  if (role === "user") {
    messageDiv.classList.add("user-message");
    messageDiv.innerHTML = `<div class="message-content"></div>`;
    messageDiv.querySelector(".message-content").textContent = content;
  } else {
    messageDiv.classList.add("assistant-message");

    const avatar = document.createElement("img");
    avatar.classList.add("msg-avatar");
    avatar.src = "/static/assets/rankridge-icon.png";
    avatar.alt = "Rankridge";

    const bubble = document.createElement("div");
    bubble.classList.add("msg-bubble");

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(bubble);
    renderAssistantContent(bubble, content);
  }

  chatMessages.appendChild(messageDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;

  return messageDiv;
}


function setInputState(disabled) {
  messageInput.disabled = disabled;

  if (!isStreaming) {
    sendBtn.disabled = disabled;
  }
}


function setSendButtonToStopMode() {
  sendBtn.textContent = "Stop";
  sendBtn.classList.add("stop-btn-active");
}


function setSendButtonToSendMode() {
  sendBtn.textContent = "Send";
  sendBtn.classList.remove("stop-btn-active");
}


function autoResizeTextarea() {
  messageInput.style.height = "auto";
  messageInput.style.height = messageInput.scrollHeight + "px";
}


function stopStreaming() {
  if (currentAbortController) {
    currentAbortController.abort();
  }
}


async function streamAssistantResponse({
  endpoint,
  payload,
  assistantMessageDiv
}) {
  currentAbortController = new AbortController();

  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload),
    signal: currentAbortController.signal
  });

  const bubble = getRenderTarget(assistantMessageDiv);

  if (!response.body) {
    bubble.innerHTML = `<div class="message-content">No response body received.</div>`;
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");

  let fullText = "";
  let firstChunkReceived = false;

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value, { stream: true });

    if (!firstChunkReceived) {
      bubble.innerHTML = "";
      firstChunkReceived = true;
    }

    fullText += chunk;
    renderAssistantContent(bubble, fullText);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
}


async function loadSessionHistory(chatId) {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/${chatId}`);

    if (!response.ok) {
      showEmptyState();
      return;
    }

    const messages = await response.json();

    if (!messages.length) {
      showEmptyState();
      return;
    }

    chatMessages.innerHTML = "";
    messages.forEach((message) => {
      addMessageToUI(message.role, message.content);
    });
  } catch (error) {
    console.error("Error loading session history:", error);
    showEmptyState();
  }
}


async function startUserMessage(chatId, message) {
  const response = await fetch(`${API_BASE_URL}/chat/start`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      chat_id: chatId,
      message: message
    })
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);
    throw new Error(errorBody?.detail || "Failed to start chat message");
  }

  return response.json();
}


async function sendMessage() {
  const message = messageInput.value.trim();

  if (!message || isStreaming) return;

  isStreaming = true;

  setInputState(true);
  setSendButtonToStopMode();

  messageInput.value = "";
  messageInput.style.height = "auto";

  let assistantMessageDiv = null;

  try {
    await startUserMessage(currentChatId, message);

    addMessageToUI("user", message);

    assistantMessageDiv = addMessageToUI("assistant", "Thinking...");

    await streamAssistantResponse({
      endpoint: `${API_BASE_URL}/chat/stream`,
      payload: {
        chat_id: currentChatId,
        message: message
      },
      assistantMessageDiv
    });
  } catch (error) {
    console.error(error);

    if (!assistantMessageDiv) {
      addMessageToUI("assistant", error.message || "Error starting message.");
    } else if (error.name === "AbortError") {
      getRenderTarget(assistantMessageDiv).innerHTML = `<div class="message-content"><em>Response stopped.</em></div>`;
    } else {
      getRenderTarget(assistantMessageDiv).innerHTML = `<div class="message-content">Error connecting to backend.</div>`;
    }
  } finally {
    isStreaming = false;
    currentAbortController = null;
    setInputState(false);
    setSendButtonToSendMode();
    messageInput.focus();
  }
}


sendBtn.addEventListener("click", () => {
  if (isStreaming) {
    stopStreaming();
  } else {
    sendMessage();
  }
});

messageInput.addEventListener("input", autoResizeTextarea);

messageInput.addEventListener("keydown", function (event) {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();

    if (!isStreaming) {
      sendMessage();
    }
  }
});

loadSessionHistory(currentChatId);
messageInput.focus();
