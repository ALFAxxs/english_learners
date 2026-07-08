// ================================================================
// VOCABULARY BUILDER — word list -> exercises -> reading comprehension,
// one unit at a time, units unlocked sequentially at 70%+.
// ================================================================

const VB = {
  units: [],
  unit: null,        // {id, name, icon}
  words: [],
  wordIdx: 0,
  questions: [],     // vocab drill questions (multiple choice, correct_answer included)
  passage: null,     // {title, body, questions}
  phase: 'drill',    // 'drill' | 'passage_questions'
  drillIdx: 0,
  pqIdx: 0,
  total: 0,
  correct: 0,
  startedAt: 0,
  selected: null,
  answered: false,
};

function goToVb(id) {
  document.querySelectorAll('.vb-screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  window.scrollTo(0, 0);
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
// UNIT SELECT
// ================================================================
async function loadUnits() {
  G.mountPlayerBar(document.getElementById('vb-player-bar-mount'));
  const profile = await G.initPlayer();
  if (!profile) return;

  try {
    const res = await fetch(`${API_VB_UNITS_URL}?uuid=${encodeURIComponent(profile.uuid)}`);
    const data = await res.json();
    if (!data.ok) return;
    VB.units = data.units;
    renderUnitGrid();
  } catch (e) {
    document.getElementById('vb-unit-grid').innerHTML = '<div class="vb-loading">Could not load units.</div>';
  }
}

function renderUnitGrid() {
  const grid = document.getElementById('vb-unit-grid');
  grid.innerHTML = VB.units.map(u => `
    <div class="vb-unit-card ${u.unlocked ? '' : 'locked'}" ${u.unlocked ? `onclick="openUnit(${u.id})"` : ''}>
      <div class="icon">${u.unlocked ? u.icon : '🔒'}</div>
      <div class="name">${u.name}</div>
      <div class="desc">${u.description}</div>
      ${u.completed ? `<div class="status completed">✅ ${u.best_score_pct}%</div>` :
        u.unlocked ? `<div class="status">Ready</div>` :
        `<div class="status locked-label">Locked</div>`}
    </div>
  `).join('');
}

// ================================================================
// OPEN A UNIT -> LESSON (WORD DECK)
// ================================================================
async function openUnit(unitId) {
  const uuid = G.getPlayerId();
  try {
    const res = await fetch(`${API_VB_UNIT_URL}?uuid=${encodeURIComponent(uuid)}&unit_id=${unitId}`);
    const data = await res.json();
    if (!data.ok) {
      G.toast({ icon: '🔒', title: data.error === 'unit is locked' ? 'This unit is still locked' : 'Could not load this unit.' });
      return;
    }
    VB.unit = data.unit;
    VB.words = data.words;
    VB.questions = data.questions;
    VB.passage = data.passage;
  } catch (e) {
    G.toast({ icon: '⚠️', title: 'Network error, please try again.' });
    return;
  }

  if (!VB.words.length) {
    G.toast({ icon: '⚠️', title: 'No words available for this unit yet.' });
    return;
  }

  VB.wordIdx = 0;
  document.getElementById('vb-lesson-title').textContent = `${VB.unit.icon} ${VB.unit.name}`;
  document.getElementById('vb-word-total').textContent = VB.words.length;
  goToVb('vb-screen-lesson');
  renderWord();
}

function renderWord() {
  const w = VB.words[VB.wordIdx];
  document.getElementById('vb-word-index').textContent = VB.wordIdx + 1;
  document.getElementById('vb-word-pos').textContent = w.part_of_speech || '';
  document.getElementById('vb-word-main').textContent = w.word;
  document.getElementById('vb-word-pron').textContent = w.pronunciation || '';
  document.getElementById('vb-word-def').textContent = w.definition;
  document.getElementById('vb-word-ex').textContent = `→ ${w.example_sentence}`;

  document.getElementById('vb-word-prev').disabled = VB.wordIdx === 0;
  const isLast = VB.wordIdx === VB.words.length - 1;
  document.getElementById('vb-word-next').style.display = isLast ? 'none' : '';
  document.getElementById('vb-start-practice-btn').style.display = isLast ? '' : 'none';
}

function prevWord() {
  if (VB.wordIdx > 0) {
    VB.wordIdx--;
    renderWord();
  }
}

function nextWord() {
  if (VB.wordIdx < VB.words.length - 1) {
    VB.wordIdx++;
    renderWord();
  }
}

function startPracticeFromLesson() {
  VB.phase = 'drill';
  VB.drillIdx = 0;
  VB.pqIdx = 0;
  VB.correct = 0;
  VB.total = VB.questions.length + (VB.passage.questions ? VB.passage.questions.length : 0);
  VB.startedAt = Date.now();

  document.getElementById('vb-passage-card').style.display = 'none';
  document.getElementById('vb-question-card').style.display = '';
  goToVb('vb-screen-game');

  if (VB.questions.length) {
    renderVbQuestion();
  } else {
    showPassage();
  }
}

// ================================================================
// DRILL / PASSAGE-QUESTION RENDERING (shared multiple-choice UI)
// ================================================================
function currentQuestion() {
  return VB.phase === 'drill' ? VB.questions[VB.drillIdx] : VB.passage.questions[VB.pqIdx];
}

function overallProgressIndex() {
  return VB.phase === 'drill' ? VB.drillIdx : VB.questions.length + VB.pqIdx;
}

function renderVbQuestion() {
  const q = currentQuestion();
  VB.answered = false;
  VB.selected = null;

  const doneCount = overallProgressIndex();
  document.getElementById('vb-progress-label').textContent = `Question ${doneCount + 1} of ${VB.total}`;
  document.getElementById('vb-progress-fill').style.width = `${(doneCount / VB.total) * 100}%`;
  document.getElementById('vb-feedback').textContent = '';
  document.getElementById('vb-feedback').className = 'vb-feedback';
  document.getElementById('vb-next-btn').style.display = 'none';

  document.getElementById('vb-prompt').textContent = q.prompt;
  const area = document.getElementById('vb-answer-area');
  area.innerHTML = shuffle([...q.options]).map(opt => `
    <button class="vb-option-btn" onclick="selectVbOption(this, '${escapeAttr(opt)}')">${opt}</button>
  `).join('');
}

function selectVbOption(el, value) {
  if (VB.answered) return;
  VB.answered = true;
  const q = currentQuestion();
  const isCorrect = value === q.correct_answer;
  if (isCorrect) VB.correct++;

  document.querySelectorAll('.vb-option-btn').forEach(btn => {
    btn.disabled = true;
    if (btn.textContent === q.correct_answer) btn.classList.add('correct');
    else if (btn === el) btn.classList.add('wrong');
  });

  const feedback = document.getElementById('vb-feedback');
  if (isCorrect) {
    feedback.textContent = '✅ Correct!';
    feedback.className = 'vb-feedback correct';
  } else {
    feedback.textContent = `❌ Correct answer: ${q.correct_answer}`;
    feedback.className = 'vb-feedback wrong';
  }
  document.getElementById('vb-next-btn').style.display = '';
}

function nextVbQuestion() {
  if (VB.phase === 'drill') {
    VB.drillIdx++;
    if (VB.drillIdx >= VB.questions.length) {
      showPassage();
    } else {
      renderVbQuestion();
    }
  } else {
    VB.pqIdx++;
    if (VB.pqIdx >= VB.passage.questions.length) {
      endUnit();
    } else {
      renderVbQuestion();
    }
  }
}

// ================================================================
// READING PASSAGE
// ================================================================
function showPassage() {
  document.getElementById('vb-question-card').style.display = 'none';
  document.getElementById('vb-passage-card').style.display = '';
  document.getElementById('vb-passage-title').textContent = VB.passage.title;
  document.getElementById('vb-passage-body').textContent = VB.passage.body;

  const doneCount = VB.questions.length;
  document.getElementById('vb-progress-label').textContent = `Reading Time`;
  document.getElementById('vb-progress-fill').style.width = `${(doneCount / VB.total) * 100}%`;
}

function startPassageQuestions() {
  VB.phase = 'passage_questions';
  VB.pqIdx = 0;
  document.getElementById('vb-passage-card').style.display = 'none';
  document.getElementById('vb-question-card').style.display = '';

  if (VB.passage.questions && VB.passage.questions.length) {
    renderVbQuestion();
  } else {
    endUnit();
  }
}

// ================================================================
// END UNIT
// ================================================================
async function endUnit() {
  const duration = Math.round((Date.now() - VB.startedAt) / 1000);
  const total = VB.total || 1;
  const pct = VB.correct / total;

  document.getElementById('vb-r-score').textContent = `${VB.correct}/${total}`;
  document.getElementById('vb-r-pct').textContent = `${Math.round(pct * 100)}%`;

  if (pct >= 0.999) {
    document.getElementById('vb-result-emoji').textContent = '🏆';
    document.getElementById('vb-result-title').textContent = 'Perfect Score!';
  } else if (pct >= 0.7) {
    document.getElementById('vb-result-emoji').textContent = '📖';
    document.getElementById('vb-result-title').textContent = 'Unit Complete!';
  } else {
    document.getElementById('vb-result-emoji').textContent = '📚';
    document.getElementById('vb-result-title').textContent = 'Good Try — Review & Retry!';
  }

  goToVb('vb-screen-results');

  const response = await fetch(API_VB_COMPLETE_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': window.CSRF_TOKEN || '' },
    body: JSON.stringify({
      uuid: G.getPlayerId(), unit_id: VB.unit.id, correct: VB.correct, total,
      duration_seconds: duration,
    }),
  });
  const data = await response.json();

  document.getElementById('vb-r-unit').textContent = data.unit_completed ? '✅ Unlocked Next' : `Need 70%`;
  document.getElementById('vb-result-sub').textContent = data.unit_completed
    ? `You cleared "${VB.unit.name}" and unlocked the next unit!`
    : `You need 70%+ to unlock the next unit. Try again!`;

  G.applyGameResult(data);
}

document.addEventListener('DOMContentLoaded', loadUnits);
