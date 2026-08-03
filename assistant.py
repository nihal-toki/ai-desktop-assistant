import os
from dotenv import load_dotenv
from google import genai
from pynput import keyboard

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def ask_gemini():
    question = input("\nAsk something: ")
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=question
    )
    print("Gemini says:", response.text)

def for_canonical(f):
    return lambda k: f(l.canonical(k))

hotkey = keyboard.HotKey(
    keyboard.HotKey.parse('<cmd>+<shift>+a'),
    ask_gemini
)

l = keyboard.Listener(
    on_press=for_canonical(hotkey.press),
    on_release=for_canonical(hotkey.release)
)

print("Assistant ready. Press Cmd+Shift+A to ask a question. (Ctrl+C to stop)")
l.start()
l.join()