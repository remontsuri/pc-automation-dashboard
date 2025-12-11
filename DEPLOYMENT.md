# Deployment Guide - PC Automation Dashboard

## Local Development

### Option 1: Docker Compose (Recommended)

**Prerequisites:**
- Docker Desktop installed
- Git

**Steps:**
```bash
git clone https://github.com/remontsuri/pc-automation-dashboard.git
cd pc-automation-dashboard
docker-compose up --build
```

Access: http://localhost:3000

### Option 2: Manual Setup (Windows)

**Backend Setup:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend Setup (New Terminal):**
```bash
cd frontend
npm install
npm run dev
```

Access: http://localhost:3000

## Production Deployment

### Frontend: Deploy to Vercel

1. Fork repo: https://github.com/remontsuri/pc-automation-dashboard
2. Connect Vercel: https://vercel.com
3. Import project from GitHub
4. Set Root Directory: `frontend/`
5. Deploy!

### Backend: Deploy to Railway

1. Create Railway account: https://railway.app
2. New Project → GitHub Repo
3. Connect GitHub
4. Select this repository
5. Environment Variables:
   - `LOG_LEVEL=INFO`
   - `WORKERS=4`
6. Deploy!

## Environment Variables

**Backend (.env):**
```
LOG_LEVEL=INFO
WORKERS=4
DATABASE_URL=sqlite:///./app.db
```

**Frontend (.env):**
```
VITE_API_URL=https://your-railway-backend.up.railway.app/api
```

## Monitoring & CI/CD

- GitHub Actions automatically tests on push
- Passes: Linting + Build
- Auto-deploys to Vercel/Railway on main branch

## Troubleshooting

**Port already in use:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

**Docker issues:**
```bash
docker-compose down
docker system prune
docker-compose up --build
```

## Support

Issues? Email: clockerindo@yandex.ru
