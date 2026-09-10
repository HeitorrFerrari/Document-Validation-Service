const sessionsList = document.getElementById("sessions-list");
const sessionsCount = document.getElementById("sessions-count");
const sessionHeading = document.getElementById("session-heading");
const metricScore = document.getElementById("metric-score");
const metricStatus = document.getElementById("metric-status");
const metricSession = document.getElementById("metric-session");
const resultCard = document.getElementById("result-card");
const scoreBadge = document.getElementById("score-badge");
const eligibleBadge = document.getElementById("eligible-badge");
const reasoning = document.getElementById("reasoning");
const requirementScores = document.getElementById("requirement-scores");
const chatLog = document.getElementById("chat-log");
const chatForm = document.getElementById("chat-form");
const questionInput = document.getElementById("question");
const chatButton = chatForm.querySelector("button");

let currentSessionId = null;
let chatMessages = [];

function formatScore(value) {
  const score = Number(value);
  if (Number.isNaN(score)) return "--";
  return Number.isInteger(score) ? String(score) : score.toFixed(1);
}

function formatDate(iso) {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}

function renderEmptyChat(message) {
  chatMessages = [];
  chatLog.innerHTML = `
    <div class="empty-state">
      <strong>${message}</strong>
      <span>O chat usa o contexto RAG daquela sessão de validação.</span>
    </div>
  `;
}

async function loadSessions() {
  try {
    const response = await fetch("/cv/sessions");
    if (!response.ok) throw new Error(`Erro ${response.status}`);
    const { sessions } = await response.json();
    renderSessions(sessions || []);

    const wanted = new URLSearchParams(location.search).get("session");
    if (wanted) selectSession(wanted);
  } catch (err) {
    sessionsCount.textContent = "!";
    sessionsList.innerHTML = `
      <div class="empty-state">
        <strong>Não foi possível carregar as sessões</strong>
        <span>${err.message}</span>
      </div>
    `;
  }
}

function renderSessions(sessions) {
  sessionsCount.textContent = String(sessions.length);

  if (!sessions.length) {
    sessionsList.innerHTML = `
      <div class="empty-state">
        <strong>Nenhuma análise ainda</strong>
        <span>Rode uma análise em "Nova análise" para começar o histórico.</span>
      </div>
    `;
    return;
  }

  sessionsList.innerHTML = "";
  sessions.forEach((session) => {
    const item = document.createElement("button");
    item.type = "button";
    item.className = "session-item";
    item.dataset.sessionId = session.session_id;

    const eligible = session.is_eligible;
    item.innerHTML = `
      <div class="session-item-head">
        <strong>${session.candidate_name || "Candidato sem nome"}</strong>
        <span class="req-score">${formatScore(session.score)}/100</span>
      </div>
      <span class="session-item-job">${session.job_title || "Vaga não identificada"}</span>
      <div class="session-item-foot">
        <span class="eligible-badge ${eligible ? "yes" : "no"}">${eligible ? "Elegível" : "Não elegível"}</span>
        <span class="muted">${formatDate(session.created_at)}</span>
      </div>
    `;

    item.addEventListener("click", () => selectSession(session.session_id));
    sessionsList.appendChild(item);
  });
}

function markActive(sessionId) {
  sessionsList.querySelectorAll(".session-item").forEach((item) => {
    item.classList.toggle("active", item.dataset.sessionId === sessionId);
  });
}

async function selectSession(sessionId) {
  currentSessionId = sessionId;
  markActive(sessionId);
  sessionHeading.textContent = "Carregando sessão...";
  renderEmptyChat("Carregando resultado da sessão...");

  try {
    const response = await fetch(`/cv/sessions/${encodeURIComponent(sessionId)}`);
    if (!response.ok) {
      const error = await response.json().catch(() => null);
      throw new Error(error?.detail || `Erro ${response.status}`);
    }
    const data = await response.json();
    renderSession(data);
  } catch (err) {
    resultCard.classList.add("hidden");
    sessionHeading.textContent = "Não foi possível abrir a sessão.";
    metricScore.textContent = "--";
    metricStatus.textContent = "--";
    metricSession.textContent = "--";
    questionInput.disabled = true;
    chatButton.disabled = true;
    renderEmptyChat(err.message);
  }
}

function renderSession(data) {
  const validation = data.validation || {};
  const score = Math.max(0, Math.min(100, Number(validation.score) || 0));

  sessionHeading.textContent = `${data.candidate_name || "Candidato"} — ${data.job?.title || "vaga não identificada"}`;
  metricScore.textContent = `${formatScore(score)}/100`;
  metricStatus.textContent = validation.is_eligible ? "Elegível" : "Não elegível";
  metricSession.textContent = data.session_id.slice(0, 8);
  document.documentElement.style.setProperty("--score-angle", `${score * 3.6}deg`);

  scoreBadge.textContent = formatScore(score);
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

  resultCard.classList.remove("hidden");
  questionInput.disabled = false;
  chatButton.disabled = false;
  renderEmptyChat("Conversa retomada");
}

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const question = questionInput.value.trim();
  if (!currentSessionId || !question) return;

  appendMessage("human", question);
  questionInput.value = "";
  questionInput.disabled = true;
  chatButton.disabled = true;

  try {
    const response = await fetch(`/chat/${encodeURIComponent(currentSessionId)}`, {
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
    chatButton.disabled = false;
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

loadSessions();
