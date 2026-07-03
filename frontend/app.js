// const VER = "0.1";
import { isValidTime, isValidShift, shiftEndAfterStart } from './utils.js';
import { api } from './js/api.js';

let lang = localStorage.getItem('language') || 'en';

let currentShiftId = null;
let currentUser = null;

let pendingDelete = null;
let showAllShifts = false;
let expandedPeriods = {};

function authHeaders() {
  const token = localStorage.getItem('access_token');

  return {
    Authorization: `Bearer ${token}`,
  };
}

function t(key) {
  return translations[lang]?.[key] ?? translations.en?.[key] ?? key;
}

function htmlEscape(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function applyTranslations() {
  document.title = t('appTitle');
  // Text nodes
  document.querySelectorAll('[data-i18n]').forEach((el) => {
    el.textContent = t(el.dataset.i18n);
  });

  // Placeholders
  document.querySelectorAll('[data-i18n-placeholder]').forEach((el) => {
    el.placeholder = t(el.dataset.i18nPlaceholder);
  });
}

function askDelete(id) {
  pendingDelete = id;
  refreshShifts();
}

async function loadAllShifts() {
  // const response = await fetch(`/periods?user_id=${currentUser.id}`);
  const response = await fetch('/periods', {
    headers: authHeaders(),
  });
  const periods = await response.json();
  renderPeriods(periods);
}

async function loadBalance() {
  const balanceRes = await fetch(api('/balance'), {
    headers: authHeaders(),
  });

  const balance = await balanceRes.json();

  const minutes = balance.balance_minutes;
  const sign = minutes > 0 ? '+' : '';

  const hours = Math.floor(Math.abs(minutes) / 60);
  const mins = Math.abs(minutes) % 60;

  let balanceClass = 'balance-neutral';

  if (minutes > 0) balanceClass = 'balance-positive';
  else if (minutes < 0) balanceClass = 'balance-negative';

  document.getElementById('balance').innerHTML =
    `<div class="balance-card ${balanceClass}">
        ${sign}${minutes} ${t('min')} (${hours}${t('h')} ${mins}${t('m')})
     </div>`;
}

async function loadCurrentPeriod() {
  const shiftsRes = await fetch(api('/periods/current'), {
    headers: authHeaders(),
  });
  document.getElementById('period-title').textContent =
    `${t('currentPeriod')} - ${currentUser.name}`;

  const periodData = await shiftsRes.json();

  document.getElementById('period').textContent =
    `${formatDate(periodData.period_start)} - ${formatDate(periodData.period_end)}`;

  const el = document.getElementById('period');

  const shifts = periodData.shifts;
  renderShifts(shifts);
}

function bindShiftButtons() {
  document.querySelectorAll('.edit-btn').forEach((el) => {
    el.addEventListener('click', () => {
      openEditor(
        Number(el.dataset.id),
        el.dataset.date,
        el.dataset.planned,
        el.dataset.actual,
        el.dataset.childName,
        el.dataset.childTime,
        el.dataset.note
      );
    });
  });

  document.querySelectorAll('.ask-delete-btn').forEach((el) => {
    el.addEventListener('click', () => askDelete(Number(el.dataset.id)));
  });

  document.querySelectorAll('.delete-btn').forEach((el) => {
    el.addEventListener('click', () => deleteShift(Number(el.dataset.id)));
  });
}

function renderShifts(shifts) {
  let previousPeriod = '';
  document.getElementById('shifts').innerHTML = shifts
    .map((s) => {
      const periodKey = `${s.period_start}-${s.period_end}`;
      let header = '';
      if (showAllShifts && periodKey !== previousPeriod) {
        header = `
              <h3>${t('period')}:
                  ${formatDate(s.period_start)}
                  -
                  ${formatDate(s.period_end)}
              </h3>
          `;
        previousPeriod = periodKey;
      }

      const deltaClass =
        s.delta_minutes > 0
          ? 'delta-positive'
          : s.delta_minutes < 0
            ? 'delta-negative'
            : 'delta-neutral';

      return `
            ${header}
            <div class="shift-card">
                <b>${formatDate(s.date)}</b>

                <p>
                    ${t('planned')}:
                    ${s.planned}
                    (${minutesToText(s.planned_minutes)})
                </p>

                <p>
                    ${t('actual')}:
                    ${s.actual}
                    (${minutesToText(s.actual_minutes)})
                </p>

                ${
                  s.latest_child_name
                    ? `<p>${t('latestChild')}: ${htmlEscape(s.latest_child_name)} (${t('childLeaves')} ${s.latest_child_time})</p>`
                    : ''
                }

                ${s.note ? `<p><i>${htmlEscape(s.note)}</i></p>` : ''}

                ${
                  s.recommended_shift
                    ? `<p>${t('suggestedShift')}: ${htmlEscape(s.recommended_shift)}</p>`
                    : ''
                }

                <p class="${deltaClass}">
                    Δ ${formatDelta(s.delta_minutes)}
                </p>

                ${
                  s.morning_bonus > 0
                    ? `<p>${t('morningBonus')}: +${s.morning_bonus} ${t('min')}</p>`
                    : ''
                }

                ${
                  s.evening_bonus > 0
                    ? `<p>${t('eveningBonus')}: +${s.evening_bonus} ${t('min')}</p>`
                    : ''
                }
            <button
              class="edit-btn"
              data-id="${s.id}"
              data-date="${s.date}"
              data-planned="${s.planned}"
              data-actual="${s.actual}"
              data-child-name="${htmlEscape(s.latest_child_name)}"
              data-child-time="${s.latest_child_time}"
              data-note="${htmlEscape(s.note)}"
            >
              ${t('edit')}
            </button>
        ${
          pendingDelete === s.id
            ? `<button class="delete-btn" data-id="${s.id}">${t('reallyDelete')}</button>`
            : `<button class="ask-delete-btn" data-id="${s.id}">${t('delete')}</button>`
        }

            </div>
        `;
    })
    .join('');

  bindShiftButtons();
}

function renderPeriods(periods) {
  document.getElementById('shifts').innerHTML = periods
    .map((p) => {
      const key = `${p.period_start}-${p.period_end}`;
      const expanded = expandedPeriods[key];
      const arrowClass = expanded ? 'expanded' : '';

      return `
        <div class="shift-card">

          <div class="period-header" data-period-key="${key}">
            <h3>
              <span class="period-arrow ${arrowClass}">▶</span>
              ${formatDate(p.period_start)}
              -
              ${formatDate(p.period_end)}
          </h3>

            <p>
              ${t('showAllShiftsBalance')}:
              ${formatDelta(p.balance_minutes)}
            </p>

            <p>
              ${t('showAllShiftsBalanceShifts')}: ${p.shift_count}
            </p>

          </div>

          ${
            expanded
              ? p.shifts
                  .map(
                    (s) => `
                    <div class="shift-subcard">
                    <b>${formatDate(s.date)}</b>
                    <p>${s.actual}</p>

                    <button
                      class="edit-btn"
                      data-id="${s.id}"
                      data-date="${s.date}"
                      data-planned="${s.planned}"
                      data-actual="${s.actual}"
                      data-child-name="${htmlEscape(s.latest_child_name)}"
                      data-child-time="${s.latest_child_time}"
                      data-note="${htmlEscape(s.note)}"
                    >
                      ${t('edit')}
                    </button>

                    ${
                      pendingDelete === s.id
                        ? `<button class="delete-btn" data-id="${s.id}">${t('reallyDelete')}</button>`
                        : `<button class="ask-delete-btn" data-id="${s.id}">${t('delete')}</button>`
                    }
                  </div>
                  `
                  )
                  .join('')
              : ''
          }
        </div>
      `;
    })
    .join('');

  bindShiftButtons();

  document.querySelectorAll('.period-header').forEach((el) => {
    el.addEventListener('click', () => togglePeriod(el.dataset.periodKey));
  });
}

async function togglePeriod(periodKey) {
  expandedPeriods[periodKey] = !expandedPeriods[periodKey];
  await loadAllShifts();
}

async function deleteShift(id) {
  // const response = await fetch(`/shifts/${id}`, {
  //   method: 'DELETE',
  // });
  const response = await fetch(`/shifts/${id}`, {
    method: 'DELETE',
    headers: authHeaders(),
  });

  if (!response.ok) {
    const err = await response.json();
    alert(err.detail);
    return;
  }

  pendingDelete = null;

  await refreshShifts();
}

function openEditor(id, date, planned, actual, childName, childTime, note) {
  currentShiftId = id;
  document.getElementById('modal').style.display = 'block';
  document.getElementById('modal_title').textContent = t('editShift');
  document.getElementById('m_date').disabled = true;
  document.getElementById('m_date').value = date;
  document.getElementById('m_planned').value = planned;
  document.getElementById('m_actual').value = actual;
  document.getElementById('m_latest_child_name').value = childName;
  document.getElementById('m_latest_child_time').value = childTime;
  document.getElementById('m_note').value = note;
}

function closeModal() {
  currentShiftId = null;
  document.getElementById('modal').style.display = 'none';
}

function clearModal() {
  document.getElementById('m_date').disabled = false;
  document.getElementById('m_date').value = '';
  document.getElementById('m_planned').value = '';
  document.getElementById('m_actual').value = '';
  document.getElementById('m_latest_child_name').value = '';
  document.getElementById('m_latest_child_time').value = '';
  document.getElementById('m_note').value = '';
}

function validateShiftForm() {
  const planned = document.getElementById('m_planned').value;
  const actual = document.getElementById('m_actual').value;
  const childTime = document.getElementById('m_latest_child_time').value;

  if (!isValidShift(planned)) {
    alert('Invalid planned shift');
    return false;
  }

  if (!isValidShift(actual)) {
    alert('Invalid actual shift');
    return false;
  }

  if (!isValidTime(childTime)) {
    alert('Invalid latest child time');
    return false;
  }

  if (!shiftEndAfterStart(planned)) {
    alert('Planned shift end must be after start');
    return false;
  }

  if (!shiftEndAfterStart(actual)) {
    alert('Actual shift end must be after start');
    return false;
  }

  return true;
}

async function saveShift() {
  if (!validateShiftForm()) return;

  if (currentShiftId === null) {
    await createShift();
  } else {
    await updateShift();
  }

  await refreshShifts();
}

async function createShift() {
  const date = document.getElementById('m_date').value;
  const planned = document.getElementById('m_planned').value;
  const actual = document.getElementById('m_actual').value;
  const childName = document.getElementById('m_latest_child_name').value;
  const childTime = document.getElementById('m_latest_child_time').value;
  const note = document.getElementById('m_note').value;
  const [pStart, pEnd] = planned.split('-');
  const [aStart, aEnd] = actual.split('-');

  const params = new URLSearchParams({
    date: date,
    planned_start: pStart,
    planned_end: pEnd,
    actual_start: aStart,
    actual_end: aEnd,
    latest_child_name: childName,
    latest_child_time: childTime,
    note: note,
  });

  // const response = await fetch(`/shifts?${params}`, {
  //   method: 'POST',
  // });
  const response = await fetch(`/shifts?${params}`, {
    method: 'POST',
    headers: authHeaders(),
  });

  if (!response.ok) {
    const err = await response.json();
    alert(err.detail || 'Create failed');
    return;
  }

  closeModal();
}

async function updateShift() {
  const planned = document.getElementById('m_planned').value;
  const actual = document.getElementById('m_actual').value;
  const childName = document.getElementById('m_latest_child_name').value;
  const childTime = document.getElementById('m_latest_child_time').value;
  const note = document.getElementById('m_note').value;

  const [pStart, pEnd] = planned.split('-');
  const [aStart, aEnd] = actual.split('-');

  const response = await fetch(`/shifts/${currentShiftId}`, {
    method: 'PUT',
    headers: {
      ...authHeaders(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      planned_start: pStart,
      planned_end: pEnd,
      actual_start: aStart,
      actual_end: aEnd,
      latest_child_name: childName,
      latest_child_time: childTime,
      note,
    }),
  });

  if (!response.ok) {
    const err = await response.json();
    alert(err.detail || 'Update failed');
    return;
  }

  closeModal();
}

function openAddShift() {
  currentShiftId = null;
  clearModal();
  document.getElementById('modal_title').textContent = t('addShift');
  document.getElementById('modal').style.display = 'block';
}

function formatDate(dateString) {
  const date = new Date(dateString);

  return date.toLocaleDateString(lang, {
    weekday: 'short',
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
}

function minutesToText(minutes) {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;

  return `${hours}${t('h')} ${mins}${t('m')}`;
}

function formatDelta(minutes) {
  const sign = minutes > 0 ? '+' : '';

  const hours = Math.floor(Math.abs(minutes) / 60);
  const mins = Math.abs(minutes) % 60;

  return `${sign}${hours}${t('h')} ${mins}${t('m')}`;
}

async function changeLanguage() {
  lang = document.getElementById('language').value;
  localStorage.setItem('language', lang);
  applyTranslations();
  await refreshShifts();
}

async function toggleShiftsView() {
  showAllShifts = !showAllShifts;
  const button = document.getElementById('toggle-shifts');
  if (showAllShifts) {
    button.textContent = `${t('showCurrentPeriod')}`;
    document.getElementById('period-title').textContent = `${t('allShifts')}`;
    await loadAllShifts();
  } else {
    button.textContent = `${t('showAllShifts')}`;
    document.getElementById('period-title').textContent =
      `${t('currentPeriod')}`;
    await loadCurrentPeriod();
  }
}

async function refreshShifts() {
  await loadBalance();

  if (showAllShifts) {
    await loadAllShifts();
  } else {
    await loadCurrentPeriod();
  }
}

async function initApp() {
  currentUser = loadCurrentUser();

  if (!currentUser) {
    window.location.href = '/login.html';
    return;
  }
  const savedLang = localStorage.getItem('language');

  if (savedLang) {
    lang = savedLang;
    document.getElementById('language').value = savedLang;
  }

  document
    .getElementById('language')
    .addEventListener('change', changeLanguage);

  document
    .getElementById('toggle-shifts')
    .addEventListener('click', toggleShiftsView);

  document
    .getElementById('add-shift-btn')
    .addEventListener('click', openAddShift);

  document.getElementById('save-btn').addEventListener('click', saveShift);

  document.getElementById('cancel-btn').addEventListener('click', closeModal);

  document.getElementById('logout-btn').addEventListener('click', logout);

  applyTranslations();
  await refreshShifts();
}

function loadCurrentUser() {
  const id = Number(localStorage.getItem('user_id'));

  if (!Number.isFinite(id) || id <= 0) {
    return null;
  }

  return {
    id,
    name: localStorage.getItem('user_name'),
    isAdmin: localStorage.getItem('is_admin') === 'true',
  };
}

async function logout() {
  const token = localStorage.getItem('access_token');

  await fetch(api('/auth/logout'), {
    method: 'POST',
    headers: authHeaders(),
  });

  localStorage.clear();
  window.location.href = '/login.html';
}

document.addEventListener('DOMContentLoaded', initApp);

export { renderShifts, initApp };
