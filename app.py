import os
import certifi
import traceback
from flask import Flask, request, render_template, jsonify, session, redirect
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from groq import Groq
from pymongo import MongoClient
from bson import ObjectId
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from dotenv import load_dotenv
from googletrans import Translator as GTranslator

load_dotenv()

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
app.secret_key = "aarogya_admin_secret_123"

print("Connecting to services...")

try:
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    print("Groq OK")
except Exception as e:
    print("Groq FAILED:", e)

try:
    twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
    print("Twilio OK")
except Exception as e:
    print("Twilio FAILED:", e)

try:
    mongo = MongoClient(
        os.getenv("MONGO_URI"),
        tlsCAFile=certifi.where()
    )
    db = mongo["healthchatbot"]
    db.command("ping")
    print("MongoDB OK")
except Exception as e:
    print("MongoDB FAILED:", e)

SYSTEM_PROMPT = """
You are Aarogya, a friendly public health assistant for rural India.

Your job:
- Answer health questions in simple language
- Explain disease symptoms and prevention
- Suggest when to see a doctor
- Give vaccination schedule information
- Warn about seasonal diseases

Rules:
- For WhatsApp keep replies under 100 words
- For website chat give detailed replies up to 200 words with proper explanation
- Never diagnose diseases yourself
- Always say consult a doctor for serious symptoms
- If user writes in Hindi, reply in Hindi
- For emergencies like chest pain, difficulty breathing,
  seizures, unconscious — immediately say: CALL 108 NOW

Diseases to know well for rural India:
Dengue, Malaria, TB, Cholera, Typhoid,
Diarrhea, Pneumonia, Polio, COVID, Anemia
"""

def ask_ai(user_message, max_tokens=300):
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print("Groq error:", e)
        return "Sorry, I could not process your request. Please try again."

