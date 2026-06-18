from flask import Flask, render_template, request, jsonify, session
import random
import os

app = Flask(__name__)
# Secret key is required to sign session cookies securely
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "super-secret-key-for-hangman-12345")

WORDS = ["python", "banana", "orange", "guitar", "window"]

def start_new_game():
    word = random.choice(WORDS)
    session["word"] = word
    session["display"] = "_" * len(word)
    session["guessed_letters"] = []
    session["wrong_guesses"] = 0
    session["max_wrong"] = 6
    session["game_over"] = False
    session["won"] = False

def current_state():
    return {
        "display": " ".join(session.get("display", "")),
        "guessed_letters": session.get("guessed_letters", []),
        "wrong_guesses": session.get("wrong_guesses", 0),
        "max_wrong": session.get("max_wrong", 6),
        "game_over": session.get("game_over", False),
        "won": session.get("won", False)
    }

@app.route("/")
def home():
    if "word" not in session:
        start_new_game()
    return render_template("index.html")

@app.route("/api/state", methods=["GET"])
def get_state():
    if "word" not in session:
        start_new_game()
    return jsonify(current_state())

@app.route("/api/guess", methods=["POST"])
def guess():
    if "word" not in session:
        start_new_game()

    if session.get("game_over"):
        return jsonify({"message": "Game is over. Start a new game.", "state": current_state()})

    data = request.get_json()
    letter = data.get("letter", "").lower().strip()

    if not letter or len(letter) != 1 or not letter.isalpha():
        return jsonify({"message": "Please enter a single valid letter."})

    guessed_letters = session.get("guessed_letters", [])
    if letter in guessed_letters:
        return jsonify({"message": "You already guessed that letter."})

    # Update guessed letters list (needs re-assignment to notify session changes)
    guessed_letters.append(letter)
    session["guessed_letters"] = guessed_letters

    word = session.get("word", "")
    display = session.get("display", "")
    wrong_guesses = session.get("wrong_guesses", 0)
    max_wrong = session.get("max_wrong", 6)

    if letter in word:
        new_display = list(display)
        for i, ch in enumerate(word):
            if ch == letter:
                new_display[i] = letter
        session["display"] = "".join(new_display)
    else:
        session["wrong_guesses"] = wrong_guesses + 1

    # Check game status
    if "_" not in session.get("display", ""):
        session["game_over"] = True
        session["won"] = True
        return jsonify({"message": "You win!", "state": current_state()})

    if session.get("wrong_guesses", 0) >= max_wrong:
        session["game_over"] = True
        session["won"] = False
        return jsonify({"message": f"You lost! The word was {word}.", "state": current_state()})

    return jsonify({"message": "Guess recorded.", "state": current_state()})

@app.route("/api/new", methods=["POST"])
def new_game():
    start_new_game()
    return jsonify({"message": "New game started.", "state": current_state()})

if __name__ == "__main__":
    app.run(debug=True)