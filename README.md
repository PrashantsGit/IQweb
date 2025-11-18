# 🧠 IQ Test Platform  
### _A Django + AI powered cognitive testing and brain-training system_

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.0-darkgreen?logo=django)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon%20DB-blue?logo=postgresql)
![AI](https://img.shields.io/badge/AI-Gemini%201.5%20Flash-purple?logo=google)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Contributions Welcome](https://img.shields.io/badge/Contributions-Welcome-orange)

---

## 🚀 About the Project

This platform is a **complete cognitive testing ecosystem** featuring:

- Professional IQ tests  
- AI-generated personalized feedback  
- Gamified brain-training games  
- Modern glass UI  
- User dashboards & analytics  
- PDF certificates  
- Puzzle & Sudoku API integrations  

Built using **Django**, powered by **Gemini AI**, and enriched with real-time interactive games.

This isn’t just an IQ test — it’s a full cognitive evaluation + training suite.  

---

# 🎯 Key Features

## 🧪 IQ Test Engine
- 25 curated IQ questions  
- Numerical, logical, verbal, spatial reasoning  
- Timed test (auto-submit)  
- Difficulty-weighted scoring  
- Radar chart & category breakdown  
- Animated IQ gauge  

## 🤖 AI-Powered Personalized Report
Powered by **Google Gemini**:
- Strengths & weaknesses  
- IQ interpretation  
- Improvement roadmap  
- Cognitive skill analysis  
- Clean structured 180–250 word summary  

## 📄 Certificate Generator
- Auto PDF generation  
- Name, score, IQ, timestamp  
- Modern design  
- Ready for download  

## 🎮 Practice Mode — Brain Training
Currently includes:

### ✔ 🧩 Sudoku (API-based)
- Fetched live via **Sudoku API**  
- Fresh puzzle each time  

### ✔ 🧠 Memory Match Game
- Flip-card memory game  
- Timer, moves, score  
- Mobile friendly  

### ✔ 🧩 Logic Puzzle Game (PuzzleDB API)
- Live logic puzzles  
- Real-time answer checking  
- “New Puzzle” generator  

### Upcoming Games
- N-Back  
- Pattern Finder  
- Reaction Time Test  
- Word Recall  
- Stroop Test  

---

# 🧱 Architecture Overview

┌───────────────────────────┐
│ Frontend UI │
│ HTML • CSS • JS • Chart.js│
└───────────────┬───────────┘
│
┌───────────────▼──────────────┐
│ Django │
│ Views • Models • Templates │
└───────────────┬──────────────┘
│
┌──────────────▼────────────────┐
│ Business Logic Layer │
│ IQ Scoring • Stats • PDF gen │
└──────────────┬────────────────┘
│
┌──────────▼───────────┐
│ Gemini API │
│ AI Personalized Report│
└──────────┬───────────┘
│
┌─────────▼──────────┐
│ External APIs │
│ Sudoku API • PuzzleDB│
└─────────────────────┘

---

# 🛠 Tech Stack

## **Backend**
- Django 5  
- Python 3.10+  
- PostgreSQL (Neon DB)  
- Django ORM  
- ReportLab PDF generator  

## **AI**
- Google Gemini 1.5 Flash  
- Personalized IQ analysis  

## **Frontend**
- Bootstrap 5  
- Chart.js  
- Vanilla JS  
- Glassmorphism UI  

## **APIs Used**
| Feature       | API Used                            |
|---------------|--------------------------------------|
| Sudoku Game   | https://sudoku-api.vercel.app        |
| Puzzle Game   | https://api.puzzlehub.org            |
| AI Feedback   | Google Gemini API                    |

---

# ⚙️ Installation

## 1️⃣ Clone repository
```bash
git clone https://github.com/<your_repo>.git
cd <your_repo>

2️⃣ Create virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate      # Windows

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Set environment variables

Create .env:

GEMINI_API_KEY=your_api_key
DATABASE_URL=your_postgres_url
DEBUG=True

5️⃣ Run migrations
python manage.py migrate

6️⃣ Start dev server
python manage.py runserver

🤝 Contributing

Pull requests are welcome!
Please follow:

Fork the repo

Create a feature branch

Commit & push

Open a Pull Request

Issues & suggestions are appreciated.

👥 Contributors
👨‍💻 Prashant Chandra

GitHub: https://github.com/PrashantsGit

Email: rajprashant032@gmail.com

👨‍💻 Rishav Kumar

GitHub: https://github.com/rishavkr2002

Email: rishavkumar1971@gmail.com

👩‍💻 Pinnamaraju Sri Harshita

GitHub: https://github.com/pinnamarajusriharshita-hash

Email: pinnamarajusriharshita@gmail.com

⭐️ Support

If you like this project, please give the repository a star ⭐ on GitHub.