async function getState() {
  const r = await fetch('/api/state');
  return r.json();
}

async function sendMove(move) {
  const r = await fetch('/api/move', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ move })
  });
  return r.json();
}

async function resetGame() {
  await fetch('/api/reset', { method: 'POST' });
}

function setText(id, text) { document.getElementById(id).textContent = text; }
function appendLog(text) {
  const el = document.getElementById('log');
  const line = document.createElement('div');
  line.textContent = text;
  el.prepend(line);
}

// --- Arcade UI helpers ---
function updateProgress(current, max) {
  const pct = Math.min(100, Math.max(0, ((current - 1) / max) * 100));
  const bar = document.getElementById('progressBar');
  if (bar) bar.style.width = pct + '%';
}

function showBanner(text) {
  const el = document.getElementById('banner');
  const span = document.getElementById('bannerText');
  if (!el || !span) return;
  span.textContent = text;
  el.classList.remove('hidden');
  setTimeout(() => el.classList.add('hidden'), 1200);
}

function setControlsEnabled(enabled) {
  document.querySelectorAll('.move').forEach(b => (b.disabled = !enabled));
}

function setBombEnabled(available) {
  const b = document.getElementById('bombBtn');
  if (b) b.disabled = !available;
}

// Tiny particle burst effect near top center
function burst(color = '#22d3ee') {
  const canvas = document.getElementById('fxCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const { innerWidth: w, innerHeight: h } = window;
  canvas.width = w;
  canvas.height = h;
  const parts = Array.from({ length: 60 }).map(() => ({
    x: w / 2,
    y: h / 3,
    vx: (Math.random() - 0.5) * 6,
    vy: Math.random() * -5 - 2,
    life: 60,
  }));
  function tick() {
    ctx.clearRect(0, 0, w, h);
    parts.forEach((p) => {
      p.x += p.vx;
      p.y += p.vy;
      p.vy += 0.12;
      p.life--;
      ctx.fillStyle = color;
      ctx.globalAlpha = Math.max(0, p.life / 60);
      ctx.fillRect(p.x, p.y, 3, 3);
    });
    ctx.globalAlpha = 1;
    if (parts.some((p) => p.life > 0)) requestAnimationFrame(tick);
  }
  tick();
}

function updateUI(state) {
  setText('userScore', state.user.score);
  setText('botScore', state.bot.score);
  const maxR = state.max_rounds || 3;
  const displayRound = Math.min(state.current_round, maxR);
  setText('round', `${displayRound}/${maxR}`);
  document.getElementById('userBomb').textContent = state.user.bomb_used ? 'Bomb used' : 'Bomb available';
  document.getElementById('botBomb').textContent = state.bot.bomb_used ? 'Bomb used' : 'Bomb available';
  setBombEnabled(!state.user.bomb_used);
  updateProgress(state.current_round, maxR);
  setControlsEnabled(!state.game_over);
}

async function init() {
  const s = await getState();
  updateUI(s);
  showBanner('Ready?');
}

async function onMoveClick(e) {
  const move = e.currentTarget.getAttribute('data-move');
  setControlsEnabled(false);
  const res = await sendMove(move);
  const s = await getState();
  updateUI({ ...s, max_rounds: s.max_rounds });

  const botMove = res.bot_move;
  appendLog(`You: ${move} | Bot: ${botMove} => ${String(res.result).toUpperCase()} - ${res.message}`);
  showBanner(String(res.result).toUpperCase());
  if (String(res.result) === 'win') burst('#34d399');
  if (String(res.result) === 'lose') burst('#f87171');

  if (res.state.game_over) {
    const finalMsg = res.state.winner === 'user' ? 'You win the game!' : res.state.winner === 'bot' ? 'Bot wins the game!' : "It's a draw!";
    appendLog(`Game Over. Final Score You ${res.state.user.score} - ${res.state.bot.score} Bot. ${finalMsg}`);
    showBanner('GAME OVER');
    setControlsEnabled(false);
  } else {
    setControlsEnabled(true);
  }
}

async function onReset() {
  await resetGame();
  document.getElementById('log').innerHTML = '';
  const s = await getState();
  updateUI(s);
  showBanner('New Game');
}

window.addEventListener('DOMContentLoaded', async () => {
  await init();
  document.querySelectorAll('.move').forEach(btn => btn.addEventListener('click', onMoveClick));
  document.getElementById('resetBtn').addEventListener('click', onReset);
  const canvas = document.getElementById('fxCanvas');
  if (canvas) { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
  window.addEventListener('resize', () => {
    const canvas = document.getElementById('fxCanvas');
    if (!canvas) return;
    canvas.width = window.innerWidth; canvas.height = window.innerHeight;
  });
});
