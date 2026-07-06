// ================================================================
// GAMIFICATION SHARED KIT
// Player bootstrap, XP/level/streak/coin state, toasts, confetti,
// theme toggle. Loaded on every page. Exposes window.G
// ================================================================
(function () {
  const STORAGE_KEY = 'vq_player_id';
  const THEME_KEY = 'vq_theme';
  const NAME_KEY = 'vq_player_name';

  let profile = null;
  const listeners = [];

  function csrf() {
    return window.CSRF_TOKEN || '';
  }

  function uuidv4() {
    if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = (Math.random() * 16) | 0;
      const v = c === 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  }

  function getPlayerId() {
    let id = localStorage.getItem(STORAGE_KEY);
    if (!id) {
      id = uuidv4();
      localStorage.setItem(STORAGE_KEY, id);
    }
    return id;
  }

  function getSavedName() {
    return localStorage.getItem(NAME_KEY) || '';
  }

  function saveName(name) {
    if (name) localStorage.setItem(NAME_KEY, name);
  }

  async function initPlayer(name) {
    const uuid = getPlayerId();
    const finalName = name || getSavedName() || 'Player';
    saveName(finalName);
    try {
      const res = await fetch('/api/g/player/init/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf() },
        body: JSON.stringify({ uuid, name: finalName }),
      });
      const data = await res.json();
      if (data.ok) {
        profile = data.profile;
        notify();
      }
    } catch (e) { /* offline-safe */ }
    return profile;
  }

  function notify() {
    listeners.forEach((fn) => { try { fn(profile); } catch (e) {} });
  }

  function onProfileChange(fn) {
    listeners.push(fn);
    if (profile) fn(profile);
  }

  async function completeGame(payload) {
    const uuid = getPlayerId();
    try {
      const res = await fetch('/api/g/game/complete/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf() },
        body: JSON.stringify({ uuid, ...payload }),
      });
      const data = await res.json();
      if (data.ok) {
        profile = data.profile;
        notify();
      }
      return data;
    } catch (e) {
      return { ok: false, error: String(e) };
    }
  }

  async function claimDaily() {
    const uuid = getPlayerId();
    try {
      const res = await fetch(`/api/g/player/${uuid}/claim-daily/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrf() },
      });
      const data = await res.json();
      if (data.ok) { profile = data.profile; notify(); }
      return data;
    } catch (e) {
      return { ok: false, error: String(e) };
    }
  }

  async function spendCoins(amount) {
    const uuid = getPlayerId();
    try {
      const res = await fetch('/api/g/coins/spend/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf() },
        body: JSON.stringify({ uuid, amount }),
      });
      const data = await res.json();
      if (data.ok && profile) { profile.coins = data.coins; notify(); }
      return data;
    } catch (e) {
      return { ok: false };
    }
  }

  // ============================================================
  // THEME
  // ============================================================
  function initTheme() {
    const saved = localStorage.getItem(THEME_KEY);
    if (saved) document.documentElement.dataset.theme = saved;
    updateThemeToggleIcon();
  }

  function toggleTheme() {
    const current = document.documentElement.dataset.theme ||
      (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    localStorage.setItem(THEME_KEY, next);
    updateThemeToggleIcon();
  }

  function updateThemeToggleIcon() {
    const btn = document.querySelector('.theme-toggle');
    if (!btn) return;
    const current = document.documentElement.dataset.theme ||
      (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    btn.textContent = current === 'dark' ? '☀️' : '🌙';
  }

  // ============================================================
  // TOASTS
  // ============================================================
  function ensureToastStack() {
    let stack = document.getElementById('toast-stack');
    if (!stack) {
      stack = document.createElement('div');
      stack.id = 'toast-stack';
      document.body.appendChild(stack);
    }
    return stack;
  }

  function toast({ icon = '✨', title = '', sub = '', type = '' , duration = 4200}) {
    const stack = ensureToastStack();
    const el = document.createElement('div');
    el.className = `g-toast ${type}`;
    el.innerHTML = `
      <div class="icon">${icon}</div>
      <div>
        <div class="title">${title}</div>
        ${sub ? `<div class="sub">${sub}</div>` : ''}
      </div>`;
    stack.appendChild(el);
    setTimeout(() => {
      el.classList.add('leaving');
      setTimeout(() => el.remove(), 320);
    }, duration);
  }

  // ============================================================
  // CONFETTI
  // ============================================================
  function confettiBurst(originX, originY) {
    let canvas = document.getElementById('confetti-canvas');
    if (!canvas) {
      canvas = document.createElement('canvas');
      canvas.id = 'confetti-canvas';
      document.body.appendChild(canvas);
    }
    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    canvas.width = window.innerWidth * dpr;
    canvas.height = window.innerHeight * dpr;
    canvas.style.width = window.innerWidth + 'px';
    canvas.style.height = window.innerHeight + 'px';
    ctx.scale(dpr, dpr);

    const colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#34d399'];
    const ox = originX ?? window.innerWidth / 2;
    const oy = originY ?? window.innerHeight / 3;
    const particles = Array.from({ length: 90 }, () => ({
      x: ox, y: oy,
      vx: (Math.random() - 0.5) * 14,
      vy: Math.random() * -14 - 4,
      size: Math.random() * 7 + 4,
      color: colors[(Math.random() * colors.length) | 0],
      rot: Math.random() * Math.PI * 2,
      vr: (Math.random() - 0.5) * 0.3,
      life: 0,
    }));

    let frame = 0;
    const maxFrames = 110;
    function tick() {
      ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
      particles.forEach((p) => {
        p.vy += 0.35;
        p.x += p.vx;
        p.y += p.vy;
        p.rot += p.vr;
        p.life++;
        ctx.save();
        ctx.globalAlpha = Math.max(0, 1 - frame / maxFrames);
        ctx.translate(p.x, p.y);
        ctx.rotate(p.rot);
        ctx.fillStyle = p.color;
        ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 0.6);
        ctx.restore();
      });
      frame++;
      if (frame < maxFrames) requestAnimationFrame(tick);
      else ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
    }
    tick();
  }

  // ============================================================
  // LEVEL-UP MODAL
  // ============================================================
  function showLevelUpModal(newLevel) {
    const overlay = document.createElement('div');
    overlay.className = 'g-modal-overlay';
    overlay.innerHTML = `
      <div class="g-modal">
        <div class="big-emoji">🏆</div>
        <h3>Level Up!</h3>
        <p>You've reached <strong>Level ${newLevel}</strong>. Keep learning to unlock more rewards!</p>
        <button class="btn btn-primary">Awesome! 🎉</button>
      </div>`;
    document.body.appendChild(overlay);
    confettiBurst();
    const close = () => overlay.remove();
    overlay.querySelector('button').addEventListener('click', close);
    overlay.addEventListener('click', (e) => { if (e.target === overlay) close(); });
  }

  // ============================================================
  // APPLY GAME RESULT — call this after any /api/g/game/complete/ response
  // ============================================================
  function applyGameResult(data) {
    if (!data || !data.ok) return;

    if (data.xp_earned > 0 || data.coins_earned > 0) {
      toast({
        icon: '⭐',
        title: `+${data.xp_earned} XP  ·  +${data.coins_earned} 🪙`,
        sub: 'Great work! Keep the momentum going.',
        type: '',
      });
    }

    if (data.streak_broken) {
      toast({ icon: '💔', title: 'Streak reset', sub: 'Play daily to protect your streak!', type: 'streak-broken' });
    } else if (data.streak > 1) {
      toast({ icon: '🔥', title: `${data.streak}-day streak!`, sub: 'You are on fire — don’t stop now.', type: '' });
    }

    (data.new_achievements || []).forEach((a, i) => {
      setTimeout(() => {
        toast({
          icon: a.icon, title: `Achievement Unlocked: ${a.title}`,
          sub: `${a.description} · +${a.xp_reward} XP +${a.coin_reward} 🪙`,
          type: 'achievement', duration: 5200,
        });
      }, i * 900);
    });

    if (data.level_up) {
      setTimeout(() => showLevelUpModal(data.new_level), 500);
    } else if (data.xp_earned > 0) {
      confettiBurst();
    }
  }

  function initials(name) {
    return (name || 'P').trim().slice(0, 2).toUpperCase();
  }

  function playerBarHTML(p) {
    if (!p) return '';
    const streakHot = p.current_streak >= 3 ? 'hot' : '';
    const pct = Math.min(100, (p.level_progress_xp / p.level_needed_xp) * 100);
    return `
      <div class="player-bar">
        <div class="avatar-ring">${initials(p.name)}<div class="lvl-badge">Lv${p.level}</div></div>
        <div class="player-name-xp">
          <div class="player-name">${p.name}</div>
          <div class="xp-bar-track"><div class="xp-bar-fill" style="width:${pct}%"></div></div>
        </div>
        <div class="stat-pill coins">🪙 ${p.coins}</div>
        <div class="stat-pill streak ${streakHot}">🔥 ${p.current_streak}</div>
      </div>`;
  }

  function mountPlayerBar(el) {
    if (!el) return;
    onProfileChange((p) => { el.innerHTML = playerBarHTML(p); });
  }

  window.G = {
    getPlayerId, getSavedName, saveName, initPlayer, onProfileChange,
    completeGame, claimDaily, spendCoins, applyGameResult,
    initTheme, toggleTheme,
    toast, confettiBurst, showLevelUpModal,
    playerBarHTML, mountPlayerBar,
    get profile() { return profile; },
  };

  document.addEventListener('DOMContentLoaded', initTheme);
})();
