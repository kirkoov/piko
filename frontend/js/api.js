import { API_PREFIX } from './config.js';

export function api(path) {
  return `${API_PREFIX}${path}`;
}
