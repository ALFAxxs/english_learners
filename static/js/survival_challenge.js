// ================================================================
// DAILY SURVIVAL CHALLENGE — branching real-life English conversations.
// Feedback/quality for each choice is only revealed AFTER picking it,
// fetched fresh from the server each step (no upfront answer key).
// ================================================================

const SV = {
  scenarios: [],
  scenario: null,       // {id, name, icon}
  goodCount: 0,
  okCount: 0,
  badCount: 0,
  totalChoices: 0,
  lastEndingQuality: 'neutral',
  startedAt: 0,
};

function goToSv(id) {
  document.querySelectorAll('.sv-screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  window.scrollTo(0, 0);
}

// ================================================================
// SCENARIO SELECT
// ================================================================
async function loadScenarios() {
  G.mountPlayerBar(document.getElementById('sv-player-bar-mount'));
  const profile = await G.initPlayer();
  if (!profile) return;

  try {
    const res = await fetch(`${API_SURVIVAL_SCENARIOS_URL}?uuid=${encodeURIComponent(profile.uuid)}`);
    const data = await res.json();
    if (!data.ok) return;
    SV.scenarios = data.scenarios;
    renderScenarioGrid();
  } catch (e) {
    document.getElementById('sv-scenario-grid').innerHTML = '<div class="sv-loading">Could not load scenarios.</div>';
  }
}

function renderScenarioGrid() {
  const grid = document.getElementById('sv-scenario-grid');
  const statusLabel = { good: '✅ Great ending', neutral: '➖ OK ending', bad: '⚠️ Rough ending' };
  grid.innerHTML = SV.scenarios.map(s => `
    <div class="sv-scenario-card" onclick="startScenario(${s.id}, '${escapeAttr(s.name)}', '${s.icon}')">
      <div class="icon">${s.icon}</div>
      <div class="name">${s.name}</div>
      <div class="desc">${s.description}</div>
      ${s.best_ending_quality ? `<div class="status ${s.best_ending_quality}">${statusLabel[s.best_ending_quality] || ''}</div>` : `<div class="status">Not played yet</div>`}
    </div>
  `).join('');
}

function escapeAttr(s) {
  return String(s).replace(/'/g, "\\'");
}

// ================================================================
// START A SCENARIO
// ================================================================
async function startScenario(id, name, icon) {
  SV.scenario = { id, name, icon };
  SV.goodCount = 0;
  SV.okCount = 0;
  SV.badCount = 0;
  SV.totalChoices = 0;
  SV.lastEndingQuality = 'neutral';
  SV.startedAt = Date.now();

  document.getElementById('sv-scenario-name').textContent = `${icon} ${name}`;
  document.getElementById('sv-chat-log').innerHTML = '';
  document.getElementById('sv-choices').innerHTML = '';

  try {
    const res = await fetch(`${API_SURVIVAL_START_URL}?scenario_id=${id}`);
    const data = await res.json();
    if (!data.ok) {
      G.toast({ icon: '⚠️', title: 'Could not start this scenario.' });
      return;
    }
    goToSv('sv-screen-conversation');
    renderNode(data.node);
  } catch (e) {
    G.toast({ icon: '⚠️', title: 'Network error, please try again.' });
  }
}

// ================================================================
// RENDER A NODE (NPC line + choices, or an ending)
// ================================================================
function renderNode(node) {
  appendBubble('npc', node.npc_line);

  if (node.is_ending) {
    SV.lastEndingQuality = node.ending_quality || 'neutral';
    document.getElementById('sv-choices').innerHTML = '';
    setTimeout(() => endScenario(), 1200);
    return;
  }

  const choicesEl = document.getElementById('sv-choices');
  choicesEl.innerHTML = node.choices.map(c => `
    <button class="sv-choice-btn" onclick="chooseOption(${c.id}, this)">${c.text}</button>
  `).join('');
}

function appendBubble(kind, text, qualityClass) {
  const log = document.getElementById('sv-chat-log');
  const div = document.createElement('div');
  div.className = `sv-bubble ${kind}${qualityClass ? ' ' + qualityClass : ''}`;
  div.textContent = text;
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
}

// ================================================================
// CHOOSE AN OPTION
// ================================================================
async function chooseOption(choiceId, btnEl) {
  const choicesEl = document.getElementById('sv-choices');
  choicesEl.querySelectorAll('.sv-choice-btn').forEach(b => { b.disabled = true; });

  appendBubble('player', btnEl.textContent);
  SV.totalChoices++;

  try {
    const res = await fetch(API_SURVIVAL_CHOOSE_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': window.CSRF_TOKEN || '' },
      body: JSON.stringify({ choice_id: choiceId }),
    });
    const data = await res.json();
    if (!data.ok) return;

    if (data.quality === 'good') SV.goodCount++;
    else if (data.quality === 'ok') SV.okCount++;
    else SV.badCount++;

    appendBubble('feedback', data.feedback, data.quality);
    choicesEl.innerHTML = '';

    setTimeout(() => renderNode(data.next_node), 1400);
  } catch (e) {
    G.toast({ icon: '⚠️', title: 'Network error, please try again.' });
  }
}

// ================================================================
// END SCENARIO
// ================================================================
async function endScenario() {
  const duration = Math.round((Date.now() - SV.startedAt) / 1000);

  document.getElementById('sv-r-good').textContent = SV.goodCount;
  document.getElementById('sv-r-ok').textContent = SV.okCount;
  document.getElementById('sv-r-bad').textContent = SV.badCount;

  const emoji = { good: '🎉', neutral: '🙂', bad: '😅' }[SV.lastEndingQuality] || '🙂';
  const title = {
    good: 'Great Conversation!', neutral: 'Conversation Complete',
    bad: 'A Bit Rocky — Try Again!',
  }[SV.lastEndingQuality] || 'Conversation Complete';
  document.getElementById('sv-result-emoji').textContent = emoji;
  document.getElementById('sv-result-title').textContent = title;
  document.getElementById('sv-result-sub').textContent =
    `You made ${SV.totalChoices} choices in the ${SV.scenario.name} scenario.`;

  goToSv('sv-screen-results');

  const response = await fetch(API_SURVIVAL_COMPLETE_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': window.CSRF_TOKEN || '' },
    body: JSON.stringify({
      uuid: G.getPlayerId(), scenario_id: SV.scenario.id,
      good_count: SV.goodCount, ok_count: SV.okCount, bad_count: SV.badCount,
      total_choices: SV.totalChoices, ending_quality: SV.lastEndingQuality,
      duration_seconds: duration,
    }),
  });
  const data = await response.json();
  G.applyGameResult(data);
}

document.addEventListener('DOMContentLoaded', loadScenarios);
