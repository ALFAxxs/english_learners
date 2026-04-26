// ================================================================
// STATE
// ================================================================
let ALL_VERBS = [];
let state = {
  name: '', count: 10, mode: 'both',
  verbs: [], idx: 0, correct: 0, wrong: 0,
  answered: false
};
let selectedCount = null, selectedMode = null;

// ================================================================
// BOOTSTRAP — load verbs from Django API
// ================================================================
async function loadVerbs() {
  try {
    const res = await fetch(API_VERBS_URL);
    const data = await res.json();
    ALL_VERBS = data.verbs;
  } catch (e) {
    console.error('Could not load verbs:', e);
  }
}
loadVerbs();

// ================================================================
// NAVIGATION
// ================================================================
function goTo(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  window.scrollTo(0, 0);
}

// ================================================================
// SETUP FLOW
// ================================================================
function step1Next() {
  const n = document.getElementById('name-input').value.trim();
  if (!n) { document.getElementById('name-input').focus(); return; }
  state.name = n;
  goTo('screen-step2');
}

function selectCount(el, v) {
  document.querySelectorAll('#count-options .option-btn').forEach(b => b.classList.remove('selected'));
  el.classList.add('selected');
  selectedCount = v;
}

function step2Next() {
  if (!selectedCount) { alert('Please choose a number of verbs!'); return; }
  state.count = selectedCount;
  goTo('screen-step3');
}

function selectMode(el, m) {
  document.querySelectorAll('#mode-options .option-btn').forEach(b => b.classList.remove('selected'));
  el.classList.add('selected');
  selectedMode = m;
}

function startGame() {
  if (!selectedMode) { alert('Please choose what to practice!'); return; }
  state.mode = selectedMode;

  if (ALL_VERBS.length === 0) {
    alert('Verbs are still loading. Please try again in a moment.');
    return;
  }

  const shuffled = [...ALL_VERBS].sort(() => Math.random() - 0.5);
  state.verbs = shuffled.slice(0, Math.min(state.count, shuffled.length));
  state.idx = 0; state.correct = 0; state.wrong = 0;

  goTo('screen-game');
  renderVerb();
}

// ================================================================
// GAME LOGIC
// ================================================================
function renderVerb() {
  const verb = state.verbs[state.idx];
  const total = state.verbs.length;

  document.getElementById('base-verb-display').textContent = verb.base;
  document.getElementById('progress-label').textContent = `Verb ${state.idx + 1} of ${total}`;
  document.getElementById('progress-fill').style.width = `${(state.idx / total) * 100}%`;
  document.getElementById('score-live').textContent = state.correct;
  document.getElementById('feedback-msg').textContent = '';
  document.getElementById('feedback-msg').className = 'feedback-msg';
  document.getElementById('check-btn').style.display = '';
  document.getElementById('next-btn').style.display = 'none';
  state.answered = false;

  const chip = document.getElementById('mode-chip');
  if (state.mode === 'past') chip.textContent = 'PAST SIMPLE';
  else if (state.mode === 'pp') chip.textContent = 'PAST PARTICIPLE';
  else chip.textContent = 'BOTH FORMS';

  const wrap = document.getElementById('fields-wrap');
  wrap.innerHTML = '';

  if (state.mode === 'past' || state.mode === 'both') {
    wrap.innerHTML += `
      <div class="field-group">
        <label>Past Simple</label>
        <input type="text" class="answer-input" id="inp-past" placeholder="Type past simple..."
               autocomplete="off" onkeydown="if(event.key==='Enter')checkAnswer()">
        <div class="feedback-row" id="fb-past"></div>
      </div>`;
  }
  if (state.mode === 'pp' || state.mode === 'both') {
    wrap.innerHTML += `
      <div class="field-group">
        <label>Past Participle</label>
        <input type="text" class="answer-input" id="inp-pp" placeholder="Type past participle..."
               autocomplete="off" onkeydown="if(event.key==='Enter')checkAnswer()">
        <div class="feedback-row" id="fb-pp"></div>
      </div>`;
  }

  setTimeout(() => {
    const first = wrap.querySelector('.answer-input');
    if (first) first.focus();
  }, 100);
}

function normalize(str) {
  return str.trim().toLowerCase().replace(/[^a-z\/]/g, '');
}

function checkAnswers(userVal, correctVal) {
  const u = normalize(userVal);
  const corrects = correctVal.split('/').map(x => x.trim().toLowerCase());
  return corrects.includes(u);
}

