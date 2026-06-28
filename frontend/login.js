async function login() {
  const username = document.getElementById('username').value;

  const password = document.getElementById('password').value;

  const response = await fetch(
    `/login?name=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`,
    {
      method: 'POST',
    }
  );

  const data = await response.json();

  if (response.ok) {
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('user_id', String(data.user_id));
    localStorage.setItem('user_name', data.name);
    localStorage.setItem('is_admin', String(data.is_admin));

    window.location.href = '/';
  }
}

function initLogin() {
  document.getElementById('login-btn').addEventListener('click', login);
}

document.addEventListener('DOMContentLoaded', initLogin);

export { initLogin };
