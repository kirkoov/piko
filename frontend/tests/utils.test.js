import { isValidTime, isValidShift, shiftEndAfterStart } from '../utils.js';

import { describe, it, expect } from 'vitest';

describe('isValidTime', () => {
  it('accepts valid times', () => {
    expect(isValidTime('08:30')).toBe(true);
    expect(isValidTime('23:59')).toBe(true);
  });

  it('rejects invalid times', () => {
    expect(isValidTime('24:00')).toBe(false);
    expect(isValidTime('8:30')).toBe(false);
  });
});

describe('shiftEndAfterStart', () => {
  it('accepts normal shifts', () => {
    expect(shiftEndAfterStart('08:00-16:00')).toBe(true);
  });

  it('rejects backwards shifts', () => {
    expect(shiftEndAfterStart('16:00-08:00')).toBe(false);
  });
});
