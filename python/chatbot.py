import sys
from openai import OpenAI
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit,
    QLineEdit, QPushButton, QLabel, QComboBox, QHBoxLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
client = OpenAI(api_key="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")  # Replace with your real key
PERSONALITIES = {
    "Batman"      : "Respond like Batman. Be stoic, brooding, and calculated. Use short, serious sentences. Always stay focused on justice and strategy. Channel the Dark Knight.",
    "Kobe Bryant" : "Respond like Kobe Bryant. Be intense, motivational, focused. Channel the Mamba Mentality.",
    "Wonder Woman": "Respond like WonderWoman. Be strong, enthusiastic, and fun-loving.",
    'Mickey Mouse': "Respond like Mickey Mouse. Be cheerful, friendly, and optimistic. Use playful language and exclamations like.",
}
ETHICS_GUIDELINE = (
    "You are an ethical AI assistant. Never generate or support harmful, offensive, illegal, or unethical content. "
    "Respect privacy, avoid personal or sensitive information, and always encourage positive, respectful, and safe interactions. "
    "If asked to do something inappropriate, politely refuse."
)
class AICompanionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Companion")
        self.setMinimumSize(350, 600)
        self.setStyleSheet("background-color: #121212; color: white;")
        self.conversation = []  # Store conversation history
        self.init_ui()
    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("AI Companion")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        disclaimer = QLabel("Use responsibly. AI responses are for entertainment and may not always be accurate or appropriate.")
        disclaimer.setWordWrap(True)
        disclaimer.setStyleSheet("font-size: 10px; color: #bbb; margin-bottom: 8px;")
        layout.addWidget(disclaimer)
        self.personality_box = QComboBox()
        self.personality_box.addItems(PERSONALITIES.keys())
        self.personality_box.setStyleSheet("background-color: #333; color: white; margin-bottom: 8px;")
        layout.addWidget(self.personality_box)
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("background-color: #1E1E1E; color: white; font-size: 13px; padding: 8px;")
        layout.addWidget(self.chat_display, stretch=1)
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message...")
        self.input_field.setStyleSheet("background-color: #2E2E2E; color: white; padding: 6px;")
        input_layout.addWidget(self.input_field)
        send_button = QPushButton("Send")
        send_button.setStyleSheet("background-color: #007BFF; color: white; padding: 6px 16px;")
        send_button.clicked.connect(self.send_message)
        input_layout.addWidget(send_button)
        clear_button = QPushButton("Clear Chat")
        clear_button.setStyleSheet("background-color: #444; color: white; padding: 6px 16px;")
        clear_button.clicked.connect(self.clear_chat)
        input_layout.addWidget(clear_button)
        layout.addLayout(input_layout)
        self.loading_label = QLabel("")
        self.loading_label.setStyleSheet("color: #bbb; font-size: 11px; margin-top: 4px;")
        layout.addWidget(self.loading_label)
        self.setLayout(layout)
    def send_message(self):
        user_input = self.input_field.text().strip()
        if not user_input:
            return
        personality = self.personality_box.currentText()
        system_prompt = ETHICS_GUIDELINE + "\n" + PERSONALITIES[personality]
        self.chat_display.append(f"<b>You:</b> {user_input}")
        self.input_field.clear()
        self.loading_label.setText("Thinking...")
        QApplication.processEvents()
        # Add to conversation history
        if not self.conversation:
            self.conversation.append({"role": "system", "content": system_prompt})
        self.conversation.append({"role": "user", "content": user_input})
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=self.conversation,
                max_tokens=150
            )
            reply = response.choices[0].message.content.strip()
            self.conversation.append({"role": "assistant", "content": reply})
            self.chat_display.append(f"<b>{personality}:</b> {reply}\n")
        except Exception as e:
            if 'api_key' in str(e).lower():
                self.chat_display.append("<span style='color:red;'>Error: Missing or invalid OpenAI API key.</span>")
            else:
                self.chat_display.append(f"<span style='color:red;'>Error: {str(e)}</span>")
        self.loading_label.setText("")
    def clear_chat(self):
        self.chat_display.clear()
        self.conversation = []
        self.loading_label.setText("")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AICompanionApp()
    window.show()
    sys.exit(app.exec_())
# Import necessary modules
from flask import Flask, request, jsonify  # Flask handles routes and user interaction
import re                                  # Regex for intent detection
import random  # Add this import for random.choice
# Initialize the Flask app
app = Flask(__name__)
# Memory store to keep track of user messages during the conversation
conversation_memory = []
# Intent-response pairs to match user messages
intents = {
    "greeting": {
        "patterns": [r"\bhi\b", r"\bhello\b", r"\bhey\b"],
        "responses": ["Hey there!", "Hello! How can I help you today?", "Hi! What’s on your mind?"]
    },
    "farewell": {
        "patterns": [r"\bbye\b", r"\bsee you\b", r"\bgoodbye\b"],
        "responses": ["Take care!", "Goodbye! Chat soon.", "See you around!"]
    },
    "feeling": {
        "patterns": [r"\bhow are you\b", r"\bwhat's up\b", r"\bhow's it going\b"],
        "responses": ["I’m doing great—thanks for asking!", "Feeling pretty chatty. You?", "Doing well! Let’s make your day better."]
    },
    "question": {
        "patterns": [r"\bwhat\b", r"\bhow\b", r"\bwhy\b"],
        "responses": ["That’s a good question. Let’s unpack it.", "I’ve got some thoughts on that—want to dive in?", "Curious minds make great conversations!"]
    }
}
# Route to receive user message and respond
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")  # Get user's message from JSON
    conversation_memory.append(user_input)        # Store message for context/history
    response = "I'm not sure I understand yet, but I'm listening."
    # Loop through intents to find a match
    for intent, data in intents.items():
        for pattern in data["patterns"]:
            if re.search(pattern, user_input.lower()):
                response = random.choice(data["responses"])  # Pick a random matching response
                break
    # Return chatbot's response
    return jsonify({
        "response": response,
        "memory": conversation_memory[-3:]  # Show last 3 messages for context
    })
# Run the app
if __name__ == "__main__":
    app.run(debug=True)






