const setupForm = document.querySelector("#setup-form");
const answerForm = document.querySelector("#answer-form");
const topicInput = document.querySelector("#topic");
const notesInput = document.querySelector("#notes");
const generateButton = document.querySelector("#generate");
const gradeButton = document.querySelector("#grade");
const quizTitle = document.querySelector("#quiz-title");
const questions = document.querySelector("#questions");
const gradeSummary = document.querySelector("#grade-summary");
const setupError = document.querySelector("#setup-error");
const gradeError = document.querySelector("#grade-error");
const choices = ["A", "B", "C"];

let currentQuiz = null;
let pending = false;

function setError(element, message = "") {
  element.textContent = message;
  element.hidden = !message;
}

function setBusy(busy) {
  pending = busy;
  generateButton.disabled = busy;
  gradeButton.disabled = busy;
}

async function requestJSON(url, data) {
  const options = data === undefined ? undefined : {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  };
  let response;
  try {
    response = await fetch(url, options);
  } catch {
    throw new Error("无法连接到 KnowForge，请确认本地服务正在运行。");
  }

  const payload = await response.json().catch(() => null);
  if (response.ok && payload) return payload;
  if (typeof payload?.detail === "string") throw new Error(payload.detail);
  if (response.status === 422) throw new Error("请检查输入内容并重试。");
  throw new Error("暂时无法完成请求，请稍后重试。");
}

function renderQuiz(quiz) {
  currentQuiz = quiz;
  quizTitle.textContent = quiz.topic;
  document.querySelector("#empty-state").hidden = true;
  gradeSummary.hidden = true;
  gradeButton.hidden = false;
  setError(gradeError);

  const fields = quiz.questions.map((question, index) => {
    const field = document.createElement("fieldset");
    field.className = "question";
    const legend = document.createElement("legend");
    legend.textContent = `${index + 1}. ${question.question}`;
    field.append(legend);

    question.options.forEach((option, optionIndex) => {
      const choice = choices[optionIndex];
      const label = document.createElement("label");
      const radio = document.createElement("input");
      label.className = "option";
      radio.type = "radio";
      radio.name = `q${index}`;
      radio.value = choice;
      radio.required = true;
      label.append(radio, `${choice}. ${option}`);
      field.append(label);
    });
    return field;
  });

  questions.replaceChildren(...fields);
  answerForm.hidden = false;
  quizTitle.focus();
}

function renderGrade(grade) {
  gradeSummary.textContent = `得分 ${grade.score} / ${grade.total}`;
  gradeSummary.hidden = false;
  grade.results.forEach((result, index) => {
    const field = questions.children[index];
    for (const input of field.querySelectorAll("input")) {
      input.disabled = true;
      if (input.value === result.answer) input.parentElement.classList.add("is-correct");
      if (!result.correct && input.value === result.selected) {
        input.parentElement.classList.add("is-wrong");
      }
    }
    const feedback = document.createElement("p");
    feedback.className = "answer-feedback";
    const outcome = result.correct ? "回答正确。" : `你选了 ${result.selected}。`;
    feedback.textContent = `${outcome}正确答案是 ${result.answer}。${result.explanation}`;
    field.append(feedback);
  });
  gradeButton.hidden = true;
  gradeSummary.focus();
}

setupForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (pending) return;
  const topic = topicInput.value.trim();
  if (!topic) {
    setError(setupError, "请输入学习主题。");
    topicInput.focus();
    return;
  }

  setError(setupError);
  setBusy(true);
  generateButton.textContent = "正在生成…";
  try {
    renderQuiz(await requestJSON("/api/quizzes", { topic, notes: notesInput.value.trim() }));
  } catch (error) {
    setError(setupError, error.message);
  } finally {
    generateButton.textContent = "生成练习";
    setBusy(false);
  }
});

answerForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (pending || !currentQuiz || gradeButton.hidden) return;
  const formData = new FormData(answerForm);
  const answers = currentQuiz.questions.map((_, index) => formData.get(`q${index}`));

  setError(gradeError);
  setBusy(true);
  gradeButton.textContent = "正在判分…";
  try {
    renderGrade(await requestJSON(`/api/quizzes/${currentQuiz.id}/grade`, { answers }));
  } catch (error) {
    setError(gradeError, error.message);
  } finally {
    gradeButton.textContent = "提交答案";
    setBusy(false);
  }
});

async function loadConfig() {
  const modeSummary = document.querySelector("#mode-summary");
  try {
    const config = await requestJSON("/api/config");
    const isDemo = config.mode === "demo";
    modeSummary.textContent = isDemo ? "离线演示 · 从下方示例主题选择" : "DeepSeek 出题 · 支持自定义主题";
    document.querySelector("#notes-field").hidden = isDemo;
    const buttons = config.topics.map((topic) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "example";
      button.textContent = topic;
      button.addEventListener("click", () => {
        topicInput.value = topic;
        topicInput.focus();
      });
      return button;
    });
    document.querySelector("#examples").replaceChildren(...buttons);
    topicInput.disabled = false;
    generateButton.disabled = false;
  } catch (error) {
    modeSummary.textContent = "无法读取出题模式，请刷新页面。";
    setError(setupError, error.message);
  }
}

loadConfig();
