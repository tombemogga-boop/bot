import os
from flask import Flask, request
import requests

# Telegram setup
TOKEN = os.environ.get("BOT_TOKEN")
URL = f"https://api.telegram.org/bot{TOKEN}"

# Hugging Face setup
HF_TOKEN = os.environ.get("HF_TOKEN")
HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

app = Flask(__name__)

# Function to get AI response
def get_ai_response(user_message):
    try:
        response = requests.post(
            HF_API_URL,
            headers=headers,
            json={"inputs": user_message}
        )

        result = response.json()

        # Handle response safely
        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"]

        elif isinstance(result, dict) and "error" in result:
            return "AI is busy right now. Try again."

        else:
            return "I didn't understand that. Try again."

    except Exception as e:
        return "Error connecting to AI."

# Home route
@app.route("/", methods=["GET"])
def home():
    return "Bot is running with AI!"

# Webhook route
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")

    if chat_id and text:
        reply = get_ai_response(text)

        requests.post(f"{URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": reply
        })

    return "ok"

# Run app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)