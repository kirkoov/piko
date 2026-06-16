// const VER = "0.1";
const CURRENT_USER_ID = 1;
let lang = localStorage.getItem("language") || "fi";
let currentShiftId = null;
let pendingDelete = null;
const esc = (s) =>
  String(s)
    .replace(/\\/g, "\\\\")
    .replace(/'/g, "\\'")
    .replace(/\n/g, "\\n")
    .replace(/\r/g, "");
let showAllShifts = false;
let expandedPeriods = {};

const translations = {
  en: {
    appTitle: "KindaGrinda",
    save: "Save",
    cancel: "Cancel",
    min: "min",
    m: "m",
    h: "h",
    balance: "Balance",
    shifts: "Shifts",
    addShift: "Add Shift",
    planned: "Planned",
    plannedPhldr: "Planned (HH:MM-HH:MM)",
    actualPhldr: "Actual (HH:MM-HH:MM)",
    actual: "Actual",
    latestChild: "Latest child",
    latestChildNamePhldr: "Latest child name",
    edit: "Edit",
    delete: "Delete",
    reallyDelete: "Really delete?",
    morningBonus: "Morning bonus",
    eveningBonus: "Evening bonus",
    suggestedShift: "Suggested shift",
    currentPeriod: "Current period",
  },

  fi: {
    appTitle: "Päiko",
    save: "Save",
    cancel: "Cancel",
    min: "min",
    m: "m",
    h: "t",
    balance: "Saldo",
    shifts: "Vuorot",
    addShift: "Lisää vuoro",
    planned: "Suunniteltu",
    plannedPhldr: "Planned (TT:MM-TT:MM)",
    actualPhldr: "Actual (HH:MM-HH:MM)",
    actual: "Toteutunut",
    latestChild: "Viimeinen lapsi",
    latestChildNamePhldr: "Latest child name",
    edit: "Muokkaa",
    delete: "Poista",
    reallyDelete: "Poistetaanko?",
    morningBonus: "Aamulisä",
    eveningBonus: "Iltalisä",
    suggestedShift: "Ehdotettu vuoro",
    currentPeriod: "Current period",
  },

  ru: {
    appTitle: "ДетсАдик",
    save: "Сохранить",
    cancel: "Отмена",
    min: "мин",
    m: "м",
    h: "ч",
    balance: "Накапало",
    shifts: "Смены",
    addShift: "Добавить смену",
    planned: "по плану",
    plannedPhldr: "По плану (ч:м-ч:м)",
    actualPhldr: "По факту (ч:м-ч:м)",
    actual: "по факту",
    latestChild: "Последний ребёнок",
    latestChildNamePhldr: "Имя посл. ребёнка",
    edit: "Изменить",
    delete: "Удалить",
    reallyDelete: "Точно удалить?",
    morningBonus: "Капнуло за утро",
    eveningBonus: "Капнуло за вечер",
    suggestedShift: "Рекомендуемая смена",
    currentPeriod: "Отчетный период",
  },
};

function t(key) {
  return translations[lang][key];
}

function applyTranslations() {
  // Text nodes
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(el.dataset.i18n);
  });

  // Placeholders
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    el.placeholder = t(el.dataset.i18nPlaceholder);
  });
}

function askDelete(id) {
  pendingDelete = id;
  refreshShifts();
}

async function loadAllShifts() {
  const response = await fetch(`/periods?user_id=${CURRENT_USER_ID}`);
  const periods = await response.json();
  renderPeriods(periods);
}

async function loadCurrentPeriod() {
  const balanceRes = await fetch(`/balance?user_id=${CURRENT_USER_ID}`);
  const balance = await balanceRes.json();

  const minutes = balance.balance_minutes;
  const sign = minutes > 0 ? "+" : "";

  const hours = Math.floor(Math.abs(minutes) / 60);
  const mins = Math.abs(minutes) % 60;

  let balanceClass = "balance-neutral";

  if (minutes > 0) balanceClass = "balance-positive";
  else if (minutes < 0) balanceClass = "balance-negative";

  document.getElementById("balance").innerHTML =
    `<div class="balance-card ${balanceClass}">
            ${sign}${minutes} ${t("min")} (${hours}${t("h")} ${mins}${t("m")})
        </div>`;

  const shiftsRes = await fetch(`/current-period?user_id=${CURRENT_USER_ID}`);

  const periodData = await shiftsRes.json();
  document.getElementById("period").textContent =
    `${formatDate(periodData.period_start)} - ${formatDate(periodData.period_end)}`;
  const shifts = periodData.shifts;
  renderShifts(shifts);
}

