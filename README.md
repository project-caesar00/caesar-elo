# Caesar ELO - Website Rating System

A service for rating websites scraped from Google Maps using an ELO rating system. Users are presented with two random websites and choose the better design, dynamically updating ratings.

## Features

- 🎯 **ELO-based rating**: Compare two websites side-by-side and pick the winner
- 📊 **Leaderboard**: View websites ranked by their ELO score
- 🗺️ **GMaps Integration**: Scrape websites from local Google Maps results
- 🖼️ **Screenshot previews**: Visual comparison of website designs

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy, SQLite
- **Frontend**: React, Vite, TypeScript

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

API available at http://localhost:8000 (docs at /docs)

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

App available at http://localhost:5173

## Project Structure

```
caesar-elo/
├── backend/
│   ├── api/           # API routes
│   ├── main.py        # FastAPI app entry
│   ├── models.py      # SQLAlchemy models
│   ├── schemas.py     # Pydantic schemas
│   └── database.py    # DB configuration
├── frontend/
│   └── src/
│       ├── components/  # React components
│       ├── pages/       # Page views
│       └── api/         # API client
└── README.md
```

## Development

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/websites` | List all websites |
| GET | `/api/compare` | Get two random websites to compare |
| POST | `/api/compare` | Submit comparison result |
| GET | `/api/leaderboard` | Get ranked websites |

## License

MIT
