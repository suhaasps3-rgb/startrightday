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
  getProfiles() {
    try { 
      const p = JSON.parse(localStorage.getItem('srd_profiles')); 
      return Array.isArray(p) ? p : [];
    } catch { return []; }
  },
  saveProfiles(profiles) {
    try { localStorage.setItem('srd_profiles', JSON.stringify(profiles)); } catch {}
  },
  getActiveProfileId() {
    return localStorage.getItem('srd_active_profile');
  },
  setActiveProfileId(id) {
    if (id) localStorage.setItem('srd_active_profile', id);
    else localStorage.removeItem('srd_active_profile');
  },
  // Transient save for when user checks time without explicitly saving profile
  saveTransient(d) {
    try { localStorage.setItem('srd_birth', JSON.stringify(d)); } catch {}
  },
  loadTransient() {
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
  hydrateSavedData();
}

// ─── Home ────────────────────────────────────────────────────────────────────
function populateDateDropdowns() {
  const daySel = document.getElementById('inp-bdate-day');
  const monthSel = document.getElementById('inp-bdate-month');
  const yearSel = document.getElementById('inp-bdate-year');
  const hidden = document.getElementById('inp-bdate');
  if (!daySel || !monthSel || !yearSel || !hidden) return;

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  
  for (let i = 1; i <= 31; i++) {
    const opt = document.createElement('option');
    opt.value = String(i).padStart(2, '0');
    opt.textContent = i;
    daySel.appendChild(opt);
  }

  months.forEach((m, i) => {
    const opt = document.createElement('option');
    opt.value = String(i + 1).padStart(2, '0');
    opt.textContent = m;
    monthSel.appendChild(opt);
  });

  const currentYear = new Date().getFullYear();
  for (let i = currentYear; i >= currentYear - 100; i--) {
    const opt = document.createElement('option');
    opt.value = i;
    opt.textContent = i;
    yearSel.appendChild(opt);
  }

  const updateHiddenDate = () => {
    const y = yearSel.value;
    const m = monthSel.value;
    const d = daySel.value;
    if (y && m && d) {
      hidden.value = `${y}-${m}-${d}`;
    } else {
      hidden.value = '';
    }
  };

  daySel.addEventListener('change', updateHiddenDate);
  monthSel.addEventListener('change', updateHiddenDate);
  yearSel.addEventListener('change', updateHiddenDate);
}

function populateTimeDropdowns() {
  const hrSel = document.getElementById('inp-btime-hr');
  const minSel = document.getElementById('inp-btime-min');
  const ampmSel = document.getElementById('inp-btime-ampm');
  const hidden = document.getElementById('inp-btime');
  if (!hrSel || !minSel || !ampmSel || !hidden) return;

  for (let i = 1; i <= 12; i++) {
    const opt = document.createElement('option');
    opt.value = String(i).padStart(2, '0');
    opt.textContent = opt.value;
    hrSel.appendChild(opt);
  }

  for (let i = 0; i <= 59; i++) {
    const opt = document.createElement('option');
    opt.value = String(i).padStart(2, '0');
    opt.textContent = opt.value;
    minSel.appendChild(opt);
  }

  const updateHiddenTime = () => {
    let h = hrSel.value;
    const m = minSel.value;
    const ampm = ampmSel.value;
    if (h && m && ampm) {
      let hrInt = parseInt(h, 10);
      if (ampm === 'PM' && hrInt !== 12) hrInt += 12;
      if (ampm === 'AM' && hrInt === 12) hrInt = 0;
      hidden.value = `${String(hrInt).padStart(2, '0')}:${m}`;
    } else {
      hidden.value = '';
    }
  };

  hrSel.addEventListener('change', updateHiddenTime);
  minSel.addEventListener('change', updateHiddenTime);
  ampmSel.addEventListener('change', updateHiddenTime);
}

