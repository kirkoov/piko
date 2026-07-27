# Piko

**Piko** is a lightweight workforce management application for daycare employees.

This package contains a ready-to-run local version for evaluation on Windows.

---

## System requirements

- Windows 10 or Windows 11
- Internet connection (required only during the initial setup)
- Python 3.10 or newer

---

## Install Python

Download and install Python from the
[official Python website](https://www.python.org/downloads/).

### Important

During installation, enable:

- **Add Python to PATH**

---

## Install uv (needs to be reviewed)

Open **PowerShell** and run:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After installation, close PowerShell and open it again.

Verify the installation:

```powershell
uv --version
```

---

## Extract the archive

Extract the ZIP archive to any folder, for example:

```text
C:\Piko
```

---

## Start the backend

Open **PowerShell**.

Change to the backend directory:

```powershell
cd C:\Piko\backend
```

Install the required Python packages:

```powershell
uv sync
```

Start the backend:

```powershell
uv run uvicorn app.main:app
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

Leave this PowerShell window open while using Piko.

---

## Open Piko

Open a second **PowerShell** window.

Change to the frontend directory:

```powershell
cd C:\Piko\frontend
```

Serve the application files:

```powershell
python -m http.server 8080
```

Open your web browser and navigate to:

```text
http://localhost:8080/login.html
```

---

## Sample database

This release already contains a pre-populated SQLite database.

No database initialization is required.

---

## Stop Piko

Press **Ctrl+C** in each PowerShell window.

---

## Troubleshooting

### `python` is not recognised

Python is either not installed or was not added to the system `PATH`.

Reinstall Python and ensure that **Add Python to PATH** is selected during installation.

### `uv` is not recognised

Close PowerShell, open it again, and run:

```powershell
uv --version
```

If the command is still not recognised, reinstall `uv` using the command shown above.

### The backend does not start

Ensure that no other application is already using port **8000**.

---

## Thank you

Thank you for taking the time to evaluate **Piko**.

Your feedback is greatly appreciated.
