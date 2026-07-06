// ================================================================
// WORD HUNTER — hidden word search with timer, combo, power-ups
// ================================================================

const WH = {
  difficulty: 1,
  size: 8,
  totalTime: 60,
  words: [],          // [{word, meaning}]
  placements: [],      // [{word, cells:[[r,c],...]}]
  grid: [],            // [r][c] = letter
  foundWords: new Set(),
  combo: 0,
  bestCombo: 0,
  lastFoundAt: 0,
  timeLeft: 60,
  timerHandle: null,
  daily: false,
  selecting: false,
  selCells: [],        // [[r,c],...]
  startedAt: 0,
};

const DIRECTIONS = [
  [0, 1], [0, -1], [1, 0], [-1, 0],
  [1, 1], [1, -1], [-1, 1], [-1, -1],
];

function selectDifficulty(el, diff) {
  document.querySelectorAll('#wh-difficulty-options .wh-option-btn').forEach(b => b.classList.remove('selected'));
  el.classList.add('selected');
  WH.difficulty = diff;
}

function goToWh(id) {
  document.querySelectorAll('.wh-screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  window.scrollTo(0, 0);
}

// ================================================================
// SETUP + WORD FETCH
// ================================================================
async function startWordHunter() {
  WH.daily = document.getElementById('wh-daily-check').checked;
  const sizeMap = { 1: 8, 2: 10, 3: 12 };
  const countMap = { 1: 6, 2: 8, 3: 10 };
  WH.size = sizeMap[WH.difficulty];
  const maxLen = WH.size - 1;

  let url = `${API_WORDS_URL}?count=40&difficulty=${WH.difficulty}`;
  if (WH.daily) {
    const today = new Date().toISOString().slice(0, 10);
    url += `&seed=${today}`;
  }

  let fetched = [];
  try {
    const res = await fetch(url);
    const data = await res.json();
    fetched = data.words || [];
  } catch (e) { /* fall through with empty */ }

  const cleaned = fetched
    .map(w => ({ word: w.word.toUpperCase().replace(/[^A-Z]/g, ''), meaning: w.meaning }))
    .filter(w => w.word.length >= 3 && w.word.length <= maxLen);

  // de-dupe by word text
  const seen = new Set();
  const unique = [];
  for (const w of cleaned) {
    if (!seen.has(w.word)) { seen.add(w.word); unique.push(w); }
  }

  WH.words = unique.slice(0, countMap[WH.difficulty]);
  if (WH.words.length < 4) {
    G.toast({ icon: '⚠️', title: 'Not enough words available', sub: 'Please ask an admin to seed the word bank.' });
    return;
  }

  buildGrid();
  WH.foundWords = new Set();
  WH.combo = 0;
  WH.bestCombo = 0;
  WH.timeLeft = WH.totalTime;
  WH.startedAt = Date.now();

  renderGrid();
  renderWordsList();
  updateTimerUI();
  attachGridEvents();
  goToWh('wh-screen-game');
  startTimer();

  G.mountPlayerBar(document.getElementById('wh-player-bar-mount'));
  G.initPlayer();
}

// ================================================================
// GRID GENERATION
// ================================================================
function buildGrid() {
  const size = WH.size;
  const grid = Array.from({ length: size }, () => Array(size).fill(null));
  const placements = [];

  const sorted = [...WH.words].sort((a, b) => b.word.length - a.word.length);

  for (const w of sorted) {
    let placed = false;
    for (let attempt = 0; attempt < 200 && !placed; attempt++) {
      const dir = DIRECTIONS[(Math.random() * DIRECTIONS.length) | 0];
      const r0 = (Math.random() * size) | 0;
      const c0 = (Math.random() * size) | 0;
      const cells = [];
      let ok = true;
      for (let i = 0; i < w.word.length; i++) {
        const r = r0 + dir[0] * i;
        const c = c0 + dir[1] * i;
        if (r < 0 || r >= size || c < 0 || c >= size) { ok = false; break; }
        const existing = grid[r][c];
        if (existing !== null && existing !== w.word[i]) { ok = false; break; }
        cells.push([r, c]);
      }
      if (ok) {
        cells.forEach(([r, c], i) => { grid[r][c] = w.word[i]; });
        placements.push({ word: w.word, meaning: w.meaning, cells });
        placed = true;
      }
    }
  }

  const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  for (let r = 0; r < size; r++) {
    for (let c = 0; c < size; c++) {
      if (grid[r][c] === null) grid[r][c] = alphabet[(Math.random() * 26) | 0];
    }
  }

  WH.grid = grid;
  WH.placements = placements;
  // Only keep words that actually got placed
  WH.words = placements.map(p => ({ word: p.word, meaning: p.meaning }));
}

// ================================================================
// RENDER
// ================================================================
function renderGrid() {
  const el = document.getElementById('wh-grid');
  el.style.gridTemplateColumns = `repeat(${WH.size}, auto)`;
  el.innerHTML = '';
  for (let r = 0; r < WH.size; r++) {
    for (let c = 0; c < WH.size; c++) {
      const cell = document.createElement('div');
      cell.className = 'wh-cell';
      cell.textContent = WH.grid[r][c];
      cell.dataset.r = r;
      cell.dataset.c = c;
      el.appendChild(cell);
    }
  }
}

function renderWordsList() {
  document.getElementById('wh-total-count').textContent = WH.words.length;
  document.getElementById('wh-found-count').textContent = WH.foundWords.size;
  const list = document.getElementById('wh-words-list');
  list.innerHTML = WH.words.map(w => `
    <div class="wh-word-item ${WH.foundWords.has(w.word) ? 'found' : ''}" data-word="${w.word}">${w.word.toLowerCase()}</div>
  `).join('');
}

function cellEl(r, c) {
  return document.querySelector(`.wh-cell[data-r="${r}"][data-c="${c}"]`);
}

// ================================================================
// SELECTION (mouse + touch)
// ================================================================
function attachGridEvents() {
  const grid = document.getElementById('wh-grid');

  const start = (r, c) => { WH.selecting = true; WH.selCells = [[r, c]]; paintSelection(); };
  const extend = (r, c) => {
    if (!WH.selecting) return;
    const [r0, c0] = WH.selCells[0];
    const dr = r - r0, dc = c - c0;
    const steps = Math.max(Math.abs(dr), Math.abs(dc));
    if (steps === 0) { WH.selCells = [[r0, c0]]; paintSelection(); return; }
    const sr = Math.sign(dr), sc = Math.sign(dc);
    // only allow straight line: horizontal, vertical, or perfect diagonal
    if (!(dr === 0 || dc === 0 || Math.abs(dr) === Math.abs(dc))) return;
    const cells = [];
    for (let i = 0; i <= steps; i++) cells.push([r0 + sr * i, c0 + sc * i]);
    WH.selCells = cells;
    paintSelection();
  };
  const finish = () => {
    if (!WH.selecting) return;
    WH.selecting = false;
    checkSelection();
  };

  function cellFromPoint(x, y) {
    const el = document.elementFromPoint(x, y);
    if (!el || !el.classList.contains('wh-cell')) return null;
    return [parseInt(el.dataset.r), parseInt(el.dataset.c)];
  }

  grid.addEventListener('mousedown', (e) => {
    if (!e.target.classList.contains('wh-cell')) return;
    start(parseInt(e.target.dataset.r), parseInt(e.target.dataset.c));
  });
  grid.addEventListener('mousemove', (e) => {
    if (!WH.selecting) return;
    if (!e.target.classList.contains('wh-cell')) return;
    extend(parseInt(e.target.dataset.r), parseInt(e.target.dataset.c));
  });
  document.addEventListener('mouseup', finish);

  grid.addEventListener('touchstart', (e) => {
    const t = e.touches[0];
    const pos = cellFromPoint(t.clientX, t.clientY);
    if (pos) start(pos[0], pos[1]);
  }, { passive: true });
  grid.addEventListener('touchmove', (e) => {
    const t = e.touches[0];
    const pos = cellFromPoint(t.clientX, t.clientY);
    if (pos) extend(pos[0], pos[1]);
  }, { passive: true });
  grid.addEventListener('touchend', finish);
}

function paintSelection() {
  document.querySelectorAll('.wh-cell.selected').forEach(el => el.classList.remove('selected'));
  WH.selCells.forEach(([r, c]) => {
    const el = cellEl(r, c);
    if (el) el.classList.add('selected');
  });
}

function checkSelection() {
  const cells = WH.selCells;
  document.querySelectorAll('.wh-cell.selected').forEach(el => el.classList.remove('selected'));
  if (cells.length < 2) return;

  const str = cells.map(([r, c]) => WH.grid[r][c]).join('');
  const reversed = str.split('').reverse().join('');

  const match = WH.placements.find(p =>
    !WH.foundWords.has(p.word) && (p.word === str || p.word === reversed) && p.cells.length === cells.length
  );

  if (match) {
    markFound(match);
  } else {
    cells.forEach(([r, c]) => {
      const el = cellEl(r, c);
      if (el) { el.classList.add('shake'); setTimeout(() => el.classList.remove('shake'), 350); }
    });
  }
}

function markFound(placement) {
  WH.foundWords.add(placement.word);
  placement.cells.forEach(([r, c]) => {
    const el = cellEl(r, c);
    if (el) el.classList.add('found');
  });

  const now = Date.now();
  WH.combo = (now - WH.lastFoundAt <= 6000) ? WH.combo + 1 : 1;
  WH.lastFoundAt = now;
  WH.bestCombo = Math.max(WH.bestCombo, WH.combo);
  updateComboUI();
  renderWordsList();
  playFoundSound();

  if (WH.foundWords.size >= WH.words.length) {
    endGame('all_found');
  }
}

function updateComboUI() {
  const badge = document.getElementById('wh-combo-badge');
  if (WH.combo >= 2) {
    badge.style.display = '';
    document.getElementById('wh-combo-val').textContent = WH.combo;
  } else {
    badge.style.display = 'none';
  }
}

// ================================================================
// TIMER
// ================================================================
function startTimer() {
  clearInterval(WH.timerHandle);
  WH.timerHandle = setInterval(() => {
    WH.timeLeft--;
    updateTimerUI();
    if (WH.timeLeft <= 0) endGame('time_up');
  }, 1000);
}

function updateTimerUI() {
  document.getElementById('wh-timer').textContent = Math.max(0, WH.timeLeft);
  const pct = Math.max(0, (WH.timeLeft / WH.totalTime) * 100);
  const fill = document.getElementById('wh-timer-fill');
  fill.style.width = pct + '%';
  fill.classList.toggle('low', WH.timeLeft <= 10);
}

// ================================================================
// POWER-UPS
// ================================================================
async function usePowerReveal() {
  const remaining = WH.placements.filter(p => !WH.foundWords.has(p.word));
  if (!remaining.length) return;
  const res = await G.spendCoins(10);
  if (!res.ok) { G.toast({ icon: '🪙', title: 'Not enough coins' }); return; }
  const p = remaining[(Math.random() * remaining.length) | 0];
  const [r, c] = p.cells[(Math.random() * p.cells.length) | 0];
  const el = cellEl(r, c);
  if (el) { el.classList.add('hint'); setTimeout(() => el.classList.remove('hint'), 1200); }
}

async function usePowerTime() {
  const res = await G.spendCoins(15);
  if (!res.ok) { G.toast({ icon: '🪙', title: 'Not enough coins' }); return; }
  WH.timeLeft += 15;
  WH.totalTime += 15;
  updateTimerUI();
  G.toast({ icon: '⏱️', title: '+15 seconds added!', duration: 2000 });
}

async function usePowerHint() {
  const remaining = WH.placements.filter(p => !WH.foundWords.has(p.word));
  if (!remaining.length) return;
  const res = await G.spendCoins(20);
  if (!res.ok) { G.toast({ icon: '🪙', title: 'Not enough coins' }); return; }
  const p = remaining[(Math.random() * remaining.length) | 0];
  p.cells.forEach(([r, c]) => {
    const el = cellEl(r, c);
    if (el) el.classList.add('hint');
  });
  setTimeout(() => {
    p.cells.forEach(([r, c]) => {
      const el = cellEl(r, c);
      if (el) el.classList.remove('hint');
    });
  }, 1200);
}

// ================================================================
// SOUND
// ================================================================
let WhAudioCtx = null;
function playFoundSound() {
  try {
    if (!WhAudioCtx) WhAudioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const o = WhAudioCtx.createOscillator();
    const g = WhAudioCtx.createGain();
    o.connect(g); g.connect(WhAudioCtx.destination);
    o.frequency.setValueAtTime(600, WhAudioCtx.currentTime);
    o.frequency.setValueAtTime(900, WhAudioCtx.currentTime + 0.08);
    g.gain.setValueAtTime(0.15, WhAudioCtx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.001, WhAudioCtx.currentTime + 0.3);
    o.start(); o.stop(WhAudioCtx.currentTime + 0.3);
  } catch (e) {}
}

// ================================================================
// END GAME
// ================================================================
async function endGame(reason) {
  clearInterval(WH.timerHandle);
  const durationSeconds = Math.round((Date.now() - WH.startedAt) / 1000);
  const found = WH.foundWords.size;
  const total = WH.words.length;

  document.getElementById('wh-r-found').textContent = `${found}/${total}`;
  document.getElementById('wh-r-combo').textContent = WH.bestCombo;
  document.getElementById('wh-r-time').textContent = `${durationSeconds}s`;

  const pct = found / total;
  if (pct >= 0.999) {
    document.getElementById('wh-result-emoji').textContent = '🏆';
    document.getElementById('wh-result-title').textContent = 'Perfect Hunt!';
  } else if (pct >= 0.5) {
    document.getElementById('wh-result-emoji').textContent = '🎉';
    document.getElementById('wh-result-title').textContent = 'Great Hunting!';
  } else {
    document.getElementById('wh-result-emoji').textContent = '📖';
    document.getElementById('wh-result-title').textContent = 'Keep Practicing!';
  }
  document.getElementById('wh-result-sub').textContent =
    reason === 'time_up' ? "Time's up! Here's how you did." : 'You found every word — amazing!';

  goToWh('wh-screen-results');

  const result = await G.completeGame({
    game_type: 'word_hunter',
    score: found,
    correct: found,
    total,
    duration_seconds: durationSeconds,
    combo: WH.bestCombo,
    meta: { grid_size: WH.size, daily: WH.daily, words_found: found },
  });
  G.applyGameResult(result);
}
