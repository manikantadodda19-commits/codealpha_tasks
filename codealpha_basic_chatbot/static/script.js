/**
 * ChatBuddy - Interactive Chatbot Frontend
 * Handles messaging, animations, themes, and particle effects
 */

// ─── DOM Elements ──────────────────────────────────────────────────────────
const chatMessages = document.getElementById("chatMessages");
const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const themeToggle = document.getElementById("themeToggle");
const themeIcon = document.getElementById("themeIcon");
const clearChatBtn = document.getElementById("clearChat");
const welcomeCard = document.getElementById("welcomeCard");
const welcomeChips = document.getElementById("welcomeChips");
const suggestionBar = document.getElementById("suggestionBar");
const statusLabel = document.getElementById("statusLabel");
const headerStatus = document.getElementById("headerStatus");
const particlesContainer = document.getElementById("particles");

// ─── State ─────────────────────────────────────────────────────────────────
let isTyping = false;
let messageCount = 0;

// ─── Initialize ────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    createParticles();
    loadSuggestions();
    messageInput.focus();
});

// ─── Theme Toggle ──────────────────────────────────────────────────────────
function initTheme() {
    const savedTheme = localStorage.getItem("chatbuddy-theme") || "dark";
    document.documentElement.setAttribute("data-theme", savedTheme);
    themeIcon.textContent = savedTheme === "dark" ? "🌙" : "☀️";
}

themeToggle.addEventListener("click", () => {
    const currentTheme = document.documentElement.getAttribute("data-theme");
    const newTheme = currentTheme === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", newTheme);
    localStorage.setItem("chatbuddy-theme", newTheme);
    themeIcon.textContent = newTheme === "dark" ? "🌙" : "☀️";

    // Fun animation on toggle
    themeToggle.style.transform = "rotate(360deg)";
    setTimeout(() => { themeToggle.style.transform = ""; }, 400);
});

// ─── Particle System ───────────────────────────────────────────────────────
function createParticles() {
    const colors = [
        "hsla(250, 85%, 60%, 0.15)",
        "hsla(185, 90%, 55%, 0.12)",
        "hsla(280, 80%, 55%, 0.1)",
        "hsla(320, 80%, 55%, 0.08)",
    ];

    for (let i = 0; i < 25; i++) {
        const particle = document.createElement("div");
        particle.classList.add("particle");

        const size = Math.random() * 6 + 3;
        const color = colors[Math.floor(Math.random() * colors.length)];
        const left = Math.random() * 100;
        const duration = Math.random() * 15 + 10;
        const delay = Math.random() * 10;

        particle.style.cssText = `
            width: ${size}px;
            height: ${size}px;
            left: ${left}%;
            background: ${color};
            animation-duration: ${duration}s;
            animation-delay: ${delay}s;
        `;

        particlesContainer.appendChild(particle);
    }
}

// ─── Load Suggestion Chips ─────────────────────────────────────────────────
async function loadSuggestions() {
    try {
        const response = await fetch("/suggestions");
        const data = await response.json();
        const chips = data.suggestions;

        // Populate welcome card chips
        welcomeChips.innerHTML = "";
        chips.forEach((chip) => {
            const btn = createChipButton(chip);
            welcomeChips.appendChild(btn);
        });

        // Populate suggestion bar
        suggestionBar.innerHTML = "";
        chips.forEach((chip) => {
            const btn = createChipButton(chip);
            suggestionBar.appendChild(btn);
        });
    } catch (err) {
        console.error("Failed to load suggestions:", err);
        // Fallback chips
        const fallback = ["Hello 👋", "How are you?", "Tell me a joke", "Help", "Bye"];
        fallback.forEach((chip) => {
            welcomeChips.appendChild(createChipButton(chip));
            suggestionBar.appendChild(createChipButton(chip));
        });
    }
}

function createChipButton(text) {
    const btn = document.createElement("button");
    btn.className = "chip";
    btn.textContent = text;
    btn.addEventListener("click", () => {
        // Strip emoji for cleaner input
        const cleanText = text.replace(/[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}]/gu, "").trim();
        messageInput.value = cleanText;
        sendMessage();
    });
    return btn;
}

// ─── Send Message ──────────────────────────────────────────────────────────
async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message || isTyping) return;

    // Hide welcome card on first message
    if (welcomeCard) {
        welcomeCard.style.animation = "fadeOut 0.3s ease forwards";
        setTimeout(() => welcomeCard.remove(), 300);
    }

    // Add user message bubble
    addMessage(message, "user");
    messageInput.value = "";
    messageInput.focus();
    messageCount++;

    // Show typing indicator
    showTypingIndicator();

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: message }),
        });

        const data = await response.json();

        // Simulate realistic typing delay
        const delay = Math.min(600 + data.reply.length * 15, 2000);
        await sleep(delay);

        hideTypingIndicator();
        addMessage(data.reply, "bot", data.timestamp);

        // Celebration on milestones
        if (messageCount === 5) spawnEmojiRain("🎉");
        if (messageCount === 10) spawnEmojiRain("🌟");

    } catch (err) {
        hideTypingIndicator();
        addMessage("Oops! Something went wrong. Please try again. 😅", "bot");
        console.error("Chat error:", err);
    }
}

