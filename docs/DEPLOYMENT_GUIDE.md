# SignAI 2.0 — Production Cloud Deployment Guide
**Architecture:** Render (FastAPI + TensorFlow Backend) + Vercel (React 19 + Vite Frontend)

This guide provides step-by-step instructions to deploy SignAI 2.0 to cloud production on 100% free hosting tiers with continuous deployment (automatic updates whenever you push to GitHub).

---

## Architecture Overview

```
                                      ┌─────────────────────────────────────────┐
                                      │              Vercel Edge                │
                                      │        React 19 + Vite Frontend         │
                                      │   https://<your-app>.vercel.app        │
                                      └────────────────────┬────────────────────┘
                                                           │
                                                           │ HTTPS REST API
                                                           │ (multipart/form-data & JSON)
                                                           ▼
                                      ┌─────────────────────────────────────────┐
                                      │             Render.com                  │
                                      │       FastAPI + TensorFlow Backend      │
                                      │    https://<your-backend>.onrender.com  │
                                      └─────────────────────────────────────────┘
```

---

## Part 1: Deploying the Backend on Render.com (Free)

Render provides a free web service tier with Python 3.11 and Docker support.

### Option A: Using Render Blueprint (1-Click Automated)
The repository includes a pre-configured [`render.yaml`](../render.yaml) file.

1. Go to [dashboard.render.com](https://dashboard.render.com/) and sign in with GitHub.
2. Click **New +** in the top navigation and select **Blueprint**.
3. Connect your GitHub repository: `Shauryaaaa07/Sign-Language-Alphabet-Recognition`.
4. Render will read `render.yaml` automatically and display:
   - **Service Name:** `signai-backend`
   - **Environment:** `Python` (`3.11.10`)
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path:** `/health`
5. Click **Apply**.
6. Wait 2–3 minutes for the build to complete.
7. Once deployed, copy your backend URL:
   `https://signai-backend-xxxx.onrender.com`

---

### Option B: Manual Web Service Setup on Render
If you prefer configuring manually through the Render dashboard:

1. In Render Dashboard, click **New +** -> **Web Service**.
2. Select **Build and deploy from a Git repository** and pick `Shauryaaaa07/Sign-Language-Alphabet-Recognition`.
3. Fill in the fields:
   - **Name:** `signai-backend`
   - **Region:** Any close region (e.g. `Singapore` or `Oregon`)
   - **Branch:** `main`
   - **Root Directory:** *(leave blank — repository root)*
   - **Runtime:** `Python`
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** `Free`
4. Expand **Environment Variables** and add:
   - `PYTHON_VERSION` = `3.11.10`
   - `CORS_ORIGINS` = `*`
5. Click **Create Web Service**.

### Verify Backend Deployment
Open your browser and navigate to:
```
https://<your-backend-name>.onrender.com/health
```
You should see:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_name": "isl_alphabet_cnn_v4_best.keras",
  "num_classes": 26,
  "classes": ["A","B","C", ... ,"Z"]
}
```
Interactive Swagger API documentation is available at:
```
https://<your-backend-name>.onrender.com/docs
```

> [!NOTE]
> On Render's Free tier, services spin down after 15 minutes of inactivity. When a new request arrives, it takes ~30–50 seconds to wake up (cold start). Once warm, responses take ~50–80ms.

---

## Part 2: Deploying the Frontend on Vercel (Free)

Vercel provides ultra-fast global CDN hosting for Vite React applications.

### Step-by-Step Vercel Deployment

1. Go to [vercel.com](https://vercel.com/) and sign in with GitHub.
2. On your Vercel dashboard, click **Add New...** -> **Project**.
3. Find your repository `Shauryaaaa07/Sign-Language-Alphabet-Recognition` and click **Import**.
4. In the **Configure Project** screen:
   - **Project Name:** `signai-frontend` (or any custom name)
   - **Framework Preset:** `Vite` *(auto-detected)*
   - **Root Directory:** Click **Edit** and choose `frontend` *(important!)*
   - **Build Command:** `npm run build` *(default)*
   - **Output Directory:** `dist` *(default)*
5. Expand the **Environment Variables** section and add:
   - **Key:** `VITE_API_URL`
   - **Value:** `https://<your-backend-name>.onrender.com` *(from Part 1, without trailing slash)*
6. Click **Deploy**.
7. Vercel will build and deploy the React application in ~30 seconds.
8. You will receive a production URL such as:
   `https://signai-frontend.vercel.app`

---

## Part 3: Post-Deployment Verification Checklist

Once both services are deployed, test the live system:

- [ ] **Open Frontend:** Navigate to your Vercel URL.
- [ ] **Backend Health Badge:** Ensure the connection indicator in the header says `Backend Connected`.
- [ ] **Studio Camera Mode:** Click `Studio` -> Allow Webcam -> Make an ISL hand sign -> Verify live landmark skeleton and predictions appear.
- [ ] **Studio Upload Mode:** Upload any hand gesture image -> Verify classification result and Grad-CAM explanation modal.
- [ ] **Practice Arena:** Practice target letters and confirm score/streak increments.
- [ ] **Model Lab:** Inspect model architectures, validation metrics, and fusion comparisons.
- [ ] **Text-to-Speech:** Assemble letters into a word and click `Speak` to test speech synthesis.

---

## Part 4: Updating the Deployed App (Continuous Deployment)

Both Render and Vercel are connected to your GitHub repository:
- Whenever you push changes to `main` branch:
  ```bash
  git add .
  git commit -m "feat: your new update"
  git push origin main
  ```
- **Vercel** automatically rebuilds and redeploys the frontend in ~25 seconds.
- **Render** automatically rebuilds and redeploys the backend in ~2 minutes.

---

## Part 5: Alternative Deployment (Docker Anywhere)

If you prefer deploying a single container to **Railway**, **Google Cloud Run**, or **DigitalOcean**:

```bash
# Build Docker image
docker build -t signai-backend:latest .

# Run locally on port 8000
docker run -p 8000:8000 -e CORS_ORIGINS="*" signai-backend:latest
```

The container includes system libraries for OpenCV/MediaPipe, TensorFlow 2.15, and the evaluated CNN V4 model weights.
