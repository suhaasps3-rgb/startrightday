'use strict';

/* ============================================================
   StartRightDay — App Logic
   ============================================================ */

// ─── Configuration ─────────────────────────────────────────────────────────
const CONFIG = {
  // API is hosted on Vercel serverless functions, so we use relative paths
  API_URL: '',

  SPLASH_DURATION: 2600,
  LOADING_MESSAGES: [
    'Calculating Panchang...',
    'Finding your Nakshatra...',
    'Checking Tarabalam...',
    'Filtering Rahu Kalam...',
    'Applying Vedic rules...',
    'Generating recommendation...',
  ],
  MESSAGE_INTERVAL: 950,
};

// ─── State ──────────────────────────────────────────────────────────────────
const state = {
  screen: 'splash',
  slide: 0,
  loadingTimer: null,
  msgTimer: null,
  msgIndex: 0,
};

// ─── Storage ────────────────────────────────────────────────────────────────
const storage = {
  save(d) {
    try { localStorage.setItem('srd_birth', JSON.stringify(d)); } catch {}
  },
  load() {
    try { return JSON.parse(localStorage.getItem('srd_birth')); } catch { return null; }
  },
  isOnboarded() { return localStorage.getItem('srd_onboarded') === 'true'; },
  markOnboarded() { localStorage.setItem('srd_onboarded', 'true'); },
};

