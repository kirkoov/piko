import { describe, it, expect } from 'vitest';
import fs from 'fs';

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
