async function login() {
  const username = document.getElementById('username').value;

  const password = document.getElementById('password').value;

  await fetch(
    `/login?name=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`,
    {
      method: 'POST',
    }
  );
}

function initLogin() {
  document.getElementById('login-btn').addEventListener('click', login);
}

document.addEventListener('DOMContentLoaded', initLogin);

export { initLogin };
