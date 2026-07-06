async function switchScope(scope, el) {
  document.querySelectorAll('.lb-tab').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  await loadLeaderboard(scope);
}

async function loadLeaderboard(scope) {
  const list = document.getElementById('lb-list');
  list.innerHTML = '<div class="lb-empty">Loading…</div>';
  try {
    const res = await fetch(`/api/g/leaderboard/?scope=${scope}`);
    const data = await res.json();
    if (!data.ok || !data.players.length) {
      list.innerHTML = '<div class="lb-empty">No players yet. Be the first to play!</div>';
      return;
    }
    list.innerHTML = data.players.map((p, i) => {
      const rank = i + 1;
      const topClass = rank <= 3 ? `top${rank}` : '';
      const medal = rank === 1 ? '🥇' : rank === 2 ? '🥈' : rank === 3 ? '🥉' : rank;
      return `
        <div class="lb-row ${topClass}">
          <div class="lb-rank">${medal}</div>
          <div class="lb-avatar">${(p.name || 'P').slice(0, 2).toUpperCase()}</div>
          <div class="lb-info">
            <div class="lb-name">${p.name}</div>
            <div class="lb-meta">Level ${p.level} · 🔥 ${p.current_streak}-day streak</div>
          </div>
          <div class="lb-xp">${p.xp} XP</div>
        </div>`;
    }).join('');
  } catch (e) {
    list.innerHTML = '<div class="lb-empty">Could not load leaderboard.</div>';
  }
}

document.addEventListener('DOMContentLoaded', () => loadLeaderboard('alltime'));