function initAutocomplete() {
  const input = document.getElementById('inp-place');
  const dropdown = document.getElementById('place-dropdown');
  const latInput = document.getElementById('inp-place-lat');
  const lonInput = document.getElementById('inp-place-lon');
  let timeout = null;

  input.addEventListener('input', (e) => {
    latInput.value = '';
    lonInput.value = '';
    const val = e.target.value.trim();
    if (val.length < 2) {
      dropdown.classList.add('hidden');
      return;
    }

    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(async () => {
      try {
        const resp = await fetch(`${CONFIG.API_URL}/api/v1/places?q=${encodeURIComponent(val)}`);
        const places = await resp.json();
        
        if (places.length > 0) {
          dropdown.innerHTML = '';
          places.forEach(p => {
            const div = document.createElement('div');
            div.className = 'autocomplete-item';
            const stateText = p.state ? `<span class="ac-state">${p.state}</span>` : '';
            div.innerHTML = `${p.name}${stateText}`;
            div.addEventListener('click', () => {
              input.value = p.name + (p.state ? `, ${p.state}` : '');
              latInput.value = p.lat;
              lonInput.value = p.lon;
              dropdown.classList.add('hidden');
            });
            dropdown.appendChild(div);
          });
          dropdown.classList.remove('hidden');
        } else {
          dropdown.classList.add('hidden');
        }
      } catch (err) {
        console.error('Autocomplete error:', err);
      }
    }, 300);
  });

  document.addEventListener('click', (e) => {
    if (!input.contains(e.target) && !dropdown.contains(e.target)) {
      dropdown.classList.add('hidden');
    }
  });
}

function initHome() {
  populateDateDropdowns();
  populateTimeDropdowns();
  initAutocomplete();
  
  // Set activity date default to today
  const today = new Date();
  const todayStr = formatDateISO(today);
  const ainput = document.getElementById('inp-adate');
  ainput.value = todayStr;

  document.getElementById('home-form').addEventListener('submit', handleFormSubmit);
  document.getElementById('btn-save-profile').addEventListener('click', handleSaveProfile);
}

// ─── Profiles ───────────────────────────────────────────────────────────────
function renderProfiles() {
  const bar = document.getElementById('profiles-bar');
  if (!bar) return;
  
  const profiles = storage.getProfiles();
  const activeId = storage.getActiveProfileId();
  
  bar.innerHTML = '';
  
  // Add Profile button
  const addBtn = document.createElement('div');
  addBtn.className = 'profile-chip profile-chip--add';
  addBtn.innerHTML = '<span>+</span> Add Profile';
  addBtn.addEventListener('click', () => {
    storage.setActiveProfileId(null);
    clearFormInputs();
    renderProfiles();
  });
  bar.appendChild(addBtn);

  // Render profiles
  profiles.forEach(p => {
    const chip = document.createElement('div');
    chip.className = `profile-chip ${p.id === activeId ? 'active' : ''}`;
    chip.innerHTML = `<span>👤</span> ${p.name}`;
    chip.addEventListener('click', () => switchProfile(p.id));
    bar.appendChild(chip);
  });
}

function clearFormInputs() {
  document.getElementById('inp-place').value = '';
  document.getElementById('inp-place-lat').value = '';
  document.getElementById('inp-place-lon').value = '';
  document.getElementById('inp-bdate').value = '';
  document.getElementById('inp-btime').value = '';
  
  document.getElementById('inp-bdate-day').value = '';
  document.getElementById('inp-bdate-month').value = '';
  document.getElementById('inp-bdate-year').value = '';
  
  document.getElementById('inp-btime-hr').value = '';
  document.getElementById('inp-btime-min').value = '';
  document.getElementById('inp-btime-ampm').value = '';
}

function switchProfile(id) {
  const profiles = storage.getProfiles();
  const p = profiles.find(x => x.id === id);
  if (!p) return;
  
  storage.setActiveProfileId(id);
  populateFormFromData(p);
  renderProfiles();
}

