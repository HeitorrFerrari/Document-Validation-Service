const analyzeForm = document.getElementById("analyze-form");
const analyzeButton = document.getElementById("analyze-button");
const analyzeStatus = document.getElementById("analyze-status");
const resultCard = document.getElementById("result-card");
const scoreBadge = document.getElementById("score-badge");
const eligibleBadge = document.getElementById("eligible-badge");
const reasoning = document.getElementById("reasoning");
const requirementScores = document.getElementById("requirement-scores");
const feedback = document.getElementById("feedback");
const sessionIdInput = document.getElementById("session-id");
const chatLog = document.getElementById("chat-log");
const chatForm = document.getElementById("chat-form");
const questionInput = document.getElementById("question");
const fileInput = document.getElementById("file");
const fileDrop = document.querySelector(".file-drop");
const fileTitle = document.getElementById("file-title");
const fileHint = document.getElementById("file-hint");
const metricScore = document.getElementById("metric-score");
const metricStatus = document.getElementById("metric-status");
const metricSession = document.getElementById("metric-session");

let chatMessages = [];
let pollTimer = null;

function splitSkills(value) {
  return value.split(",").map((skill) => skill.trim()).filter(Boolean);
}

function formatScore(value) {
  const score = Number(value);
  if (Number.isNaN(score)) return "--";
  return Number.isInteger(score) ? String(score) : score.toFixed(1);
}

function setStatus(message, tone = "neutral") {
  analyzeStatus.classList.remove("hidden", "error", "success");
  if (tone !== "neutral") analyzeStatus.classList.add(tone);
  analyzeStatus.textContent = message;
  metricStatus.textContent = message.replace(/\.+$/, "");
}

function clearChat() {
  chatMessages = [];
  chatLog.innerHTML = `
    <div class="empty-state">
      <strong>Nenhuma conversa iniciada</strong>
      <span>Após a análise, use o chat para entender score, critérios e próximos passos.</span>
    </div>
  `;
}

fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  fileDrop.classList.toggle("has-file", Boolean(file));
  fileTitle.textContent = file ? file.name : "Selecionar currículo";
  fileHint.textContent = file ? `${(file.size / 1024 / 1024).toFixed(2)} MB` : "PDF ou DOCX até o limite configurado no servidor";
});

analyzeForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (pollTimer) clearInterval(pollTimer);

  const job = {
    title: document.getElementById("title").value.trim(),
    description: document.getElementById("description").value.trim() || null,
    required_skills: splitSkills(document.getElementById("required_skills").value),
    desired_skills: splitSkills(document.getElementById("desired_skills").value),
    min_years_experience: Number(document.getElementById("min_years_experience").value),
    min_education: document.getElementById("min_education").value.trim(),
  };

  const file = fileInput.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);
  formData.append("job", JSON.stringify(job));

  analyzeButton.disabled = true;
  resultCard.classList.add("hidden");
  metricScore.textContent = "--";
  metricSession.textContent = "--";
  sessionIdInput.value = "";
  clearChat();
  setStatus("Enviando currículo...");

  try {
    const response = await fetch("/cv/analyze", { method: "POST", body: formData });
    if (!response.ok) throw new Error(`Erro ${response.status} ao enviar análise`);
    const { task_id: taskId } = await response.json();
    setStatus("Análise em fila...");
    pollStatus(taskId);
  } catch (err) {
    analyzeButton.disabled = false;
    setStatus(`Falha: ${err.message}`, "error");
  }
});

function pollStatus(taskId) {
  const statusLabels = {
    PENDING: "Aguardando worker...",
    STARTED: "Processando currículo...",
    RETRY: "Tentando novamente...",
  };

  pollTimer = setInterval(async () => {
    try {
      const response = await fetch(`/cv/status/${taskId}`);
      if (!response.ok) throw new Error(`Erro ${response.status}`);
      const data = await response.json();

      if (data.status === "SUCCESS") {
        clearInterval(pollTimer);
        pollTimer = null;
        analyzeButton.disabled = false;
        setStatus("Análise concluída.", "success");
        renderResult(data.result);
        return;
      }

      if (data.status === "FAILURE") {
        clearInterval(pollTimer);
        pollTimer = null;
        analyzeButton.disabled = false;
        setStatus(`Falha na análise: ${data.detail || "erro desconhecido"}`, "error");
        return;
      }

      setStatus(statusLabels[data.status] || `Status: ${data.status}...`);
    } catch (err) {
      clearInterval(pollTimer);
      pollTimer = null;
      analyzeButton.disabled = false;
      setStatus(`Falha ao consultar status: ${err.message}`, "error");
    }
  }, 1800);
}

function renderResult(result) {
  const validation = result.validation || {};
  const score = Math.max(0, Math.min(100, Number(validation.score) || 0));
  const sessionId = result.session_id || validation.resume_id || "--";

  scoreBadge.textContent = formatScore(score);
  metricScore.textContent = `${formatScore(score)}/100`;
  metricSession.textContent = sessionId === "--" ? "--" : sessionId.slice(0, 8);
  document.documentElement.style.setProperty("--score-angle", `${score * 3.6}deg`);

  eligibleBadge.textContent = validation.is_eligible ? "Elegível" : "Não elegível";
  eligibleBadge.className = `eligible-badge ${validation.is_eligible ? "yes" : "no"}`;
  reasoning.textContent = validation.reasoning || "Sem raciocínio retornado.";

  requirementScores.innerHTML = "";
  const scores = Array.isArray(validation.requirement_scores) ? validation.requirement_scores : [];
  scores.forEach((requirementScore) => {
    const item = document.createElement("li");
    const badge = document.createElement("span");
    const content = document.createElement("span");
    const title = document.createElement("span");
    const detail = document.createElement("span");

    badge.className = "req-score";
    badge.textContent = `${formatScore(requirementScore.score)}/100`;

    title.className = "criterion-title";
    title.textContent = requirementScore.requirement || "Critério";

    detail.className = "criterion-detail";
    detail.textContent = requirementScore.detail || "Sem detalhe retornado.";

    content.append(title, detail);
    item.append(badge, content);
    requirementScores.appendChild(item);
  });

  if (!scores.length) {
    const empty = document.createElement("li");
    empty.textContent = "Nenhum critério detalhado foi retornado.";
    requirementScores.appendChild(empty);
  }

  feedback.textContent = result.feedback || "Sem feedback retornado.";
  resultCard.classList.remove("hidden");

  sessionIdInput.value = result.session_id || "";
  clearChat();
}

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const sessionId = sessionIdInput.value.trim();
  const question = questionInput.value.trim();
  if (!sessionId || !question) return;

  appendMessage("human", question);
  questionInput.value = "";
  questionInput.disabled = true;

  try {
    const response = await fetch(`/chat/${sessionId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, messages: chatMessages }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => null);
      throw new Error(error?.detail || `Erro ${response.status}`);
    }

    const data = await response.json();
    chatMessages = data.messages || chatMessages;
    appendMessage("ai", data.answer);
  } catch (err) {
    appendMessage("ai", `Erro ao consultar o chat: ${err.message}`);
  } finally {
    questionInput.disabled = false;
    questionInput.focus();
  }
});

function appendMessage(role, content) {
  const emptyState = chatLog.querySelector(".empty-state");
  if (emptyState) emptyState.remove();

  const message = document.createElement("div");
  message.className = `msg ${role}`;
  message.textContent = content;
  chatLog.appendChild(message);
  chatLog.scrollTop = chatLog.scrollHeight;
}
