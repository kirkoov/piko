import { describe, it, expect, vi } from 'vitest';

import fs from 'fs';

global.translations = {
  fi: {},
  en: {},
};

import { renderShifts, initApp } from '../../app.js';

const html = fs.readFileSync('./index.html', 'utf8');

const t_data = {
  period_start: '2026-06-01',
  period_end: '2026-06-30',
  shifts: [
    {
      id: 123,
      date: '2026-06-19',
      planned: '08:00-16:00',
      actual: '08:05-16:10',
      planned_minutes: 480,
      actual_minutes: 485,
      delta_minutes: 5,
      morning_bonus: 0,
      evening_bonus: 0,
      latest_child_name: 'Matti',
      latest_child_time: '15:30',
      note: 'Late bus',
      recommended_shift: '07:30-15:30',
    },
  ],
};

const shift = t_data.shifts[0];

describe('renderShifts', () => {
  it('opens editor when edit button is clicked', () => {
    document.documentElement.innerHTML = html;

    renderShifts([
      {
        ...t_data.shifts[0],
        period_start: t_data.period_start,
        period_end: t_data.period_end,
      },
    ]);

    document.querySelector('.edit-btn').click();

    expect(document.getElementById('modal').style.display).toBe('block');
    expect(document.getElementById('m_date').value).toBe(shift.date);
    expect(document.getElementById('m_planned').value).toBe(shift.planned);
    expect(document.getElementById('m_actual').value).toBe(shift.actual);
    expect(document.getElementById('m_latest_child_name').value).toBe(
      shift.latest_child_name
    );
    expect(document.getElementById('m_latest_child_time').value).toBe(
      shift.latest_child_time
    );
    expect(document.getElementById('m_note').value).toBe(shift.note);

    expect(document.getElementById('shifts').textContent).toContain(
      shift.latest_child_name
    );
    expect(document.getElementById('shifts').textContent).toContain(shift.note);

    expect(document.getElementById('shifts').textContent).toContain(
      shift.recommended_shift
    );
  });
});

describe('Add Shift workflow', () => {
  it('opens empty modal when Add Shift is clicked', () => {
    document.documentElement.innerHTML = html;

    // Pretend previous edit left values in fields
    document.getElementById('m_date').value = shift.date;
    document.getElementById('m_planned').value = shift.planned;
    document.getElementById('m_actual').value = shift.actual;
    document.getElementById('m_latest_child_name').value =
      shift.latest_child_name;
    document.getElementById('m_latest_child_time').value =
      shift.latest_child_time;
    document.getElementById('m_note').value = shift.note;
  });
});

describe('initApp current period', () => {
  it('loads current period and balance', async () => {
    document.documentElement.innerHTML = html;

    localStorage.setItem('user_id', '2');
    localStorage.setItem('user_name', 'Lora');
    localStorage.setItem('is_admin', 'false');
    localStorage.setItem('access_token', 'test-token');
    localStorage.setItem('language', 'en');

    global.fetch = vi.fn((url) => {
      if (url.includes('/balance')) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              balance_minutes: 15,
            }),
        });
      }

      if (url.includes('/periods/current')) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              period_start: '2026-06-01',
              period_end: '2026-06-14',
              shifts: [],
            }),
        });
      }

      return Promise.reject(new Error(`Unexpected URL: ${url}`));
    });

    globalThis.__periodElement = document.getElementById('period');

    await initApp();

    await Promise.resolve();
    await Promise.resolve();

    const el = document.getElementById('period');

    expect(document.getElementById('period').textContent).not.toBe('');
    expect(document.getElementById('balance').textContent).not.toBe('');
  });
});