function handleSaveProfile() {
  if (!validate()) return;
  
  const name = prompt("Enter a name for this profile (e.g. 'Me', 'Spouse', 'Rohan'):");
  if (!name || !name.trim()) return;
  
  const payload = {
    id: 'prof_' + Date.now(),
    name: name.trim(),
    birth_place: document.getElementById('inp-place').value.trim(),
    birth_date:  document.getElementById('inp-bdate').value,
    birth_time:  document.getElementById('inp-btime').value,
    lat: parseFloat(document.getElementById('inp-place-lat').value),
    lon: parseFloat(document.getElementById('inp-place-lon').value)
  };
  
  const profiles = storage.getProfiles();
  profiles.push(payload);
  storage.saveProfiles(profiles);
  storage.setActiveProfileId(payload.id);
  
  renderProfiles();
}

function populateFormFromData(data) {
  if (!data) return;
  document.getElementById('inp-place').value = data.birth_place || '';
  if (data.lat && data.lon) {
    document.getElementById('inp-place-lat').value = data.lat;
    document.getElementById('inp-place-lon').value = data.lon;
  }
  
  if (data.birth_date) {
    document.getElementById('inp-bdate').value = data.birth_date;
    const parts = data.birth_date.split('-');
    if (parts.length === 3) {
      document.getElementById('inp-bdate-year').value = parts[0];
      document.getElementById('inp-bdate-month').value = parts[1];
      document.getElementById('inp-bdate-day').value = parts[2];
    }
  }
  
  if (data.birth_time) {
    document.getElementById('inp-btime').value = data.birth_time;
    const parts = data.birth_time.split(':');
    if (parts.length === 2) {
      let h = parseInt(parts[0], 10);
      let ampm = 'AM';
      if (h >= 12) {
        ampm = 'PM';
        if (h > 12) h -= 12;
      } else if (h === 0) {
        h = 12;
      }
      document.getElementById('inp-btime-hr').value = String(h).padStart(2, '0');
      document.getElementById('inp-btime-min').value = parts[1];
      document.getElementById('inp-btime-ampm').value = ampm;
    }
  }
}

function hydrateSavedData() {
  renderProfiles();
  const profiles = storage.getProfiles();
  const activeId = storage.getActiveProfileId();
  
  if (activeId && profiles.some(p => p.id === activeId)) {
    switchProfile(activeId);
  } else {
    // Attempt to load transient data or legacy data
    const saved = storage.loadTransient();
    if (saved) {
      // Migrate legacy to "Me" profile if no profiles exist
      if (profiles.length === 0) {
         const p = { id: 'prof_' + Date.now(), name: 'Me', ...saved };
         storage.saveProfiles([p]);
         switchProfile(p.id);
      } else {
         populateFormFromData(saved);
      }
    }
  }
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
  const lat = document.getElementById('inp-place-lat').value;
  const bdate = document.getElementById('inp-bdate').value;
  const btime = document.getElementById('inp-btime').value;
  const adate = document.getElementById('inp-adate').value;

  if (!place) { showError('place', 'Please enter a birth place'); ok = false; }
  else if (!lat) { showError('place', 'Please select a place from the dropdown'); ok = false; }
  if (!bdate) { showError('bdate', 'Please select birth date'); ok = false; }
  if (!btime) { showError('btime', 'Please select birth time'); ok = false; }
  if (!adate) { showError('adate', 'Please select activity date'); ok = false; }
  
  if (bdate && adate) {
    if (new Date(adate) < new Date(bdate)) {
      showError('adate', 'Activity date cannot be before birth date');
      ok = false;
    }
  }
  
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
    lat: parseFloat(document.getElementById('inp-place-lat').value),
    lon: parseFloat(document.getElementById('inp-place-lon').value)
  };

  // Save birth details transiently
  storage.saveTransient({
    birth_place: payload.birth_place,
    birth_date:  payload.birth_date,
    birth_time:  payload.birth_time,
    lat: payload.lat,
    lon: payload.lon
  });

  // Navigate to loading
  goTo('loading');
  startLoadingMessages();

  try {
    // Artificial delay to allow loading animation to play (min 3 seconds)
    const [result] = await Promise.all([
      api.recommend(payload),
      new Promise(res => setTimeout(res, 3000))
    ]);
    
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
