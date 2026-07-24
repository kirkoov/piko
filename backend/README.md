# Piko

**Piko** is a lightweight workforce management application for daycare employees.

This package contains a ready-to-run local version for evaluation on Windows.

---

## System requirements

- Windows 10 or Windows 11
- Internet connection (first launch only)
- Python 3.10 or newer

---

## 1. Install Python

Download Python from the
[official Python website](https://www.python.org/downloads/).

### Important

During installation, enable: ☑ **Add Python to PATH**

---

## 2. Install uv

Open **PowerShell** and run:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After installation, close PowerShell and open it again.

Verify:

```powershell
uv --version
```

---

## 3. Extract the archive

Extract the ZIP file to any folder, for example:

```text
C:\Piko
```

---

## 4. Start the backend

Open **PowerShell**.

Change to the backend directory:

```powershell
cd C:\Piko\backend
```

Install the required Python packages:

```powershell
uv sync
```

Start the server:

```powershell
uv run uvicorn app.main:app
```

The backend will start at:

```text
http://127.0.0.1:8000
```

Leave this PowerShell window open.

---

## 5. Start the frontend

Open a **second PowerShell** window.

```powershell
cd C:\Piko\frontend
python -m http.server 8080
```

---

## 6. Open Piko

Open your browser and navigate to:

```text
http://localhost:8080/login.html
```

---

## Included sample database

This release already contains a pre-populated SQLite database.

No database initialization is required.

---

## Stopping Piko

Press **Ctrl+C** in each PowerShell window.

---

## Troubleshooting

### `python` is not recognised

Python is not installed or was not added to the system PATH.

Reinstall Python and enable:

- Enable **Add Python to PATH** during installation.

---

### `uv` is not recognised

Close PowerShell and open it again.

If necessary, reinstall uv using the command above.

---

### Backend does not start

Ensure that no other application is already using port **8000**.

---

## Thank you

Thank you for taking the time to test **Piko**.

Your feedback is highly appreciated.