function renderShifts(shifts) {
  let previousPeriod = "";
  document.getElementById("shifts").innerHTML = shifts
    .map((s) => {
      const periodKey = `${s.period_start}-${s.period_end}`;
      let header = "";
      if (showAllShifts && periodKey !== previousPeriod) {
        header = `
              <h3>Period:
                  ${formatDate(s.period_start)}
                  -
                  ${formatDate(s.period_end)}
              </h3>
          `;
        previousPeriod = periodKey;
      }

      const deltaClass =
        s.delta_minutes > 0
          ? "delta-positive"
          : s.delta_minutes < 0
            ? "delta-negative"
            : "delta-neutral";

      return `
            ${header}
            <div class="shift-card">
                <b>${formatDate(s.date)}</b>

                <p>
                    ${t("planned")}:
                    ${s.planned}
                    (${minutesToText(s.planned_minutes)})
                </p>

                <p>
                    ${t("actual")}:
                    ${s.actual}
                    (${minutesToText(s.actual_minutes)})
                </p>

                ${
                  s.latest_child_name
                    ? `<p>${t("latestChild")}: ${s.latest_child_name} (leaves ${s.latest_child_time})</p>`
                    : ""
                }

                ${s.note ? `<p><i>${s.note}</i></p>` : ""}

                ${
                  s.recommended_shift
                    ? `<p>${t("suggestedShift")}: ${s.recommended_shift}</p>`
                    : ""
                }

                <p class="${deltaClass}">
                    Δ ${formatDelta(s.delta_minutes)}
                </p>

                ${
                  s.morning_bonus > 0
                    ? `<p>${t("morningBonus")}: +${s.morning_bonus} ${t("min")}</p>`
                    : ""
                }

                ${
                  s.evening_bonus > 0
                    ? `<p>${t("eveningBonus")}: +${s.evening_bonus} ${t("min")}</p>`
                    : ""
                }

                <button onclick="openEditor(
                    ${s.id},
                    '${s.planned}',
                    '${s.actual}',
                    '${esc(s.latest_child_name)}',
                    '${s.latest_child_time}',
                    '${esc(s.note)}'
                )">
                ${t("edit")}
            </button>

        ${
          pendingDelete === s.id
            ? `<button onclick="deleteShift(${s.id})">${t("reallyDelete")}</button>`
            : `<button onclick="askDelete(${s.id})">${t("delete")}</button>`
        }

            </div>
        `;
    })
    .join("");
}

function renderPeriods(periods) {
  document.getElementById("shifts").innerHTML = periods
    .map((p) => {
      const key = `${p.period_start}-${p.period_end}`;
      const expanded = expandedPeriods[key];

      return `
        <div class="shift-card">

          <div onclick="togglePeriod('${key}')">

            <h3>
              ${formatDate(p.period_start)}
              -
              ${formatDate(p.period_end)}
            </h3>

            <p>
              Balance:
              ${formatDelta(p.balance_minutes)}
            </p>

            <p>
              Shifts: ${p.shift_count}
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
                    </div>
                  `,
                  )
                  .join("")
              : ""
          }

        </div>
      `;
    })
    .join("");
}

function togglePeriod(periodKey) {
  expandedPeriods[periodKey] = !expandedPeriods[periodKey];
  loadAllShifts();
}

async function deleteShift(id) {
  const response = await fetch(`/shifts/${id}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    const err = await response.json();
    alert(err.detail);
    return;
  }

  pendingDelete = null;

  await refreshShifts();
}

function openEditor(id, planned, actual, childName, childTime, note) {
  currentShiftId = id;
  document.getElementById("modal").style.display = "block";
  document.getElementById("m_planned").value = planned;
  document.getElementById("m_actual").value = actual;
  document.getElementById("m_latest_child_name").value = childName;
  document.getElementById("m_latest_child_time").value = childTime;
  document.getElementById("m_note").value = note;
}

function closeModal() {
  currentShiftId = null;
  document.getElementById("modal").style.display = "none";
}

