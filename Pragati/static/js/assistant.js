const form = document.getElementById("assistant-form");
const input = document.getElementById("assistant-message");
const log = document.getElementById("chat-log");
const language = document.getElementById("assistant-language");
const status = document.getElementById("voice-status");
let lastReply = "";

const replies = {
  en: {
    water: "Check soil moisture before watering. Water needs depend on crop type, growth stage, soil, and weather.",
    yellow: "Yellow leaves can have several causes, including watering stress, nutrient issues, pests, or normal aging. Check which leaves are affected and record the pattern.",
    pest: "Inspect both sides of leaves and young shoots. Identify the pest before selecting a control method; consider integrated pest management.",
    default: "Please describe the crop, growth stage, and symptoms. Record observations in the Crop Health Passport and consult a local agricultural expert if symptoms spread."
  },
  hi: {
    water: "Paani dene se pehle mitti ki nami check karein. Paani ki zaroorat fasal, growth stage, mitti aur mausam par depend karti hai.",
    yellow: "Peeli pattiyon ke kai kaaran ho sakte hain, jaise paani ka stress, nutrients ki kami, keede ya purani pattiyan. Pattern note karein.",
    pest: "Pattiyon ke dono taraf aur naye shoots par keede dekhein. Control method chunne se pehle keede ki pehchan karein.",
    default: "Fasal ka naam, growth stage aur symptoms batayein. Observation Crop Health Passport mein record karein aur zaroorat par local agriculture expert se salah lein."
  }
};
function chooseReply(message, lang) {
  const m = message.toLowerCase();
  const pack = replies[lang] || replies.en;
  if (m.includes("water") || m.includes("paani") || m.includes("पानी") || m.includes("irrigation")) return pack.water;
  if (m.includes("yellow") || m.includes("peeli") || m.includes("पीली")) return pack.yellow;
  if (m.includes("pest") || m.includes("insect") || m.includes("keede") || m.includes("कीड़े")) return pack.pest;
  return pack.default;
}
function addBubble(text, kind) {
  const div = document.createElement("div");
  div.className = "chat-bubble " + kind;
  div.textContent = text;
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
}
if (form) form.addEventListener("submit", event => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message) return;
  addBubble(message, "user");
  lastReply = chooseReply(message, language.value);
  addBubble(lastReply, "bot");
  input.value = "";
});
const speak = text => {
  if (!("speechSynthesis" in window)) {
    status.textContent = "Speech output is not supported in this browser.";
    return;
  }
  const utterance = new SpeechSynthesisUtterance(text);
  const langMap = {en:"en-US", hi:"hi-IN", pa:"pa-IN", bn:"bn-IN", ta:"ta-IN", te:"te-IN", mr:"mr-IN", ur:"ur-PK", gu:"gu-IN", ar:"ar-SA", fr:"fr-FR", es:"es-ES"};
  utterance.lang = langMap[language.value] || "en-US";
  window.speechSynthesis.speak(utterance);
};
document.getElementById("speak-last")?.addEventListener("click", () => {
  if (lastReply) speak(lastReply);
  else status.textContent = "Send a question first.";
});
document.getElementById("voice-input")?.addEventListener("click", () => {
  const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!Recognition) {
    status.textContent = "Voice input is not supported in this browser. Please type instead.";
    return;
  }
  const recognition = new Recognition();
  const langMap = {en:"en-US", hi:"hi-IN", pa:"pa-IN", bn:"bn-IN", ta:"ta-IN", te:"te-IN", mr:"mr-IN", ur:"ur-PK", gu:"gu-IN", ar:"ar-SA", fr:"fr-FR", es:"es-ES"};
  recognition.lang = langMap[language.value] || "en-US";
  recognition.onstart = () => status.textContent = "Listening…";
  recognition.onerror = () => status.textContent = "Voice input failed. Try typing your question.";
  recognition.onresult = event => {
    input.value = event.results[0][0].transcript;
    status.textContent = "Voice captured. Press Send.";
    input.focus();
  };
  recognition.onend = () => { if (status.textContent === "Listening…") status.textContent = ""; };
  recognition.start();
});
