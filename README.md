# 🏥 Aarogya — AI-Powered Public Health Chatbot

> An intelligent public health assistant for rural India, accessible on **WhatsApp** and **Web Browser** — supporting Hindi, English, and Hinglish.

---

## 🌐 Live Demo

| Platform | Link |
|---|---|
| Website Chatbot | [health-chatbot-j7z1.onrender.com](https://health-chatbot-j7z1.onrender.com) |
| Admin Panel | [health-chatbot-j7z1.onrender.com/admin](https://health-chatbot-j7z1.onrender.com/admin) |

---

## 📌 Problem Statement

Rural India faces major public health challenges:
- Lack of awareness about diseases and prevention
- Misinformation spreading through communities
- Difficulty accessing doctors quickly
- Language barriers — people are more comfortable in Hindi
- No easy way to receive vaccination reminders

---

## 💡 Solution

**Aarogya** is an AI-powered chatbot that:
- Answers health-related questions in simple language
- Works on both **WhatsApp** and **web browser**
- Supports **Hindi, English, and Hinglish** automatically
- Sends **vaccination reminders** via WhatsApp
- Alerts users about **disease outbreaks**
- Handles **emergencies** — detects chest pain, breathing issues → responds with CALL 108 NOW

---

## ✨ Key Features

| Feature | Description |
|---|---|
| AI Health Chatbot | Powered by Groq AI (LLaMA 3.3 70B) |
| Multilingual | Hindi, English, Hinglish auto-detection |
| WhatsApp Integration | Sends and receives health messages via WhatsApp |
| Web Interface | Full screen chat UI accessible on any browser |
| Vaccination Reminders | Set date and time, auto sends WhatsApp reminder |
| Broadcast Alerts | Send health alerts to all users at once |
| Admin Dashboard | Manage users, reminders, alerts, web chats |
| Emergency Detection | Triggers CALL 108 NOW for critical symptoms |
| 24/7 Uptime | Deployed on Render, monitored by UptimeRobot |
| Cloud Database | MongoDB Atlas for user and reminder storage |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.13, Flask |
| AI Model | Groq API — LLaMA 3.3 70B Versatile |
| WhatsApp | Twilio WhatsApp API |
| Database | MongoDB Atlas |
| Translation | Google Translate API |
| Scheduler | APScheduler |
| Deployment | Render.com |
| Uptime Monitor | UptimeRobot |
| Frontend | HTML, CSS, Vanilla JavaScript |

---

## 🏗️ Project Structure
```
health-chatbot/
├── app.py                  # Main Flask application
├── Procfile                # Render deployment config
├── requirements.txt        # Python dependencies
├── .env                    # API keys (not on GitHub)
├── .gitignore              # Ignores .env and venv
└── templates/
    ├── chat.html           # Public chatbot website
    └── admin.html          # Admin dashboard
```

---

## ⚙️ How It Works
```
User (WhatsApp / Website)
        ↓
   Twilio / Browser
        ↓
   Flask Backend (app.py)
        ↓
   Google Translate (detect language)
        ↓
   Groq AI — LLaMA 3.3 (generate health response)
        ↓
   Translate back to user's language
        ↓
   Reply sent to user
```

---

## 🚀 Setup — Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/manish272736/health-chatbot.git
cd health-chatbot
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create .env file
```
GROQ_API_KEY=your_groq_api_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/healthchatbot
```

### 5. Run the app
```bash
python app.py
```

### 6. Open in browser
```
http://127.0.0.1:5000
```

---

## 🔐 Admin Panel

Access at `/admin` — password protected.

**Features:**
- View all registered users with join date
- Add vaccination reminders with date and time
- Delete pending reminders
- Send broadcast health alerts to all users
- View all web chat history

---

## 💬 Sample Conversations

**English:**
```
User:  I have fever and headache
Bot:   Fever with headache can be due to viral infection, dengue, or malaria.
       Drink plenty of water, rest, and take paracetamol if needed.
       If fever lasts more than 3 days, consult a doctor immediately.
```

**Hindi:**
```
User:  मुझे बुखार है
Bot:   बुखार के साथ यदि सिरदर्द, दस्त या उल्टी हो तो तुरंत डॉक्टर से मिलें।
       पर्याप्त पानी पीजिए और आराम करें।
```

**Emergency:**
```
User:  I have chest pain
Bot:   CALL 108 NOW
```

---

## 🔮 Future Improvements

- [ ] Add more regional languages (Bhojpuri, Tamil, Telugu)
- [ ] WhatsApp Business API for public deployment
- [ ] Location-based disease outbreak alerts
- [ ] User login and personal chat history
- [ ] Analytics dashboard with message trends
- [ ] Voice message support on WhatsApp

---

## 📄 License

This project is built for educational and social welfare purposes.
Feel free to fork and build upon it for public health initiatives.

---

> Built with the goal of making healthcare information accessible to every person in rural India — regardless of language, device, or internet speed.
