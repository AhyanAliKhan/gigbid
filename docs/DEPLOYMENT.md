# GigBid Deployment Guide: Vercel (Frontend) & Render (Backend)

This guide provides instructions for deploying GigBid into production with the **React/TypeScript Web Application deployed on Vercel** and the **FastAPI Multi-Agent Backend deployed on Render**.

---

## 1. Deploying the Frontend on Vercel

The frontend is fully configured with [`vercel.json`](../vercel.json) for zero-configuration, instant static single-page application (SPA) deployment.

### Method A: One-Click GitHub Import (Recommended)
1. Go to **[vercel.com/new](https://vercel.com/new)** and sign in with your GitHub account.
2. Select your repository: **`AhyanAliKhan/gigbid`**.
3. In the project setup screen:
   - **Framework Preset**: *Other* (or *Vite*)
   - **Root Directory**: `./` (or `apps/web`)
   - **Build Command**: Leave empty / Default
   - **Output Directory**: Leave empty / Default
4. Click **Deploy**.
5. Once deployed, Vercel will assign a live URL (e.g., `https://gigbid-web.vercel.app`).

### Method B: Deploying via Vercel CLI
```bash
# In your project root:
npx vercel

# Or specifically inside the web directory:
cd apps/web
npx vercel
```
Follow the interactive prompts to log in and select your personal Vercel team.

---

## 2. Deploying the Backend on Render

The backend is configured with [`render.yaml`](../render.yaml) for automated Blueprint deployment and a production [`Dockerfile`](../Dockerfile).

### Method A: Render Blueprint (1-Click Automated Setup)
1. Log in to your **[dashboard.render.com](https://dashboard.render.com)** account.
2. Click **New +** in the top right corner and select **Blueprint**.
3. Connect your GitHub repository **`AhyanAliKhan/gigbid`**.
4. Render will automatically detect [`render.yaml`](../render.yaml) and configure:
   - **Service Name**: `gigbid-backend`
   - **Runtime**: Python 3.11
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn apps.api.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/health`
5. Click **Apply**.
6. Render will build and deploy your service to a live URL (e.g., `https://gigbid-backend.onrender.com`).

### Method B: Manual Web Service Setup on Render
1. Go to **[dashboard.render.com](https://dashboard.render.com)** $\rightarrow$ **New +** $\rightarrow$ **Web Service**.
2. Connect your GitHub repo `AhyanAliKhan/gigbid`.
3. Fill in the following parameters:
   - **Name**: `gigbid-backend`
   - **Region**: Oregon (US West) or Frankfurt
   - **Branch**: `master`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn apps.api.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free
4. Under **Advanced** $\rightarrow$ **Health Check Path**, enter: `/health`.
5. Click **Create Web Service**.

---

## 3. Connecting Vercel Frontend to Render Backend

Once your Render backend is live:
1. Open your deployed Vercel web app in your browser (e.g., `https://gigbid-web.vercel.app`).
2. Click the endpoint badge in the top right header:
   ```text
   🌐 Render / Local: 8000
   ```
3. Enter your deployed Render backend URL:
   ```text
   https://gigbid-backend.onrender.com
   ```
4. Click **Test & Save Backend URL**.
5. Your Vercel frontend is now communicating directly with your live multi-agent backend on Render!
