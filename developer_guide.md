# Caesar ELO - Developer Guide

## 🚀 Deployment Workflow
The project uses **GitHub Actions** for Continuous Deployment.
- **Push to `main`** → Automatically deploys to Production (Hetzner VPS).
- **Manual Restart:** If needed, SSH into VPS and run `docker compose up -d`.

---

## 💻 Connecting Local Dev to Production Data

Since we use **SQLite**, the database is a file on the server. You cannot connect to it directly via a database client from your local machine (like you could with PostgreSQL).

However, you can point your **local Frontend** to the **Production API**.

### For Frontend Developers
To work on the local UI using real production data:

1. Create a `.env.local` file in `frontend/`:
   ```bash
   VITE_API_URL=https://caesar-elo.duckdns.org
   ```
2. Run the frontend:
   ```bash
   npm run dev
   ```
3. Your local app (`http://localhost:5173`) will now fetch/grade websites from the live production database.

### For Backend Developers
You cannot safely write to the production SQLite file from your local machine.
- **Recommended:** Use a local SQLite database (created automatically on first run).
- **To Sync Data:** You can download the production DB for local testing (READ-ONLY recommended):
  ```bash
  scp root@pceasar.duckdns.org:/opt/caesar-elo/data/caesar_elo.db ./backend/data/
  ```
  *(Note: This overwrites your local DB)*

## 📂 Production & Logs
- **VPS IP:** `116.203.144.152`
- **Domain:** [https://caesar-elo.duckdns.org](https://caesar-elo.duckdns.org)
- **Check Logs:**
  ```bash
  ssh root@pceasar.duckdns.org "docker logs -f caesar-elo-backend"
  ```
