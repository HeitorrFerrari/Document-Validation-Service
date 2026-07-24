const analyzeForm = document.getElementById("analyze-form");
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

let chatMessages = [];

function splitSkills(value) {
  return value.split(",").map((s) => s.trim()).filter(Boolean);
}

analyzeForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const job = {
    title: document.getElementById("title").value,
    required_skills: splitSkills(document.getElementById("required_skills").value),
    desired_skills: splitSkills(document.getElementById("desired_skills").value),
    min_years_experience: Number(document.getElementById("min_years_experience").value),
    min_education: document.getElementById("min_education").value,
  };

  const file = document.getElementById("file").files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);
  formData.append("job", JSON.stringify(job));

  resultCard.classList.add("hidden");
  analyzeStatus.classList.remove("hidden");
  analyzeStatus.textContent = "Enviando currículo...";

  try {
    const response = await fetch("/cv/analyze", { method: "POST", body: formData });
    if (!response.ok) throw new Error(`Erro ${response.status} ao enviar análise`);
    const { task_id } = await response.json();
    pollStatus(task_id);
  } catch (err) {
    analyzeStatus.textContent = `Falha: ${err.message}`;
  }
});

function pollStatus(taskId) {
  analyzeStatus.textContent = "Processando (extração, validação, feedback)...";

  const interval = setInterval(async () => {
    try {
      const response = await fetch(`/cv/status/${taskId}`);
      const data = await response.json();

      if (data.status === "SUCCESS") {
        clearInterval(interval);
        analyzeStatus.textContent = "Análise concluída.";
        renderResult(data.result);
      } else if (data.status === "FAILURE") {
        clearInterval(interval);
        analyzeStatus.textContent = `Falha na análise: ${data.detail || "erro desconhecido"}`;
      } else {
        analyzeStatus.textContent = `Status: ${data.status}...`;
      }
    } catch (err) {
      clearInterval(interval);
      analyzeStatus.textContent = `Falha ao consultar status: ${err.message}`;
    }
  }, 2000);
}

function renderResult(result) {
  const validation = result.validation;

  scoreBadge.textContent = `${validation.score}/100`;
  eligibleBadge.textContent = validation.is_eligible ? "Elegível" : "Não elegível";
  eligibleBadge.className = `eligible-badge ${validation.is_eligible ? "yes" : "no"}`;
  reasoning.textContent = validation.reasoning;

  requirementScores.innerHTML = "";
  validation.requirement_scores.forEach((rs) => {
    const li = document.createElement("li");
    li.innerHTML = `<span class="req-score">${rs.score}/100</span> — ${rs.requirement}: ${rs.detail}`;
    requirementScores.appendChild(li);
  });

  feedback.textContent = result.feedback;

  resultCard.classList.remove("hidden");

  sessionIdInput.value = result.session_id;
  chatMessages = [];
  chatLog.innerHTML = "";
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

    if (!response.ok) throw new Error(`Erro ${response.status}`);

    const data = await response.json();
    chatMessages = data.messages;
    appendMessage("ai", data.answer);
  } catch (err) {
    appendMessage("ai", `Erro ao consultar o chat: ${err.message}`);
  } finally {
    questionInput.disabled = false;
    questionInput.focus();
  }
});

function appendMessage(role, content) {
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.textContent = content;
  chatLog.appendChild(div);
  chatLog.scrollTop = chatLog.scrollHeight;
}
