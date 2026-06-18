"""
Task 4: Rule-Based Chatbot - Flask Backend
Key Concepts: if-elif, functions, loops, input/output
"""

from flask import Flask, render_template, request, jsonify
import random
from datetime import datetime

app = Flask(__name__)

# ─── Rule-Based Response Engine ─────────────────────────────────────────────

def get_bot_response(user_message):
    """
    Rule-based chatbot using if-elif logic.
    Maps user input patterns to predefined replies.
    """
    # Normalize the input: lowercase and strip whitespace
    import re
    message = user_message.lower().strip()
    message = re.sub(r'[^\w\s]', '', message)

    # ── Greeting Rules ──────────────────────────────────────────────────
    if message in ["hello", "hi", "hey", "hola", "howdy"]:
        replies = ["Hi! 👋", "Hello there! 😊", "Hey! How can I help you?", "Howdy! 🤠"]
        return random.choice(replies)

    elif message in ["good morning", "morning"]:
        return "Good morning! ☀️ Hope you're having a great start to the day!"

    elif message in ["good evening", "evening"]:
        return "Good evening! 🌙 How was your day?"

    elif message in ["good night", "night", "gn"]:
        return "Good night! 🌟 Sweet dreams!"

    # ── How Are You Rules ───────────────────────────────────────────────
    elif message in ["how are you", "how are you?", "how r u", "how are u"]:
        replies = [
            "I'm fine, thanks! 😄",
            "Doing great! How about you? 🌟",
            "I'm wonderful, thank you for asking! ✨",
            "Never been better! 🚀"
        ]
        return random.choice(replies)

    elif message in ["what's up", "whats up", "sup", "wassup"]:
        replies = [
            "Not much! Just here to chat 💬",
            "The sky! 😄 Just kidding, what's up with you?",
            "All good here! What can I do for you? 🎯"
        ]
        return random.choice(replies)

    # ── Identity Rules ──────────────────────────────────────────────────
    elif message in ["what is your name", "what's your name", "who are you", "whats your name"]:
        return "I'm ChatBuddy 🤖, your friendly rule-based chatbot!"

    elif message in ["how old are you", "what is your age", "your age"]:
        return "I'm timeless! ⏳ I was just created to chat with you!"

    # ── Gratitude Rules ─────────────────────────────────────────────────
    elif message in ["thank you", "thanks", "thank u", "thx", "ty"]:
        replies = [
            "You're welcome! 😊",
            "Happy to help! 🎉",
            "Anytime! Don't hesitate to ask more! 💪",
            "No problem at all! ✨"
        ]
        return random.choice(replies)

    # ── Help Rules ──────────────────────────────────────────────────────
    elif message in ["help", "help me", "i need help"]:
        return ("Sure! I can chat about:\n"
                "👋 Greetings (hello, hi, hey)\n"
                "❓ How I'm doing (how are you)\n"
                "🧠 Fun facts (tell me a fact)\n"
                "😂 Jokes (tell me a joke)\n"
                "⏰ Time (what time is it)\n"
                "👋 Goodbyes (bye, goodbye)")

    # ── Fun Facts Rules ─────────────────────────────────────────────────
    elif message in ["tell me a fact", "fact", "fun fact", "interesting fact"]:
        facts = [
            "🧠 Honey never spoils. Archaeologists found 3000-year-old honey in Egyptian tombs!",
            "🐙 An octopus has three hearts and blue blood!",
            "🌍 A day on Venus is longer than a year on Venus!",
            "🍌 Bananas are berries, but strawberries are not!",
            "💡 A bolt of lightning is 5x hotter than the surface of the sun!",
            "🦈 Sharks have been around longer than trees!",
        ]
        return random.choice(facts)

    # ── Joke Rules ──────────────────────────────────────────────────────
    elif message in ["tell me a joke", "joke", "make me laugh", "funny"]:
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything! 😂",
            "Why did the scarecrow win an award? He was outstanding in his field! 🌾",
            "What do you call a fake noodle? An impasta! 🍝",
            "Why don't eggs tell jokes? They'd crack each other up! 🥚",
            "What did the ocean say to the beach? Nothing, it just waved! 🌊",
        ]
        return random.choice(jokes)

    # ── Time Rules ──────────────────────────────────────────────────────
    elif message in ["what time is it", "time", "current time", "what's the time"]:
        now = datetime.now().strftime("%I:%M %p")
        return f"It's currently {now} ⏰"

    elif message in ["what day is it", "today", "date", "what's the date"]:
        today = datetime.now().strftime("%A, %B %d, %Y")
        return f"Today is {today} 📅"

    # ── Mood Rules ──────────────────────────────────────────────────────
    elif message in ["i'm happy", "im happy", "i am happy", "feeling good", "feeling great"]:
        return "That's wonderful to hear! 🎉 Keep spreading those good vibes!"

    elif message in ["i'm sad", "im sad", "i am sad", "feeling sad", "feeling down"]:
        return "I'm sorry to hear that 💙 Remember, tough times don't last, but tough people do! You've got this! 💪"

    elif message in ["i'm bored", "im bored", "i am bored", "bored"]:
        return "Let's fix that! Try asking me for a joke or a fun fact! 🎮"

    # ── Goodbye Rules ───────────────────────────────────────────────────
    elif message in ["bye", "goodbye", "see you", "see ya", "cya", "later"]:
        replies = [
            "Goodbye! 👋 Have a wonderful day!",
            "See you later! 🌟 Take care!",
            "Bye bye! Come back anytime! 😊",
            "Until next time! ✨"
        ]
        return random.choice(replies)

    # ── Default / Fallback ──────────────────────────────────────────────
    else:
        fallback = [
            "Hmm, I'm not sure I understand that 🤔 Try saying 'help' to see what I can do!",
            "That's interesting! I'm still learning though 📚 Type 'help' for suggestions!",
            "I don't have a response for that yet 😅 But try asking me a joke or fact!",
        ]
        return random.choice(fallback)


# ─── Routes ─────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the chatbot frontend."""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """API endpoint: receive user message, return bot response."""
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message.strip():
        return jsonify({"reply": "Please type something! 😊"}), 400

    bot_reply = get_bot_response(user_message)
    return jsonify({
        "reply": bot_reply,
        "timestamp": datetime.now().strftime("%I:%M %p")
    })


@app.route("/suggestions")
def suggestions():
    """Return quick-reply suggestion chips."""
    chips = [
        "Hello 👋",
        "How are you?",
        "Tell me a joke",
        "Tell me a fact",
        "What time is it?",
        "Help",
        "Bye"
    ]
    return jsonify({"suggestions": chips})


# ─── Run ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5002)
