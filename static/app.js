const chatLog = document.getElementById("chat-log");
const chatForm = document.getElementById("chat-form");
const messageInput = document.getElementById("message-input");
const healthPill = document.getElementById("health-pill");
const voiceInputBtn = document.getElementById("voice-input-btn");
const voiceOutputBtn = document.getElementById("voice-output-btn");

let voiceOutputEnabled = true;
let recognition;

function addMessage(role, text, meta = "") {
    const article = document.createElement("article");
    article.className = `message ${role}`;
    article.textContent = text;

    if (meta) {
        const small = document.createElement("small");
        small.className = "message-meta";
        small.textContent = meta;
        article.appendChild(small);
    }

    chatLog.appendChild(article);
    chatLog.scrollTop = chatLog.scrollHeight;
}

async function checkHealth() {
    try {
        const response = await fetch("/api/health");
        const data = await response.json();
        healthPill.textContent = data.llm_enabled ? "LLM ulangan" : "Lokal rejim";
    } catch (error) {
        healthPill.textContent = "Server offline";
    }
}

function speak(text) {
    if (!voiceOutputEnabled || !("speechSynthesis" in window)) {
        return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "uz-UZ";
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
}

async function sendMessage(message) {
    addMessage("user", message, "Foydalanuvchi");
    messageInput.value = "";

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                message,
                speak_reply: voiceOutputEnabled,
            }),
        });

        if (!response.ok) {
            throw new Error("Server xatosi");
        }

        const data = await response.json();
        const meta = data.action ? `${data.source} | ${data.action.status}` : data.source;
        addMessage("assistant", data.reply, meta);
        speak(data.reply);
    } catch (error) {
        addMessage("assistant", "So'rov yuborishda xato yuz berdi. Backend ishga tushganini tekshiring.", "error");
    }
}

chatForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = messageInput.value.trim();
    if (!message) {
        return;
    }
    await sendMessage(message);
});

messageInput.addEventListener("keydown", async (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        chatForm.requestSubmit();
    }
});

document.querySelectorAll(".quick-btn").forEach((button) => {
    button.addEventListener("click", async () => {
        const command = button.dataset.command;
        await sendMessage(command);
    });
});

voiceOutputBtn.addEventListener("click", () => {
    voiceOutputEnabled = !voiceOutputEnabled;
    voiceOutputBtn.classList.toggle("active", voiceOutputEnabled);
    voiceOutputBtn.textContent = voiceOutputEnabled ? "Javobni o'qish" : "Ovoz o'chiq";
    if (!voiceOutputEnabled && "speechSynthesis" in window) {
        window.speechSynthesis.cancel();
    }
});

voiceInputBtn.addEventListener("click", () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        addMessage("assistant", "Bu brauzer voice input funksiyasini qo'llamaydi.", "voice");
        return;
    }

    if (!recognition) {
        recognition = new SpeechRecognition();
        recognition.lang = "uz-UZ";
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            messageInput.value = transcript;
        };

        recognition.onerror = () => {
            addMessage("assistant", "Voice input vaqtida xato bo'ldi.", "voice");
        };

        recognition.onend = () => {
            voiceInputBtn.textContent = "Tinglashni boshlash";
        };
    }

    voiceInputBtn.textContent = "Tinglanmoqda...";
    recognition.start();
});

addMessage(
    "assistant",
    "Assalomu alaykum. Men lokal AI yordamchingizman. Kod yozish, fayl yaratish, script ishga tushirish va brauzer buyruqlarini boshqarishga tayyorman.",
    "system",
);

checkHealth();
