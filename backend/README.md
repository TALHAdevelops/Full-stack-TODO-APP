# TaskFlow Backend (FastAPI)

Phase 2 implementation of the multi-user task management API.

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create `.env` file from `.env.example` and fill in the values.

4. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

## Testing

Access the health check at: http://localhost:8000/health
Interactive API docs: http://localhost:8000/docs