async function saveModal() {
  const planned = document.getElementById("m_planned").value;
  const actual = document.getElementById("m_actual").value;
  const childName = document.getElementById("m_latest_child_name").value;
  const childTime = document.getElementById("m_latest_child_time").value;
  const note = document.getElementById("m_note").value;

  if (!isValidShift(planned)) {
    alert("Invalid planned shift");
    return;
  }

  if (!isValidShift(actual)) {
    alert("Invalid actual shift");
    return;
  }

  if (!isValidTime(childTime)) {
    alert("Invalid latest child time");
    return;
  }

  if (!shiftEndAfterStart(planned)) {
    alert("Planned shift end must be after start");
    return;
  }

  if (!shiftEndAfterStart(actual)) {
    alert("Actual shift end must be after start");
    return;
  }

  const [pStart, pEnd] = planned.split("-");
  const [aStart, aEnd] = actual.split("-");

  const response = await fetch(`/shifts/${currentShiftId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      planned_start: pStart,
      planned_end: pEnd,
      actual_start: aStart,
      actual_end: aEnd,
      latest_child_name: childName,
      latest_child_time: childTime,
      note: note,
    }),
  });

  if (!response.ok) {
    const err = await response.json();
    alert(err.detail);
    return;
  }

  closeModal();
  await refreshShifts();
}

async function addShift() {
  const date = document.getElementById("new_date").value.trim();
  const planned = document.getElementById("new_planned").value.trim();
  const actual = document.getElementById("new_actual").value.trim();
  const childName = document
    .getElementById("new_latest_child_name")
    .value.trim();
  const childTime = document
    .getElementById("new_latest_child_time")
    .value.trim();
  const note = document.getElementById("new_note").value.trim();

  if (!date || !planned || !actual || !childTime) {
    alert("All fields mandatory except child name");
    return;
  }

  if (!isValidShift(planned)) {
    alert("Invalid planned shift");
    return;
  }

  if (!isValidShift(actual)) {
    alert("Invalid actual shift");
    return;
  }

  if (!isValidTime(childTime)) {
    alert("Invalid latest child time");
    return;
  }

  if (!shiftEndAfterStart(planned)) {
    alert("Planned shift end must be after start");
    return;
  }

  if (!shiftEndAfterStart(actual)) {
    alert("Actual shift end must be after start");
    return;
  }

  const [pStart, pEnd] = planned.split("-");
  const [aStart, aEnd] = actual.split("-");

  const params = new URLSearchParams({
    user_id: CURRENT_USER_ID,
    date: date,
    planned_start: pStart,
    planned_end: pEnd,
    actual_start: aStart,
    actual_end: aEnd,
    latest_child_name: childName,
    latest_child_time: childTime,
    note: note,
  });

  const response = await fetch(`/shifts?${params}`, {
    method: "POST",
  });

  const result = await response.json();

  if (result.status === "error") {
    alert(result.message);
    return;
  }

  document.getElementById("new_date").value = "";
  document.getElementById("new_planned").value = "";
  document.getElementById("new_actual").value = "";
  document.getElementById("new_latest_child_name").value = "";
  document.getElementById("new_latest_child_time").value = "";
  document.getElementById("new_note").value = "";

  await refreshShifts();
}

function formatDate(dateString) {
  const date = new Date(dateString);

  return date.toLocaleDateString(lang, {
    weekday: "short",
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

function minutesToText(minutes) {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;

  return `${hours}${t("h")} ${mins}${t("m")}`;
}

function formatDelta(minutes) {
  const sign = minutes > 0 ? "+" : "";

  const hours = Math.floor(Math.abs(minutes) / 60);
  const mins = Math.abs(minutes) % 60;

  return `${sign}${hours}${t("h")} ${mins}${t("m")}`;
}

async function changeLanguage() {
  lang = document.getElementById("language").value;
  localStorage.setItem("language", lang);
  applyTranslations();
  await refreshShifts();
}

function isValidTime(time) {
  return /^([01]\d|2[0-3]):([0-5]\d)$/.test(time);
}

function isValidShift(shift) {
  return /^([01]\d|2[0-3]):([0-5]\d)-([01]\d|2[0-3]):([0-5]\d)$/.test(shift);
}

function shiftEndAfterStart(shift) {
  const [start, end] = shift.split("-");

  const [sh, sm] = start.split(":").map(Number);
  const [eh, em] = end.split(":").map(Number);

  const startMin = sh * 60 + sm;
  const endMin = eh * 60 + em;

  return endMin > startMin;
}

async function toggleShiftsView() {
  showAllShifts = !showAllShifts;
  const button = document.getElementById("toggle-shifts");
  if (showAllShifts) {
    button.textContent = "Current period";
    document.getElementById("period-title").textContent = "All shifts";
    await loadAllShifts();
  } else {
    button.textContent = "Show all shifts";
    document.getElementById("period-title").textContent = "Current period";
    await loadCurrentPeriod();
  }
}

async function refreshShifts() {
  if (showAllShifts) {
    await loadAllShifts();
  } else {
    await loadCurrentPeriod();
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const savedLang = localStorage.getItem("language");

  if (savedLang) {
    lang = savedLang;
    document.getElementById("language").value = savedLang;
  }

  applyTranslations();
  refreshShifts();
});