def ask_ai_in_lang(user_message, language, max_tokens=300):
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT + f"\n\nIMPORTANT: Always reply in {language} only, regardless of what language the user wrote in."},
                {"role": "user",   "content": user_message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print("Groq error:", e)
        return "Sorry, I could not process your request. Please try again."

def to_english(text):
    try:
        t = GTranslator()
        lang = t.detect(text).lang
        if isinstance(lang, str) and lang != 'en':
            return t.translate(text, dest='en').text, lang
        return text, 'en'
    except:
        return text, 'en'

def to_original(text, lang):
    try:
        if lang != 'en':
            t = GTranslator()
            return t.translate(text, dest=lang).text
        return text
    except:
        return text

def format_phone(phone):
    phone = phone.strip().replace(" ", "").replace("-", "")
    if phone.startswith("0"):
        phone = "+91" + phone[1:]
    if not phone.startswith("+"):
        phone = "+91" + phone
    if not phone.startswith("whatsapp:"):
        phone = "whatsapp:" + phone
    return phone

# ── Public chatbot website ────────────────────────────────────────────
@app.route("/health")
def health():
    return "OK", 200

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data      = request.json
        message   = data.get("message", "").strip()
        lang_pref = data.get("lang", "auto")

        if not message:
            return jsonify({"reply": "Please type a message."})

        if lang_pref == "hi":
            english_msg, _ = to_english(message)
            reply = ask_ai_in_lang(english_msg + " (give detailed answer)", "Hindi", max_tokens=600)
        elif lang_pref == "en":
            english_msg, _ = to_english(message)
            reply = ask_ai_in_lang(english_msg + " (give detailed answer)", "English", max_tokens=600)
        else:
            reply = ask_ai(message + " (give detailed answer)", max_tokens=400)

        db.web_chats.insert_one({
            "message": message,
            "reply":   reply,
            "time":    datetime.now()
        })
        return jsonify({"reply": reply})

    except Exception as e:
        print("Chat error:", traceback.format_exc())
        return jsonify({"reply": "Something went wrong. Please try again."})

# ── Admin panel ───────────────────────────────────────────────────────
ADMIN_PASSWORD = "aarogya123"

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin")
        return render_template("admin.html", error="Wrong password", logged_in=False)
    if not session.get("admin"):
        return render_template("admin.html", logged_in=False, error=None)
    users     = list(db.users.find({}, {"_id": 0}))
    reminders = list(db.reminders.find({}).sort("date", 1))
    for r in reminders:
        r["id"] = str(r["_id"])
        del r["_id"]
    web_chats = list(db.web_chats.find({}, {"_id": 0}).sort("time", -1).limit(20))
    return render_template("admin.html",
        logged_in=True,
        users=users,
        reminders=reminders,
        web_chats=web_chats,
        user_count=len(users),
        reminder_count=len(reminders)
    )

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect("/admin")

@app.route("/admin/add-reminder", methods=["POST"])
def admin_add_reminder():
    if not session.get("admin"):
        return jsonify({"status": "unauthorized"}), 401
    data  = request.json
    phone = format_phone(data["phone"])
    db.reminders.insert_one({
        "phone":   phone,
        "date":    data["date"],
        "time":    data["time"],
        "message": data["message"],
        "sent":    False
    })
    return jsonify({"status": "added"})

@app.route("/admin/delete-reminder", methods=["POST"])
def admin_delete_reminder():
    if not session.get("admin"):
        return jsonify({"status": "unauthorized"}), 401
    data = request.json
    db.reminders.delete_one({"_id": ObjectId(data["id"])})
    return jsonify({"status": "deleted"})

@app.route("/admin/send-alert", methods=["POST"])
def admin_send_alert():
    if not session.get("admin"):
        return jsonify({"status": "unauthorized"}), 401
    data    = request.json
    message = data.get("message", "")
    users   = list(db.users.find({}, {"phone": 1}))
    sent    = 0
    for u in users:
        try:
            twilio_client.messages.create(
                from_="whatsapp:+14155238886",
                to=u["phone"],
                body="Health Alert from Aarogya: " + message
            )
            sent += 1
        except Exception as e:
            print("Alert send error:", e)
    db.alerts.insert_one({
        "message": message,
        "sent_to": sent,
        "time":    datetime.now()
    })
    return jsonify({"status": "sent", "count": sent})

# ── WhatsApp webhook ──────────────────────────────────────────────────
@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    try:
        incoming = request.form.get("Body", "").strip()
        sender   = request.form.get("From", "")
        print("Message received:", incoming)
        print("From:", sender)
        try:
            db.users.update_one(
                {"phone": sender},
                {"$setOnInsert": {"phone": sender, "joined": datetime.now()}},
                upsert=True
            )
            print("User saved to DB")
        except Exception as e:
            print("DB save warning:", e)
        reply = ask_ai(incoming)
        print("AI replied:", reply)
        resp = MessagingResponse()
        resp.message(reply)
        return str(resp)
    except Exception as e:
        print("ERROR IN WHATSAPP ROUTE:")
        print(traceback.format_exc())
        resp = MessagingResponse()
        resp.message("Sorry, something went wrong. Please try again.")
        return str(resp)

@app.route("/add-reminder", methods=["POST"])
def add_reminder():
    try:
        data  = request.json
        phone = format_phone(data["phone"])
        db.reminders.insert_one({
            "phone":   phone,
            "date":    data["date"],
            "time":    data.get("time", "09:00"),
            "message": data["message"],
            "sent":    False
        })
        return jsonify({"status": "reminder added"})
    except Exception as e:
        print("Reminder error:", e)
        return jsonify({"status": "error"}), 500

def send_reminders():
    try:
        now_dt   = datetime.now()
        today    = now_dt.strftime("%Y-%m-%d")
        now_time = now_dt.strftime("%H:%M")
        print(f"Checking reminders for {today} at {now_time}")
        due = db.reminders.find({
            "date": today,
            "time": {"$lte": now_time},
            "sent": False
        })
        for r in due:
            try:
                twilio_client.messages.create(
                    from_="whatsapp:+14155238886",
                    to=r["phone"],
                    body="Health Reminder from Aarogya: " + r["message"]
                )
                db.reminders.update_one(
                    {"_id": r["_id"]},
                    {"$set": {"sent": True}}
                )
                print("Reminder sent to:", r["phone"])
            except Exception as e:
                print("Failed to send reminder:", e)
    except Exception as e:
        print("Send reminders error:", e)

scheduler = BackgroundScheduler()
scheduler.add_job(send_reminders, 'interval', minutes=1)
scheduler.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