// ─── API ────────────────────────────────────────────────────────────────────
const api = {
  async recommend(payload) {
    const resp = await fetch(`${CONFIG.API_URL}/api/v1/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      throw new Error(err.detail || `Server error (${resp.status}). Please try again.`);
    }
    return resp.json();
  },
};

// ─── Screen Controller ───────────────────────────────────────────────────────
function goTo(name) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  const next = document.getElementById(`screen-${name}`);
  if (next) next.classList.add('active');
  state.screen = name;
}

// ─── Splash ─────────────────────────────────────────────────────────────────
function initSplash() {
  setTimeout(() => {
    if (storage.isOnboarded()) {
      goTo('home');
      hydrateSavedData();
    } else {
      goTo('onboarding');
    }
  }, CONFIG.SPLASH_DURATION);
}

// ─── Onboarding ─────────────────────────────────────────────────────────────
const TOTAL_SLIDES = 3;

function initOnboarding() {
  document.getElementById('ob-skip').addEventListener('click', finishOnboarding);
  document.getElementById('ob-next').addEventListener('click', nextSlide);
}

function nextSlide() {
  if (state.slide < TOTAL_SLIDES - 1) {
    setSlide(state.slide + 1);
  } else {
    finishOnboarding();
  }
}

function setSlide(i) {
  // Exit current
  const current = document.querySelector(`.slide[data-slide="${state.slide}"]`);
  if (current) {
    current.classList.remove('active');
    current.classList.add('exit');
    setTimeout(() => current.classList.remove('exit'), 350);
  }

  state.slide = i;

  // Enter next
  const next = document.querySelector(`.slide[data-slide="${i}"]`);
  if (next) next.classList.add('active');

  // Dots
  document.querySelectorAll('.dot').forEach(d => d.classList.remove('active'));
  const activeDot = document.querySelector(`.dot[data-dot="${i}"]`);
  if (activeDot) activeDot.classList.add('active');

  // Button label
  const btn = document.getElementById('ob-next');
  btn.textContent = i === TOTAL_SLIDES - 1 ? 'Get Started' : 'Continue';
}

function finishOnboarding() {
  storage.markOnboarded();
  goTo('home');
}

// ─── Home ────────────────────────────────────────────────────────────────────
function initHome() {
  // Set activity date default to today
  const today = new Date();
  const todayStr = formatDateISO(today);
  const ainput = document.getElementById('inp-adate');
  ainput.value = todayStr;
  ainput.min = todayStr;

  // Birth date max = today
  document.getElementById('inp-bdate').max = todayStr;

  document.getElementById('home-form').addEventListener('submit', handleFormSubmit);
}

function hydrateSavedData() {
  const saved = storage.load();
  if (!saved) return;
  document.getElementById('inp-place').value = saved.birth_place || '';
  document.getElementById('inp-bdate').value = saved.birth_date || '';
  document.getElementById('inp-btime').value = saved.birth_time || '';
}

function formatDateISO(d) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

function clearErrors() {
  ['place', 'bdate', 'btime', 'adate'].forEach(k => {
    const fg = document.getElementById(`fg-${k}`);
    const err = document.getElementById(`err-${k}`);
    if (fg) fg.classList.remove('has-error');
    if (err) err.textContent = '';
  });
}

function showError(key, msg) {
  const fg = document.getElementById(`fg-${key}`);
  const err = document.getElementById(`err-${key}`);
  if (fg) fg.classList.add('has-error');
  if (err) err.textContent = msg;
}

function validate() {
  clearErrors();
  let ok = true;
  const place = document.getElementById('inp-place').value.trim();
  const bdate = document.getElementById('inp-bdate').value;
  const btime = document.getElementById('inp-btime').value;
  const adate = document.getElementById('inp-adate').value;

  if (!place) { showError('place', 'Please enter a birth place'); ok = false; }
  if (!bdate) { showError('bdate', 'Please select birth date'); ok = false; }
  if (!btime) { showError('btime', 'Please select birth time'); ok = false; }
  if (!adate) { showError('adate', 'Please select activity date'); ok = false; }
  return ok;
}

async function handleFormSubmit(e) {
  e.preventDefault();
  if (!validate()) return;

  const payload = {
    birth_place: document.getElementById('inp-place').value.trim(),
    birth_date:  document.getElementById('inp-bdate').value,
    birth_time:  document.getElementById('inp-btime').value,
    activity_date: document.getElementById('inp-adate').value,
  };

  // Save birth details
  storage.save({
    birth_place: payload.birth_place,
    birth_date:  payload.birth_date,
    birth_time:  payload.birth_time,
  });

  // Navigate to loading
  goTo('loading');
  startLoadingMessages();

  try {
    const result = await api.recommend(payload);
    stopLoadingMessages();
    renderResult(result);
    goTo('result');
  } catch (err) {
    stopLoadingMessages();
    renderError(err.message);
    goTo('result');
  }
}

// ─── Loading ─────────────────────────────────────────────────────────────────
function startLoadingMessages() {
  state.msgIndex = 0;
  const el = document.getElementById('loading-msg');
  el.textContent = CONFIG.LOADING_MESSAGES[0];

  state.msgTimer = setInterval(() => {
    el.classList.add('fading');
    setTimeout(() => {
      state.msgIndex = (state.msgIndex + 1) % CONFIG.LOADING_MESSAGES.length;
      el.textContent = CONFIG.LOADING_MESSAGES[state.msgIndex];
      el.classList.remove('fading');
    }, 300);
  }, CONFIG.MESSAGE_INTERVAL);
}

function stopLoadingMessages() {
  if (state.msgTimer) { clearInterval(state.msgTimer); state.msgTimer = null; }
}

// ─── Result ──────────────────────────────────────────────────────────────────
function renderResult(data) {
  // Status banner
  const banner = document.getElementById('status-banner');
  const icon   = document.getElementById('status-icon');
  const label  = document.getElementById('status-label');
  const sub    = document.getElementById('status-sub');

  banner.className = 'status-banner';
  icon.className   = 'status-icon';
  label.className  = 'status-label';
  sub.className    = 'status-sub';

  if (data.status === 'auspicious') {
    banner.classList.add('status-banner--auspicious');
    icon.classList.add('status-icon--auspicious');
    icon.textContent = '✓';
    label.classList.add('status-label--auspicious');
    label.textContent = 'Auspicious Day';
    sub.classList.add('status-sub--auspicious');
    sub.textContent = data.birth_nakshatra ? `Birth Nakshatra: ${data.birth_nakshatra}` : '';
  } else {
    banner.classList.add('status-banner--avoid');
    icon.classList.add('status-icon--avoid');
    icon.textContent = '⚠';
    label.classList.add('status-label--avoid');
    label.textContent = 'Avoid New Starts';
    sub.classList.add('status-sub--avoid');
    sub.textContent = data.birth_nakshatra ? `Birth Nakshatra: ${data.birth_nakshatra}` : '';
  }

  // Date
  document.getElementById('result-date').textContent = data.activity_date_display || '';

  // Cards vs empty
  const cardsList  = document.getElementById('cards-list');
  const emptyState = document.getElementById('empty-state');
  const errorState = document.getElementById('error-state');
  if (errorState) errorState.classList.add('hidden');

  cardsList.innerHTML = '';

  if (data.intervals && data.intervals.length > 0) {
    emptyState.classList.add('hidden');
    data.intervals.forEach((iv, i) => {
      const card = buildCard(iv, i);
      cardsList.appendChild(card);
    });
  } else {
    emptyState.classList.remove('hidden');
    emptyState.querySelector('.empty-icon').textContent = '🌙';
    emptyState.querySelector('.empty-title').textContent = 'No Auspicious Time Found';
    document.getElementById('empty-body').textContent =
      data.message || 'No auspicious time found today. Consider choosing a different date.';
  }
}

function renderError(msg) {
  const banner = document.getElementById('status-banner');
  const icon   = document.getElementById('status-icon');
  const label  = document.getElementById('status-label');
  const sub    = document.getElementById('status-sub');
  const cardsList  = document.getElementById('cards-list');
  const emptyState = document.getElementById('empty-state');

  emptyState.classList.add('hidden');
  cardsList.innerHTML = '';

  banner.className = 'status-banner status-banner--avoid';
  icon.className   = 'status-icon status-icon--avoid';
  icon.textContent = '⚠';
  label.className  = 'status-label status-label--avoid';
  label.textContent = 'Connection Error';
  sub.className    = 'status-sub status-sub--avoid';
  sub.textContent  = '';
  document.getElementById('result-date').textContent = '';

  emptyState.classList.remove('hidden');
  emptyState.querySelector('.empty-icon').textContent = '⚠️';
  emptyState.querySelector('.empty-title').textContent = 'Could not connect';
  document.getElementById('empty-body').textContent = msg || 'Please check your connection and try again.';
}

function buildCard(iv, index) {
  const card = document.createElement('div');
  card.className = 'interval-card';
  card.style.animationDelay = `${index * 80}ms`;

  const p = iv.panchang;
  const activities = iv.activities || [];

  card.innerHTML = `
    <div class="card-header">
      <div>
        <div class="card-time-label">BEST TIME WINDOW</div>
        <div class="card-time">${iv.start_time} – ${iv.end_time}</div>
      </div>
      <div class="recommended-badge">
        <span class="badge-dot"></span>
        <span class="badge-text">Recommended</span>
      </div>
    </div>

    <div class="card-panchang">
      <div class="card-section-label">PANCHANG DETAILS</div>
      <div class="panchang-grid">
        <div class="panchang-row">
          <span class="panchang-label">Nakshatra</span>
          <span class="panchang-value">${p.nakshatra}</span>
        </div>
        <div class="panchang-row">
          <span class="panchang-label">Tara</span>
          <span class="panchang-value">${p.tara}</span>
        </div>
        <div class="panchang-row">
          <span class="panchang-label">Tithi</span>
          <span class="panchang-value">${p.tithi}</span>
        </div>
        <div class="panchang-row">
          <span class="panchang-label">Yoga</span>
          <span class="panchang-value">${p.yoga}</span>
        </div>
        <div class="panchang-row">
          <span class="panchang-label">Karana</span>
          <span class="panchang-value">${p.karana}</span>
        </div>
      </div>
    </div>

    ${activities.length > 0 ? `
    <div class="card-activities">
      <div class="card-section-label">GOOD FOR</div>
      <div class="activities-chips">
        ${activities.map(a => `<span class="chip">${a}</span>`).join('')}
      </div>
    </div>
    ` : ''}
  `;

  return card;
}

// ─── Back navigation ─────────────────────────────────────────────────────────
function initResultScreen() {
  document.getElementById('result-back').addEventListener('click', () => goTo('home'));
  document.getElementById('result-retry').addEventListener('click', () => goTo('home'));
}

// ─── Init ────────────────────────────────────────────────────────────────────
function init() {
  initOnboarding();
  initHome();
  initResultScreen();
  initSplash();
}

document.addEventListener('DOMContentLoaded', init);
