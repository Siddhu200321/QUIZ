# QUIZ
Quiz Through Robot
Here's a **`README.md`** file you can include in your GitHub repository for this **AI-Powered Robot Quiz App using Pygame** project:

---

## 🤖 Robot Quiz Game using Pygame

An interactive, animated robot quiz game built using **Python, Pygame, pyttsx3 (Text-to-Speech)**, and **OpenTDB API**. The robot asks questions with voice, displays a timer, shows visual feedback, plays sounds, exports performance reports (CSV/PDF), and maintains a leaderboard.

---

### 🧠 Features

* 🎮 Full GUI-based quiz app with animated robot character
* 🔊 Questions spoken using `pyttsx3` (offline TTS)
* 📋 Fetches real-time questions from [OpenTDB](https://opentdb.com/)
* ⏱️ 30-second countdown timer bar per question
* ✅ Sound effects for correct/wrong answers
* 📊 Exports detailed quiz report as **CSV** and **PDF**
* 🏆 Leaderboard to track top scores
* 🗂️ Choose topic (Python/HTML/CSS/JS) and difficulty
* 🎨 Clean and intuitive Pygame interface

---

### 📦 Dependencies

Install these via pip:

```bash
pip install pygame pyttsx3 requests matplotlib reportlab
```

Also ensure your system supports `pyttsx3` voice engine (typically works offline on Windows/Mac/Linux).

---
### 🚀 How to Run

1. open vscode

2. Ensure you have Python 3.8+ installed.

3. Run the app:

```bash
python app.py
```

---

---

### 📈 Sample Output Reports

* **CSV Report**: `reports/username_timestamp.csv`
  Contains: Question, Your Answer, Correct Answer, Correct? Yes/No

* **PDF Report**: `reports/username_timestamp.pdf`
  Includes a score summary and a performance chart (bar graph of correct vs wrong answers)

---

### 🌐 Quiz Topics (via OpenTDB)

* `python` → Computers category
* `html`, `css`, `js` → Also mapped to Computers category
  *You can expand this by mapping new categories in the code's `CATEGORY` dictionary.*

---

### 🛠 Future Enhancements

* Speech recognition for voice-based answers
* Webcam-based emotion or gesture feedback
* Multiplayer support
* Add custom question database option

---

### 📜 License

MIT License – use it freely for learning, teaching, or extending!

---

### 🤝 Acknowledgements

* [OpenTDB](https://opentdb.com/) for trivia questions
* `pyttsx3` for offline TTS
* `pygame` for game GUI
* `reportlab` & `matplotlib` for report generation

