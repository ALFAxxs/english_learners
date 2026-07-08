// ================================================================
// GRAMMAR BATTLE — multiple choice / fill-blank / drag-drop rounds
// with combo, time pressure, and a boss round every 10 questions.
// ================================================================

const GB = {
  topics: [],
  topic: null,       // {id, name, icon}
  selectedTopicId: null,
  questions: [],      // from API, includes correct_answer
  idx: 0,
  correct: 0,
  combo: 0,
  bestCombo: 0,
  answered: false,
  ddPlaced: [],        // drag-drop: tokens placed in the answer row, in order
  ddBank: [],          // drag-drop: remaining tokens in the bank
  timerHandle: null,
  timeLeft: 0,
  startedAt: 0,
  bossCleared: false,  // whether the boss (round-10) question was answered correctly
};

const GB_QUESTION_TIME = 20;
const GB_BOSS_TIME = 25;

function goToGb(id) {
  document.querySelectorAll('.gb-screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  window.scrollTo(0, 0);
}

function normalizeLoose(s) {
  return (s || '').trim().toLowerCase().replace(/\s+/g, '');
}

// ================================================================
// TOPIC SELECT
// ================================================================
async function loadTopics() {
  G.mountPlayerBar(document.getElementById('gb-player-bar-mount'));
  const profile = await G.initPlayer();
  if (!profile) return;

  try {
    const res = await fetch(`${API_GRAMMAR_TOPICS_URL}?uuid=${encodeURIComponent(profile.uuid)}`);
    const data = await res.json();
    if (!data.ok) return;
    GB.topics = data.topics;
    renderTopicGrid();
  } catch (e) {
    document.getElementById('gb-topic-grid').innerHTML = '<div class="gb-loading">Could not load topics.</div>';
  }
}

function renderTopicGrid() {
  const grid = document.getElementById('gb-topic-grid');
  grid.innerHTML = GB.topics.map(t => `
    <div class="gb-topic-card ${t.unlocked ? '' : 'locked'}" ${t.unlocked ? `onclick="showLesson(${t.id})"` : ''}>
      <div class="icon">${t.unlocked ? t.icon : '🔒'}</div>
      <div class="name">${t.name}</div>
      <div class="desc">${t.description}</div>
      ${t.completed ? `<div class="status completed">✅ Completed · ${t.best_score_pct}%</div>` :
        t.unlocked ? `<div class="status">Ready to play</div>` :
        `<div class="status locked-label">Locked</div>`}
    </div>
  `).join('');
}

// ================================================================
// LESSON SCREEN (explanation before practice)
// ================================================================
function showLesson(topicId) {
  const topic = GB.topics.find(t => t.id === topicId);
  if (!topic) return;

  GB.selectedTopicId = topicId;
  document.getElementById('gb-lesson-icon').textContent = topic.icon;
  document.getElementById('gb-lesson-name').textContent = topic.name;
  document.getElementById('gb-lesson-rule').textContent = topic.lesson_rule || '';
  document.getElementById('gb-lesson-structure').textContent = topic.lesson_structure || '';
  document.getElementById('gb-lesson-signal-words').innerHTML =
    (topic.lesson_signal_words || []).map(w => `<span class="sw-chip">${w}</span>`).join('');
  document.getElementById('gb-lesson-examples').innerHTML =
    (topic.lesson_examples || []).map(ex => `<li>${ex}</li>`).join('');
  document.getElementById('gb-lesson-mistakes').innerHTML =
    (topic.lesson_common_mistakes || []).map(m => `<li>${m}</li>`).join('');

  goToGb('gb-screen-lesson');
}

function startPracticeFromLesson() {
  if (GB.selectedTopicId != null) startBattle(GB.selectedTopicId);
}

// ================================================================
// START A ROUND
// ================================================================
async function startBattle(topicId) {
  const uuid = G.getPlayerId();
  try {
    const res = await fetch(`${API_GRAMMAR_QUESTIONS_URL}?uuid=${encodeURIComponent(uuid)}&topic_id=${topicId}&count=10`);
    const data = await res.json();
    if (!data.ok) {
      G.toast({ icon: '🔒', title: data.error === 'topic is locked' ? 'This topic is still locked' : 'Could not start battle' });
      return;
    }
    GB.topic = data.topic;
    GB.questions = data.questions;
  } catch (e) {
    G.toast({ icon: '⚠️', title: 'Network error, please try again.' });
    return;
  }

  if (!GB.questions.length) {
    G.toast({ icon: '⚠️', title: 'No questions available for this topic yet.' });
    return;
  }

  GB.idx = 0;
  GB.correct = 0;
  GB.combo = 0;
  GB.bestCombo = 0;
  GB.bossCleared = false;
  GB.startedAt = Date.now();

  document.getElementById('gb-q-total').textContent = GB.questions.length;
  goToGb('gb-screen-game');
  renderQuestion();
}

// ================================================================
// RENDER A QUESTION
// ================================================================
function renderQuestion() {
  const q = GB.questions[GB.idx];
  GB.answered = false;
  GB.ddPlaced = [];
  GB.ddBank = [];

  document.getElementById('gb-q-index').textContent = GB.idx + 1;
  document.getElementById('gb-progress-fill').style.width = `${(GB.idx / GB.questions.length) * 100}%`;
  document.getElementById('gb-boss-banner').style.display = q.is_boss ? '' : 'none';
  document.getElementById('gb-feedback').textContent = '';
  document.getElementById('gb-feedback').className = 'gb-feedback';
  document.getElementById('gb-submit-btn').style.display = q.question_type === 'multiple_choice' ? 'none' : '';
  document.getElementById('gb-submit-btn').disabled = false;
  document.getElementById('gb-next-btn').style.display = 'none';
  updateComboUI();

  document.getElementById('gb-prompt').textContent = q.prompt;
  const area = document.getElementById('gb-answer-area');

  if (q.question_type === 'multiple_choice') {
    area.innerHTML = q.options.map(opt => `
      <button class="gb-option-btn" onclick="selectMcOption(this, '${escapeAttr(opt)}')">${opt}</button>
    `).join('');
  } else if (q.question_type === 'fill_blank') {
    area.innerHTML = `<input type="text" class="gb-fill-input" id="gb-fill-input" placeholder="Type your answer..."
      autocomplete="off" onkeydown="if(event.key==='Enter')submitAnswer()">`;
    setTimeout(() => { const el = document.getElementById('gb-fill-input'); if (el) el.focus(); }, 80);
  } else {
    GB.ddBank = shuffle([...q.options]);
    area.innerHTML = `
      <div class="gb-dd-answer-row" id="gb-dd-answer-row"></div>
      <div class="gb-dd-bank-row" id="gb-dd-bank-row"></div>`;
    renderDragDrop();
  }

  startQuestionTimer(q.is_boss ? GB_BOSS_TIME : GB_QUESTION_TIME);
}

function escapeAttr(s) {
  return String(s).replace(/'/g, "\\'");
}

function shuffle(arr) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = (Math.random() * (i + 1)) | 0;
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

// ================================================================
// MULTIPLE CHOICE
// ================================================================
let gbSelectedOption = null;
function selectMcOption(el, value) {
  if (GB.answered) return;
  document.querySelectorAll('.gb-option-btn').forEach(b => b.classList.remove('selected'));
  el.classList.add('selected');
  gbSelectedOption = value;
  submitAnswer();
}

// ================================================================
// DRAG AND DROP (tap-to-place word chips)
// ================================================================
function renderDragDrop() {
  document.getElementById('gb-dd-bank-row').innerHTML = GB.ddBank.map((tok, i) => `
    <div class="gb-chip" onclick="placeChip(${i})">${tok}</div>
  `).join('');
  document.getElementById('gb-dd-answer-row').innerHTML = GB.ddPlaced.map((tok, i) => `
    <div class="gb-chip placed" onclick="unplaceChip(${i})">${tok}</div>
  `).join('');
}

function placeChip(bankIndex) {
  if (GB.answered) return;
  GB.ddPlaced.push(GB.ddBank[bankIndex]);
  GB.ddBank.splice(bankIndex, 1);
  renderDragDrop();
}

function unplaceChip(placedIndex) {
  if (GB.answered) return;
  GB.ddBank.push(GB.ddPlaced[placedIndex]);
  GB.ddPlaced.splice(placedIndex, 1);
  renderDragDrop();
}

// ================================================================
// TIMER
// ================================================================
function startQuestionTimer(seconds) {
  clearInterval(GB.timerHandle);
  GB.timeLeft = seconds;
  updateTimerUI(seconds);
  GB.timerHandle = setInterval(() => {
    GB.timeLeft--;
    updateTimerUI(seconds);
    if (GB.timeLeft <= 0) {
      clearInterval(GB.timerHandle);
      if (!GB.answered) submitAnswer(true);
    }
  }, 1000);
}

function updateTimerUI(totalSeconds) {
  const fill = document.getElementById('gb-timer-fill');
  const pct = Math.max(0, (GB.timeLeft / totalSeconds) * 100);
  fill.style.width = pct + '%';
  fill.classList.toggle('low', GB.timeLeft <= 5);
}

// ================================================================
// CHECK ANSWER
// ================================================================
function submitAnswer(timedOut) {
  if (GB.answered) return;
  const q = GB.questions[GB.idx];
  let isCorrect = false;

  if (!timedOut) {
    if (q.question_type === 'multiple_choice') {
      if (!gbSelectedOption) return;
      isCorrect = gbSelectedOption === q.correct_answer;
    } else if (q.question_type === 'fill_blank') {
      const val = document.getElementById('gb-fill-input').value;
      isCorrect = normalizeLoose(val) === normalizeLoose(q.correct_answer);
    } else {
      const built = GB.ddPlaced.join(' ');
      isCorrect = normalizeLoose(built) === normalizeLoose(q.correct_answer);
    }
  }

  GB.answered = true;
  gbSelectedOption = null;
  clearInterval(GB.timerHandle);

  if (q.is_boss && isCorrect) GB.bossCleared = true;

  const feedback = document.getElementById('gb-feedback');
  if (isCorrect) {
    GB.correct++;
    GB.combo++;
    GB.bestCombo = Math.max(GB.bestCombo, GB.combo);
    feedback.textContent = '✅ Correct!';
    feedback.className = 'gb-feedback correct';
    playGbSound(true);
  } else {
    GB.combo = 0;
    feedback.textContent = timedOut ? `⏱️ Time's up! Answer: ${q.correct_answer}` : `❌ Answer: ${q.correct_answer}`;
    feedback.className = 'gb-feedback wrong';
    playGbSound(false);
  }
  updateComboUI();
  markAnswerUI(isCorrect);

  document.getElementById('gb-submit-btn').style.display = 'none';
  document.getElementById('gb-next-btn').style.display = '';
}

function markAnswerUI(isCorrect) {
  const q = GB.questions[GB.idx];
  if (q.question_type === 'multiple_choice') {
    document.querySelectorAll('.gb-option-btn').forEach(btn => {
      btn.disabled = true;
      if (btn.textContent === q.correct_answer) btn.classList.add('correct');
      else if (btn.classList.contains('selected')) btn.classList.add('wrong');
    });
  } else if (q.question_type === 'fill_blank') {
    const el = document.getElementById('gb-fill-input');
    el.disabled = true;
    el.classList.add(isCorrect ? 'correct' : 'wrong');
  } else {
    document.querySelectorAll('#gb-dd-bank-row .gb-chip, #gb-dd-answer-row .gb-chip').forEach(chip => {
      chip.style.pointerEvents = 'none';
    });
  }
}

function updateComboUI() {
  const badge = document.getElementById('gb-combo-badge');
  if (GB.combo >= 2) {
    badge.style.display = '';
    document.getElementById('gb-combo-val').textContent = GB.combo;
  } else {
    badge.style.display = 'none';
  }
}

function nextQuestion() {
  GB.idx++;
  if (GB.idx >= GB.questions.length) {
    endBattle();
  } else {
    renderQuestion();
  }
}

// ================================================================
// SOUND
// ================================================================
let GbAudioCtx = null;
function playGbSound(good) {
  try {
    if (!GbAudioCtx) GbAudioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const o = GbAudioCtx.createOscillator();
    const g = GbAudioCtx.createGain();
    o.connect(g); g.connect(GbAudioCtx.destination);
    if (good) {
      o.frequency.setValueAtTime(523, GbAudioCtx.currentTime);
      o.frequency.setValueAtTime(784, GbAudioCtx.currentTime + 0.1);
    } else {
      o.frequency.setValueAtTime(280, GbAudioCtx.currentTime);
    }
    g.gain.setValueAtTime(0.14, GbAudioCtx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.001, GbAudioCtx.currentTime + 0.3);
    o.start(); o.stop(GbAudioCtx.currentTime + 0.3);
  } catch (e) {}
}

// ================================================================
// END BATTLE
// ================================================================
async function endBattle() {
  clearInterval(GB.timerHandle);
  const duration = Math.round((Date.now() - GB.startedAt) / 1000);
  const total = GB.questions.length;
  const pct = GB.correct / total;

  document.getElementById('gb-r-score').textContent = `${GB.correct}/${total}`;
  document.getElementById('gb-r-combo').textContent = GB.bestCombo;

  if (pct >= 0.999) {
    document.getElementById('gb-result-emoji').textContent = '🏆';
    document.getElementById('gb-result-title').textContent = 'Flawless Victory!';
  } else if (pct >= 0.7) {
    document.getElementById('gb-result-emoji').textContent = '⚔️';
    document.getElementById('gb-result-title').textContent = 'Battle Won!';
  } else {
    document.getElementById('gb-result-emoji').textContent = '📖';
    document.getElementById('gb-result-title').textContent = 'Good Try — Keep Training!';
  }

  goToGb('gb-screen-results');

  const response = await fetch(API_GRAMMAR_COMPLETE_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': window.CSRF_TOKEN || '' },
    body: JSON.stringify({
      uuid: G.getPlayerId(), topic_id: GB.topic.id, correct: GB.correct, total,
      combo: GB.bestCombo, duration_seconds: duration, boss_cleared: GB.bossCleared,
    }),
  });
  const data = await response.json();

  document.getElementById('gb-r-topic').textContent = data.topic_completed ? '✅ Unlocked Next' : `${Math.round(pct * 100)}% (need 70%)`;
  document.getElementById('gb-result-sub').textContent = data.topic_completed
    ? `You cleared "${GB.topic.name}" and unlocked the next topic!`
    : `You need 70%+ to unlock the next topic. Try again!`;

  G.applyGameResult(data);
}

document.addEventListener('DOMContentLoaded', loadTopics);
