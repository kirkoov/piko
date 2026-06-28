async function logout() {
  const token = localStorage.getItem("access_token");

  const response = await fetch("/logout", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  // Even if server fails, we clear local state
  localStorage.removeItem("access_token");
  localStorage.removeItem("user_id");
  localStorage.removeItem("user_name");
  localStorage.removeItem("is_admin");

  if (response.ok) {
    window.location.href = "/login.html";
  } else {
    alert("Logout failed on server, but local session cleared.");
    window.location.href = "/login.html";
  }
}

function initLogout() {
  document.getElementById("logout-btn").addEventListener("click", logout);
}

document.addEventListener("DOMContentLoaded", initLogout);

export { initLogout };