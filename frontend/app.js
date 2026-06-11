const CURRENT_USER_ID = 1;
let lang = "fi";
let currentShiftId = null;
let pendingDelete = null;

const translations = {
  en: {
    refresh: "Refresh",
    balance: "Balance",
    shifts: "Shifts",
    addShift: "Add Shift",
    planned: "Planned",
    actual: "Actual",
    latestChild: "Latest child",
    edit: "Edit",
    delete: "Delete",
    reallyDelete: "Really delete?",
  },

  fi: {
    refresh: "Päivitä",
    balance: "Saldo",
    shifts: "Vuorot",
    addShift: "Lisää vuoro",
    planned: "Suunniteltu",
    actual: "Toteutunut",
    latestChild: "Viimeinen lapsi",
    edit: "Muokkaa",
    delete: "Poista",
    reallyDelete: "Poistetaanko?",
  },

  ru: {
    refresh: "Обновить",
    balance: "Баланс",
    shifts: "Смены",
    addShift: "Добавить смену",
    planned: "по плану",
    actual: "по факту",
    latestChild: "Последний ребёнок",
    edit: "Изменить",
    delete: "Удалить",
    reallyDelete: "Точно удалить?",
  },
};

function t(key) {
  return translations[lang][key];
}

function askDelete(id) {
  pendingDelete = id;
  loadData();
}

async function loadData() {
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
            ${sign}${minutes} min (${hours}h ${mins}m)
        </div>`;

  const shiftsRes = await fetch(`/shifts?user_id=${CURRENT_USER_ID}`);
  const shifts = await shiftsRes.json();

  document.getElementById("shifts").innerHTML = shifts
    .map((s) => {
      const deltaClass =
        s.delta_minutes > 0
          ? "delta-positive"
          : s.delta_minutes < 0
            ? "delta-negative"
            : "delta-neutral";

      return `
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
                <p class="${deltaClass}">
                    Δ ${formatDelta(s.delta_minutes)}
                </p>

                <button onclick="openEditor(
                    ${s.id},
                    '${s.planned}',
                    '${s.actual}',
                    '${s.latest_child_name}',
                    '${s.latest_child_time}'
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

async function editShift(id, planned, actual) {
  const newPlanned = prompt("Planned (HH:MM-HH:MM)", planned);
  if (!newPlanned) return;

  const newActual = prompt("Actual (HH:MM-HH:MM)", actual);
  if (!newActual) return;

  const [pStart, pEnd] = newPlanned.split("-");
  const [aStart, aEnd] = newActual.split("-");

  await fetch(`/shifts/${id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      planned_start: pStart,
      planned_end: pEnd,
      actual_start: aStart,
      actual_end: aEnd,
    }),
  });

  loadData();
}

async function deleteShift(id) {
  // if (!confirm("Delete this shift?")) return;

  await fetch(`/shifts/${id}`, {
    method: "DELETE",
  });
  pendingDelete = null;

  loadData();
}

function openEditor(id, planned, actual, childName, childTime) {
  currentShiftId = id;
  document.getElementById("modal").style.display = "block";
  document.getElementById("m_planned").value = planned;
  document.getElementById("m_actual").value = actual;
  document.getElementById("m_latest_child_name").value = childName;
  document.getElementById("m_latest_child_time").value = childTime;
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

  const [pStart, pEnd] = planned.split("-");
  const [aStart, aEnd] = actual.split("-");

  await fetch(`/shifts/${currentShiftId}`, {
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
    }),
  });

  closeModal();
  loadData();
}

function closeEditor() {
  currentShiftId = null;
  document.getElementById("editor").style.display = "none";
}

async function saveShift() {
  const planned = document.getElementById("e_planned").value;
  const actual = document.getElementById("e_actual").value;
  const latest_child_n = document.getElementById("e_latest_child_name").value;
  const latest_child_t = document.getElementById("e_latest_child_time").value;

  const [pStart, pEnd] = planned.split("-");
  const [aStart, aEnd] = actual.split("-");

  await fetch(`/shifts/${currentShiftId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      planned_start: pStart,
      planned_end: pEnd,
      actual_start: aStart,
      actual_end: aEnd,
      latest_child_name: latest_child_n,
      latest_child_time: latest_child_t,
    }),
  });

  closeEditor();
  loadData();
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

  if (!date || !planned || !actual || !childName || !childTime) {
    alert("Fill all fields");
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

  loadData();
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

  return `${hours}h ${mins}m`;
}

function formatDelta(minutes) {
  const sign = minutes > 0 ? "+" : "";

  const hours = Math.floor(Math.abs(minutes) / 60);
  const mins = Math.abs(minutes) % 60;

  return `${sign}${hours}h ${mins}m`;
}

function changeLanguage() {
  lang = document.getElementById("language").value;
  localStorage.setItem("language", lang);
  loadData();
}

document.addEventListener("DOMContentLoaded", () => {
  const savedLang = localStorage.getItem("language");

  if (savedLang) {
    lang = savedLang;
    document.getElementById("language").value = savedLang;
  }

  loadData();
});
