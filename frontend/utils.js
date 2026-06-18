export function isValidTime(time) {
  return /^([01]\d|2[0-3]):([0-5]\d)$/.test(time);
}

export function isValidShift(shift) {
  return /^([01]\d|2[0-3]):([0-5]\d)-([01]\d|2[0-3]):([0-5]\d)$/.test(shift);
}

export function shiftEndAfterStart(shift) {
  const [start, end] = shift.split('-');

  const [sh, sm] = start.split(':').map(Number);
  const [eh, em] = end.split(':').map(Number);

  const startMin = sh * 60 + sm;
  const endMin = eh * 60 + em;

  return endMin > startMin;
}

export function minutesToText(minutes) {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;

  return `${hours}${t('h')} ${mins}${t('m')}`;
}

export function formatDelta(minutes) {
  const sign = minutes > 0 ? '+' : '';

  const hours = Math.floor(Math.abs(minutes) / 60);
  const mins = Math.abs(minutes) % 60;

  return `${sign}${hours}${t('h')} ${mins}${t('m')}`;
}
