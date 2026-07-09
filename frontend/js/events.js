export function registerEventHandlers({
  changeLanguage,
  toggleShiftsView,
  openAddShift,
  saveShift,
  closeModal,
  logout,
}) {
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
}
