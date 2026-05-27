import re
import random
from datetime import datetime

history = []

def chat(msg):
    history.append(msg)
    if re.search(r'weather', msg, re.I):
        return "It is 22°C and sunny today! (simulated)"
    elif re.search(r'news', msg, re.I):
        return "Breaking: Scientists discover water on Mars! (simulated)"
    elif re.search(r'time', msg, re.I):
        return f"Current time: {datetime.now().strftime('%H:%M:%S')}"
    elif re.search(r'joke', msg, re.I):
        return random.choice(["Why did the chicken cross the road? To get to the other side!", "I told a joke about pizza... it was too cheesy."])
    elif re.search(r'bye|quit', msg, re.I):
        return "Goodbye!"
    else:
        return "I'm still learning so I don't understand. Try: weather, news, time, or joke."

print("Chatbot started! Type 'quit' to exit.")
while True:
    user = input("You: ")
    response = chat(user)
    print(f"Bot: {response}")
    if "Goodbye" in response:
        break
print(f"Chat ended. You sent {len(history)} messages.")
