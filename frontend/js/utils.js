import { DEFAULT_LANGUAGE } from './config.js';

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

export function formatDate(dateString, lang = DEFAULT_LANGUAGE) {
  const date = new Date(dateString);

  return date.toLocaleDateString(lang, {
    weekday: 'short',
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
}

export function htmlEscape(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
