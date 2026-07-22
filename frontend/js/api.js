import { API_PREFIX } from './config.js';

export function api(path) {
  return `${API_PREFIX}${path}`;
}

export function authHeaders() {
  const token = localStorage.getItem('access_token');

  return {
    Authorization: `Bearer ${token}`,
  };
}

export async function changeUserPassword(userId, password) {
  const response = await fetch(
    api(`/users/${userId}/password?password=${encodeURIComponent(password)}`),
    {
      method: 'PUT',
      headers: authHeaders(),
    }
  );

  if (!response.ok) {
    throw new Error(await response.text());
  }

  return response.json();
}
