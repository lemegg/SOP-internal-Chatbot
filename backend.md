# Backend Documentation

This project uses a FastAPI-based backend for the RAG chatbot.

## Prerequisites

- Python 3.11+
- Virtual environment (venv)
- `requirements.txt` installed

## Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/macOS: `source venv/bin/activate`

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Starting the Backend

The backend should be started from the **project root directory** to ensure paths and imports are correctly resolved.

### Using PowerShell (Windows)

Set the `PYTHONPATH` to include the `backend` directory and run `main.py`:

```powershell
$env:PYTHONPATH = "backend"
.\venv\Scripts\python.exe backend/app/main.py
```

### Using Command Prompt (Windows)

```cmd
set PYTHONPATH=backend
venv\Scripts\python.exe backend\app\main.py
```

### Using Bash (Linux/macOS)

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/backend
./venv/bin/python backend/app/main.py
```

## API Endpoints

- **Auth**: `/auth`
- **Chat**: `/api`
- **Analytics**: `/api/analytics`
- **Feedback**: `/api/feedback`
- **Admin**: `/api/admin`

The API is served at `http://localhost:8000` by default.
Documentation is available at `http://localhost:8000/docs`.

## Auto-Ingestion

Upon startup, the backend automatically checks if the FAISS index is present and synchronized with the documents in `backend/data/sops`. If missing or out-of-sync, it will perform auto-ingestion.