// ─── Add Message to Chat ───────────────────────────────────────────────────
function addMessage(text, sender, timestamp) {
    const now = timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    const row = document.createElement("div");
    row.className = `message-row ${sender}`;

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = sender === "bot" ? "🤖" : "🧑";

    const content = document.createElement("div");
    content.className = "message-content";

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";
    bubble.textContent = text;

    const time = document.createElement("span");
    time.className = "message-time";
    time.textContent = now;

    content.appendChild(bubble);
    content.appendChild(time);
    row.appendChild(avatar);
    row.appendChild(content);

    chatMessages.appendChild(row);
    scrollToBottom();

    // Haptic-like micro-animation on bubble
    bubble.style.animation = "popIn 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275) both";
}

// ─── Typing Indicator ──────────────────────────────────────────────────────
function showTypingIndicator() {
    isTyping = true;
    statusLabel.textContent = "Typing...";
    headerStatus.style.display = "inline-flex";

    const row = document.createElement("div");
    row.className = "message-row bot";
    row.id = "typingIndicator";

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = "🤖";

    const content = document.createElement("div");
    content.className = "message-content";

    const bubble = document.createElement("div");
    bubble.className = "message-bubble typing-bubble";
    bubble.innerHTML = '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';

    content.appendChild(bubble);
    row.appendChild(avatar);
    row.appendChild(content);

    chatMessages.appendChild(row);
    scrollToBottom();
}

function hideTypingIndicator() {
    isTyping = false;
    statusLabel.textContent = "Online";

    const indicator = document.getElementById("typingIndicator");
    if (indicator) {
        indicator.style.animation = "fadeOut 0.2s ease forwards";
        setTimeout(() => indicator.remove(), 200);
    }
}

// ─── Clear Chat ────────────────────────────────────────────────────────────
clearChatBtn.addEventListener("click", () => {
    // Animate messages out
    const messages = chatMessages.querySelectorAll(".message-row, .date-separator");
    messages.forEach((msg, i) => {
        msg.style.animation = `fadeOut 0.3s ease ${i * 0.05}s forwards`;
    });

    setTimeout(() => {
        chatMessages.innerHTML = "";
        messageCount = 0;

        // Re-add welcome card
        const welcome = document.createElement("div");
        welcome.className = "welcome-card";
        welcome.id = "welcomeCard";
        welcome.innerHTML = `
            <div class="welcome-emoji bounce-in">🤖</div>
            <h2 class="welcome-title fade-in">Welcome back!</h2>
            <p class="welcome-text fade-in delay-1">Chat cleared! Ready for a fresh conversation. 🚀</p>
            <div class="welcome-chips fade-in delay-2" id="welcomeChips"></div>
        `;
        chatMessages.appendChild(welcome);

        // Reload chips
        loadSuggestions();
    }, messages.length * 50 + 350);
});

// ─── Event Listeners ───────────────────────────────────────────────────────
sendBtn.addEventListener("click", sendMessage);

messageInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Input glow effect on typing
messageInput.addEventListener("input", () => {
    if (messageInput.value.trim()) {
        sendBtn.style.boxShadow = "0 6px 24px hsla(260, 80%, 50%, 0.5)";
    } else {
        sendBtn.style.boxShadow = "";
    }
});

// ─── Emoji Rain Celebration ────────────────────────────────────────────────
function spawnEmojiRain(emoji) {
    for (let i = 0; i < 15; i++) {
        setTimeout(() => {
            const el = document.createElement("div");
            el.className = "emoji-rain";
            el.textContent = emoji;
            el.style.left = Math.random() * 100 + "vw";
            el.style.animationDuration = (Math.random() * 2 + 1.5) + "s";
            el.style.fontSize = (Math.random() * 1.5 + 1) + "rem";
            document.body.appendChild(el);
            setTimeout(() => el.remove(), 4000);
        }, i * 100);
    }
}

// ─── Utilities ─────────────────────────────────────────────────────────────
function scrollToBottom() {
    requestAnimationFrame(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    });
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Add fadeOut keyframe dynamically
const style = document.createElement("style");
style.textContent = `@keyframes fadeOut { to { opacity: 0; transform: translateY(-10px) scale(0.95); } }`;
document.head.appendChild(style);
