// ================================================================
// HUB PAGE LOGIC
// ================================================================

function renderPlayerBar(profile) {
  if (!profile) return;
  document.getElementById('player-bar-mount').innerHTML = G.playerBarHTML(profile);
  document.getElementById('hero-name').textContent = profile.name;
}

async function claimDailyReward() {
  const btn = document.getElementById('daily-reward-btn');
  btn.disabled = true;
  const data = await G.claimDaily();
  if (data.ok && data.claimed) {
    G.toast({
      icon: '🎁', title: `Daily Reward: +${data.coins_awarded} 🪙 +${data.xp_awarded} XP`,
      sub: `Day ${data.day_in_cycle} of your streak cycle`, type: 'achievement', duration: 5000,
    });
    G.confettiBurst();
    btn.textContent = '✅ Claimed for Today';
  } else if (data.ok) {
    G.toast({ icon: '⏳', title: 'Already claimed today', sub: 'Come back tomorrow for more!', duration: 3200 });
    btn.textContent = '✅ Claimed for Today';
  } else {
    btn.disabled = false;
  }
}

async function loadAchievements(uuid) {
  try {
    const res = await fetch(`/api/g/achievements/?uuid=${encodeURIComponent(uuid)}`);
    const data = await res.json();
    if (!data.ok) return;
    const shelf = document.getElementById('achv-shelf');
    shelf.innerHTML = data.achievements.map((a) => `
      <div class="achv-chip ${a.unlocked ? 'unlocked' : ''}" title="${a.description}">
        <div class="ico">${a.icon}</div>
        <div class="lbl">${a.title}</div>
      </div>`).join('');
  } catch (e) {}
}

function submitName() {
  const val = document.getElementById('name-modal-input').value.trim();
  if (!val) return;
  document.getElementById('name-modal').style.display = 'none';
  bootPlayer(val);
}

async function bootPlayer(name) {
  const profile = await G.initPlayer(name);
  if (profile) {
    renderPlayerBar(profile);
    loadAchievements(profile.uuid);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  G.onProfileChange(renderPlayerBar);
  const savedName = G.getSavedName();
  if (!savedName) {
    document.getElementById('name-modal').style.display = 'flex';
    document.getElementById('name-modal-input').focus();
  } else {
    bootPlayer(savedName);
  }
});
