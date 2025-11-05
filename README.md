
## Setup (local)
1. Copy `.env.example` to `.env` and fill `OPENAI_API_KEY`.
2. Create a virtualenv and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Run FastAPI:
   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
4. Start UI (separate terminal):
   ```bash
   python -m app.ui.nicegui_app
   ```

## Tests
- Place a small `sample.pdf` at `tests/data/sample.pdf`.
- Run tests:
  ```bash
  pytest -q
  ```

