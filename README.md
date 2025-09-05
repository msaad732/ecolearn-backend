# EcoLearn AI 🌍

An AI-powered educational platform for kids and students to learn about **sustainability, recycling, and climate change** in a fun and an interactive way.
Built with a **FastAPI backend**, responsive **PWA frontend**, and features like quizzes, chat, and eco-friendly tips.

---

## ✨ Features

* **AI Chatbot** 🤖 – Ask eco-questions, get answers powered by Groq LLaMA-3.
* **Carbon Footprint Calculator** 🌱 – Get 3 personalized tips to reduce your footprint.
* **Quiz System** 📝 – Fun multiple-choice quizzes with leaderboard tracking.
* **Recycling Scanner** ♻️ – Upload an image, get recycling & DIY reuse tips.
* **Impact Share Card** 📸 – Generate shareable cards of your eco impact.
* **Leaderboard** 🏆 – Compete with friends and track quiz scores.
* **Progressive Web App** 📱 – Works offline, installable on phone/desktop.

---

## 🏗️ Project Structure

```
ecolearn-ai/
├── backend/
│   ├── main.py            # FastAPI backend (API routes, DB, AI integration)
│   ├── requirements.txt   # Python dependencies
│   └── leaderboard.db     # SQLite DB (auto-created)
├── frontend/
│   ├── index.html         # Landing page
│   ├── quiz.html          # Quiz interface
│   ├── carbon.html        # Carbon footprint calculator
│   ├── recycle.html       # Recycling scanner
│   ├── chat.html          # Chatbot
│   ├── share.html         # Share card page
│   ├── app.js             # Main frontend JS
│   ├── quiz.js / carbon.js / recycle.js / chat.js # Page-specific JS
│   ├── styles.css         # Unified styling
│   ├── manifest.json      # PWA manifest
│   └── sw.js              # Service Worker for offline support
├── assets/
│   └── icons/             # PWA icons (192x192, 512x512, etc.)
├── start.bat              # Quick local run script (Windows)
└── README.md              # Project docs
```

---

## 🚀 Quick Start

### 🔹 Backend (FastAPI)

1. Go to backend folder:

   ```bash
   cd backend
   ```

2. Create & activate virtual environment:

   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   source venv/bin/activate # macOS/Linux
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run backend:

   ```bash
   python main.py
   ```

   API will be live at: `http://localhost:8000`
   Docs: `http://localhost:8000/docs`

---

### 🔹 Frontend (PWA)

1. Go to frontend folder:

   ```bash
   cd frontend
   ```

2. Start local server:

   ```bash
   python -m http.server 8000
   ```

   Open: `http://localhost:8000`

✅ This allows service worker & manifest to work (double-clicking `index.html` will not).

---

## 🌐 API Endpoints

* `GET /` → Backend health check
* `POST /chat` → AI chat response
* `POST /stt` → Speech-to-text (Groq Whisper)
* `POST /carbon-footprint` → Calculate & get 3 tips
* `POST /recycle` → Classify recycle item & get AI suggestions
* `POST /quiz/start` → Generate quiz questions
* `POST /quiz/submit` → Submit quiz answers
* `GET /quiz/leaderboard` → Leaderboard

---

## 📱 PWA Features

* **Installable** – Add to Home Screen on mobile & desktop
* **Offline Support** – Service Worker caches pages
* **Responsive UI** – Works on all screen sizes
* **Eco Animations** – Smooth, fun design to engage kids

---

## 🚀 Deployment

### Backend

* **Render / Railway** – Deploy `backend/` with `requirements.txt`
* **Start Command**:

  ```bash
  uvicorn main:app --host 0.0.0.0 --port 10000
  ```

### Frontend

* **Netlify / Vercel / GitHub Pages** – Deploy `frontend/` as static site
* Must point API calls to your deployed backend URL

---

## 🌟 Roadmap

* [ ] Add user accounts & login
* [ ] Save quiz history per user
* [ ] Gamified eco-challenges
* [ ] Push notifications for tips
* [ ] Mobile app (React Native/Flutter)

---

## 📄 License

MIT License – Free to use & modify.

**Built with ❤️ for a sustainable future**
