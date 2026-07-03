import { vi, describe, it, expect } from 'vitest';
import fs from 'fs';

import { initLogin } from '../../login.js';
import { api } from '../../js/api.js';

const html = fs.readFileSync('./login.html', 'utf8');

describe('login page', () => {
  it('contains login controls', () => {
    document.documentElement.innerHTML = html;

    expect(document.getElementById('username')).not.toBeNull();

    expect(document.getElementById('password')).not.toBeNull();

    expect(document.getElementById('login-btn')).not.toBeNull();
  });
});

describe('login page', () => {
  it('contains login controls', () => {
    document.documentElement.innerHTML = html;

    expect(document.getElementById('username')).not.toBeNull();

    expect(document.getElementById('password')).not.toBeNull();

    expect(document.getElementById('login-btn')).not.toBeNull();
  });
});

describe('successful login', () => {
  it('stores authenticated user', async () => {
    document.documentElement.innerHTML = html;

    localStorage.clear();

    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            status: 'ok',
            access_token: 'test-token',
            token_type: 'Bearer',
            user_id: 5,
            name: 'alice',
            is_admin: false,
          }),
      })
    );

    initLogin();

    document.getElementById('username').value = 'alice';
    document.getElementById('password').value = 'secret';

    document.getElementById('login-btn').click();

    await Promise.resolve();
    await Promise.resolve();

    expect(localStorage.getItem('user_id')).toBe('5');
    expect(localStorage.getItem('user_name')).toBe('alice');
    expect(localStorage.getItem('is_admin')).toBe('false');
    expect(localStorage.getItem('access_token')).toBe('test-token');
  });
});
