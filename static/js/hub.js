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

// ================================================================
// ACCOUNT SAVE / RECOVER MODAL
// ================================================================
function openAccountModal() {
  document.getElementById('account-modal').style.display = 'flex';
}
function closeAccountModal() {
  document.getElementById('account-modal').style.display = 'none';
}

function switchAccountTab(tab) {
  const isSave = tab === 'save';
  document.getElementById('tab-save').classList.toggle('active', isSave);
  document.getElementById('tab-signin').classList.toggle('active', !isSave);
  document.getElementById('account-form-save').style.display = isSave ? '' : 'none';
  document.getElementById('account-form-signin').style.display = isSave ? 'none' : '';
}

async function submitSaveAccount() {
  const phone = document.getElementById('save-phone').value.trim();
  const password = document.getElementById('save-password').value;
  const errorEl = document.getElementById('save-error');
  errorEl.textContent = '';

  if (phone.replace(/\D/g, '').length < 9) { errorEl.textContent = "Telefon raqamni to'g'ri kiriting."; return; }
  if (password.length < 6) { errorEl.textContent = 'Parol kamida 6 ta belgidan iborat bo\'lishi kerak.'; return; }

  const data = await G.registerAccount(phone, password);
  if (data.ok) {
    closeAccountModal();
    G.toast({ icon: '✅', title: 'Progress saved!', sub: 'You can now recover it on any device with this phone number.' });
  } else {
    errorEl.textContent = data.error || 'Something went wrong.';
  }
}

async function submitSignIn() {
  const phone = document.getElementById('signin-phone').value.trim();
  const password = document.getElementById('signin-password').value;
  const errorEl = document.getElementById('signin-error');
  errorEl.textContent = '';

  if (!phone || !password) { errorEl.textContent = 'Telefon raqam va parolni kiriting.'; return; }

  const confirmed = confirm("Diqqat: ushbu qurilmadagi joriy progress almashtiriladi. Davom etasizmi?");
  if (!confirmed) return;

  const data = await G.loginAccount(phone, password);
  if (data.ok) {
    closeAccountModal();
    location.reload();
  } else {
    errorEl.textContent = data.error || 'Something went wrong.';
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
