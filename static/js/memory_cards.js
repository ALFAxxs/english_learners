// ================================================================
// MEMORY CARDS — word/meaning matching game
// ================================================================

const MC = {
  pairs: 6,
  cards: [],          // [{uid, pairId, type, text, matched, flipped}]
  flipped: [],        // uids currently face-up (max 2)
  moves: 0,
  combo: 0,
  bestCombo: 0,
  matchedCount: 0,
  timerHandle: null,
  seconds: 0,
  startedAt: 0,
  locked: false,
};

function selectMcDifficulty(el, pairs) {
  document.querySelectorAll('#mc-difficulty-options .mc-option-btn').forEach(b => b.classList.remove('selected'));
  el.classList.add('selected');
  MC.pairs = pairs;
}

function goToMc(id) {
  document.querySelectorAll('.mc-screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  window.scrollTo(0, 0);
}

async function startMemoryCards() {
  let words = [];
  try {
    const res = await fetch(`${API_WORDS_URL}?count=${MC.pairs}`);
    const data = await res.json();
    words = data.words || [];
  } catch (e) { /* fall through */ }

  if (words.length < MC.pairs) {
    G.toast({ icon: '⚠️', title: 'Not enough words available', sub: 'Please ask an admin to seed the word bank.' });
    return;
  }
  words = words.slice(0, MC.pairs);

  const cards = [];
  words.forEach((w, i) => {
    cards.push({ uid: `${i}-word`, pairId: i, type: 'word', text: w.word, matched: false, flipped: false });
    cards.push({ uid: `${i}-meaning`, pairId: i, type: 'meaning', text: w.meaning, matched: false, flipped: false });
  });
  shuffle(cards);
  MC.cards = cards;
  MC.flipped = [];
  MC.moves = 0;
  MC.combo = 0;
  MC.bestCombo = 0;
  MC.matchedCount = 0;
  MC.seconds = 0;
  MC.locked = false;
  MC.startedAt = Date.now();

  renderMcGrid();
  updateMcStats();
  goToMc('mc-screen-game');
  startMcTimer();

  G.mountPlayerBar(document.getElementById('mc-player-bar-mount'));
  G.initPlayer();
}

function shuffle(arr) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = (Math.random() * (i + 1)) | 0;
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
}

function renderMcGrid() {
  const total = MC.cards.length;
  const cols = total <= 12 ? 4 : total <= 16 ? 4 : 6;
  const grid = document.getElementById('mc-grid');
  grid.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;
  grid.innerHTML = MC.cards.map(c => `
    <div class="mc-card" data-uid="${c.uid}" onclick="flipCard('${c.uid}')">
      <div class="mc-card-inner">
        <div class="mc-face mc-face-back">❓</div>
        <div class="mc-face mc-face-front ${c.type === 'word' ? 'word' : ''}">${c.text}</div>
      </div>
    </div>
  `).join('');
}

function cardEl(uid) {
  return document.querySelector(`.mc-card[data-uid="${uid}"]`);
}

function flipCard(uid) {
  if (MC.locked) return;
  const card = MC.cards.find(c => c.uid === uid);
  if (!card || card.matched || card.flipped) return;
  if (MC.flipped.length >= 2) return;

  card.flipped = true;
  cardEl(uid).classList.add('flipped');
  MC.flipped.push(uid);

  if (MC.flipped.length === 2) {
    MC.moves++;
    updateMcStats();
    MC.locked = true;
    const [uidA, uidB] = MC.flipped;
    const a = MC.cards.find(c => c.uid === uidA);
    const b = MC.cards.find(c => c.uid === uidB);

    if (a.pairId === b.pairId) {
      setTimeout(() => {
        a.matched = b.matched = true;
        cardEl(uidA).classList.add('matched');
        cardEl(uidB).classList.add('matched');
        MC.matchedCount++;
        MC.combo++;
        MC.bestCombo = Math.max(MC.bestCombo, MC.combo);
        updateComboUI();
        MC.flipped = [];
        MC.locked = false;
        playMcSound(true);
        if (MC.matchedCount >= MC.pairs) endMemoryGame();
      }, 450);
    } else {
      MC.combo = 0;
      updateComboUI();
      playMcSound(false);
      setTimeout(() => {
        cardEl(uidA).classList.add('mismatch');
        cardEl(uidB).classList.add('mismatch');
      }, 100);
      setTimeout(() => {
        a.flipped = b.flipped = false;
        cardEl(uidA).classList.remove('flipped', 'mismatch');
        cardEl(uidB).classList.remove('flipped', 'mismatch');
        MC.flipped = [];
        MC.locked = false;
      }, 900);
    }
  }
}

function updateMcStats() {
  document.getElementById('mc-moves').textContent = MC.moves;
  document.getElementById('mc-time').textContent = MC.seconds;
}

function updateComboUI() {
  const badge = document.getElementById('mc-combo-badge');
  if (MC.combo >= 2) {
    badge.style.display = '';
    document.getElementById('mc-combo-val').textContent = MC.combo;
  } else {
    badge.style.display = 'none';
  }
}

function startMcTimer() {
  clearInterval(MC.timerHandle);
  MC.timerHandle = setInterval(() => {
    MC.seconds++;
    document.getElementById('mc-time').textContent = MC.seconds;
  }, 1000);
}

let McAudioCtx = null;
function playMcSound(good) {
  try {
    if (!McAudioCtx) McAudioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const o = McAudioCtx.createOscillator();
    const g = McAudioCtx.createGain();
    o.connect(g); g.connect(McAudioCtx.destination);
    if (good) {
      o.frequency.setValueAtTime(523, McAudioCtx.currentTime);
      o.frequency.setValueAtTime(784, McAudioCtx.currentTime + 0.1);
    } else {
      o.frequency.setValueAtTime(280, McAudioCtx.currentTime);
    }
    g.gain.setValueAtTime(0.14, McAudioCtx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.001, McAudioCtx.currentTime + 0.3);
    o.start(); o.stop(McAudioCtx.currentTime + 0.3);
  } catch (e) {}
}

async function endMemoryGame() {
  clearInterval(MC.timerHandle);
  const duration = Math.round((Date.now() - MC.startedAt) / 1000);
  const parMoves = Math.round(MC.pairs * 1.6);
  const parTime = MC.pairs * 6;

  let stars = 1;
  if (MC.moves <= parMoves && duration <= parTime) stars = 3;
  else if (MC.moves <= parMoves * 1.5 && duration <= parTime * 1.6) stars = 2;

  document.getElementById('mc-stars').textContent = '⭐'.repeat(stars) + '☆'.repeat(3 - stars);
  document.getElementById('mc-result-title').textContent =
    stars === 3 ? 'Flawless Memory!' : stars === 2 ? 'Great Job!' : 'Good Effort!';
  document.getElementById('mc-result-sub').textContent =
    `You matched all ${MC.pairs} pairs in ${MC.moves} moves.`;
  document.getElementById('mc-r-time').textContent = `${duration}s`;
  document.getElementById('mc-r-moves').textContent = MC.moves;
  document.getElementById('mc-r-combo').textContent = MC.bestCombo;

  goToMc('mc-screen-results');

  const result = await G.completeGame({
    game_type: 'memory_cards',
    score: stars,
    correct: MC.pairs,
    total: MC.pairs,
    duration_seconds: duration,
    combo: MC.bestCombo,
    meta: { pairs: MC.pairs, moves: MC.moves, stars },
  });
  G.applyGameResult(result);
}
