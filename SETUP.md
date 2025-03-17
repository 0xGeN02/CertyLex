# Setup

## Full-Stack Setup

This project consists of a **Next.js full-stack** and a **Python FastAPI backend**. Follow the steps at [SETUP.md](./SETUP.md).

---

## Prerequisites

- **Node.js** (v18 or higher)
- **Python** (v3.9 or higher)
- **Poetry** (for Python dependency management)

---

## Frontend Setup (Next.js)

1. Navigate to the project directory:

   ```bash
   cd CertyLex
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Start the development server:

   ```bash
   npm run dev
   ```

   The frontend will be available at [http://localhost:3000](http://localhost:3000).

---

## Backend Setup (Python FastAPI)

1. Navigate to the backend directory:

   ```bash
   cd backend
   ```

2. Install dependencies using Poetry:

   ```bash
   poetry install
   ```

3. Start the backend server:

   ```bash
   poetry run uvicorn backend.api.main:app --reload --port 5328
   ```

   The backend will be available at [http://localhost:5328](http://localhost:5328).

---

## Combined Workflow

1. Start the backend server:

   ```bash
   poetry run uvicorn backend.api.main:app --reload --port 5328
   ```

2. Start the frontend server:

   ```bash
   npm run dev
   ```

3. Access the application at [http://localhost:3000](http://localhost:3000).

---

## Additional Commands

### Frontend

- **Build for production**:

  ```bash
  npm run build
  ```

- **Start production server**:

  ```bash
  npm start
  ```

### Backend

- **Run tests**:

  ```bash
  poetry run pytest
  ```

---

## Documentation

- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Poetry Documentation](https://python-poetry.org/docs/)