function checkAnswer() {
  if (state.answered) { nextVerb(); return; }
  const verb = state.verbs[state.idx];
  let allCorrect = true;

  if (state.mode === 'past' || state.mode === 'both') {
    const inp = document.getElementById('inp-past');
    const fb = document.getElementById('fb-past');
    const ok = checkAnswers(inp.value, verb.past);
    inp.className = 'answer-input ' + (ok ? 'correct' : 'wrong');
    inp.disabled = true;
    if (ok) { fb.className = 'feedback-row ok'; fb.textContent = '✅ Correct!'; }
    else { fb.className = 'feedback-row err'; fb.textContent = `❌ Answer: ${verb.past}`; allCorrect = false; }
  }

  if (state.mode === 'pp' || state.mode === 'both') {
    const inp = document.getElementById('inp-pp');
    const fb = document.getElementById('fb-pp');
    const ok = checkAnswers(inp.value, verb.pp);
    inp.className = 'answer-input ' + (ok ? 'correct' : 'wrong');
    inp.disabled = true;
    if (ok) { fb.className = 'feedback-row ok'; fb.textContent = '✅ Correct!'; }
    else { fb.className = 'feedback-row err'; fb.textContent = `❌ Answer: ${verb.pp}`; allCorrect = false; }
  }

  if (allCorrect) {
    state.correct++;
    document.getElementById('feedback-msg').className = 'feedback-msg correct';
    document.getElementById('feedback-msg').textContent = '🎉 Perfect! Keep it up!';
    playSound('correct');
  } else {
    state.wrong++;
    document.getElementById('feedback-msg').className = 'feedback-msg wrong';
    document.getElementById('feedback-msg').textContent = "📖 Study this one — you'll get it next time!";
    playSound('wrong');
  }

  document.getElementById('score-live').textContent = state.correct;
  state.answered = true;
  document.getElementById('check-btn').style.display = 'none';
  document.getElementById('next-btn').style.display = '';
}

function nextVerb() {
  state.idx++;
  if (state.idx >= state.verbs.length) {
    finishGame();
  } else {
    const card = document.getElementById('verb-card');
    card.style.animation = 'none';
    requestAnimationFrame(() => { card.style.animation = ''; renderVerb(); });
  }
}

async function finishGame() {
  const total = state.verbs.length;
  const pct = Math.round((state.correct / total) * 100);

  // Save session to Django backend
  try {
    await fetch(API_SAVE_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': CSRF_TOKEN,
      },
      body: JSON.stringify({
        name: state.name,
        mode: state.mode,
        total: total,
        correct: state.correct,
        wrong: state.wrong,
        pct: pct,
      }),
    });
  } catch (e) {
    console.error('Could not save session:', e);
  }

  // Show results
  document.getElementById('result-pct').textContent = pct + '%';
  document.getElementById('r-correct').textContent = state.correct;
  document.getElementById('r-wrong').textContent = state.wrong;
  document.getElementById('r-total').textContent = total;
  document.getElementById('r-name').textContent = state.name;

  const scoreCircle = document.querySelector('.score-circle');
  const pctEl = document.querySelector('.score-circle .pct');
  if (pct >= 80) { scoreCircle.style.borderColor = '#10b981'; pctEl.style.color = '#10b981'; }
  else if (pct >= 50) { scoreCircle.style.borderColor = '#f59e0b'; pctEl.style.color = '#f59e0b'; }
  else { scoreCircle.style.borderColor = '#ef4444'; pctEl.style.color = '#ef4444'; }

  if (pct === 100) {
    document.getElementById('result-emoji').textContent = '🏆';
    document.getElementById('result-title').textContent = 'Perfect Score!';
  } else if (pct >= 80) {
    document.getElementById('result-emoji').textContent = '🎉';
    document.getElementById('result-title').textContent = 'Great Job, ' + state.name + '!';
  } else if (pct >= 50) {
    document.getElementById('result-emoji').textContent = '💪';
    document.getElementById('result-title').textContent = 'Good Effort, ' + state.name + '!';
  } else {
    document.getElementById('result-emoji').textContent = '📖';
    document.getElementById('result-title').textContent = 'Keep Practicing, ' + state.name + '!';
  }

  document.getElementById('result-sub').textContent =
    `You got ${state.correct} out of ${total} correct. Score: ${pct}%`;
  goTo('screen-results');
}

function restartGame() {
  goTo('screen-step1');
}

// ================================================================
// SOUND (Web Audio API)
// ================================================================
let AudioCtx = null;
function playSound(type) {
  try {
    if (!AudioCtx) AudioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const o = AudioCtx.createOscillator();
    const g = AudioCtx.createGain();
    o.connect(g); g.connect(AudioCtx.destination);
    if (type === 'correct') {
      o.frequency.setValueAtTime(523, AudioCtx.currentTime);
      o.frequency.setValueAtTime(659, AudioCtx.currentTime + 0.1);
      o.frequency.setValueAtTime(784, AudioCtx.currentTime + 0.2);
      g.gain.setValueAtTime(0.15, AudioCtx.currentTime);
      g.gain.exponentialRampToValueAtTime(0.001, AudioCtx.currentTime + 0.5);
      o.start(); o.stop(AudioCtx.currentTime + 0.5);
    } else {
      o.frequency.setValueAtTime(300, AudioCtx.currentTime);
      o.frequency.setValueAtTime(220, AudioCtx.currentTime + 0.1);
      g.gain.setValueAtTime(0.15, AudioCtx.currentTime);
      g.gain.exponentialRampToValueAtTime(0.001, AudioCtx.currentTime + 0.3);
      o.start(); o.stop(AudioCtx.currentTime + 0.3);
    }
  } catch (e) {}
}
