import { describe, it, expect } from 'vitest';
import fs from 'fs';

global.translations = {
  fi: {},
  en: {},
};

import { renderShifts } from '../app.js';

const html = fs.readFileSync(
  './index.html',
  'utf8'
);

describe('renderShifts', () => {
  it('opens editor when edit button is clicked', () => {
    document.documentElement.innerHTML = html;

    renderShifts([
      {
        id: 123,
        date: '2026-06-19',
        planned: '08:00-16:00',
        actual: '08:05-16:10',
        planned_minutes: 480,
        actual_minutes: 485,
        latest_child_name: 'Matti',
        latest_child_time: '15:30',
        note: 'Late bus',
        delta_minutes: 5,
        morning_bonus: 0,
        evening_bonus: 0,
        period_start: '2026-06-01',
        period_end: '2026-06-30',
      },
    ]);

    document.querySelector('.edit-btn').click();

    expect(document.getElementById('modal').style.display).toBe('block');

    expect(document.getElementById('m_date').value).toBe('2026-06-19');

    expect(document.getElementById('m_planned').value).toBe('08:00-16:00');

    expect(document.getElementById('m_actual').value).toBe('08:05-16:10');

    expect(document.getElementById('m_latest_child_name').value).toBe('Matti');

    expect(document.getElementById('m_latest_child_time').value).toBe('15:30');

    expect(document.getElementById('m_note').value).toBe('Late bus');
  });
});
