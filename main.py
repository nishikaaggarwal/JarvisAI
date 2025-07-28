import os
import json
import random
import datetime
import time
import threading
import requests
import socket
import webbrowser
import pyttsx3
import speech_recognition as sr
import pyaudio
import wikipedia
from plyer import notification
from msal import PublicClientApplication

CLIENT_ID = "Add yous"
TENANT_ID = "add yours"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["Mail.Read", "Calendars.Read"]

engine = pyttsx3.init()
recognizer = sr.Recognizer()

with open("timetable.json") as f:
    TIMETABLE = json.load(f)
with open("exercise_plan.json") as f:
    EXERCISES = json.load(f)

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "Why was the computer cold? It left its Windows open.",
    "I told my computer I needed a break, and it said: 'No problem, I'll go to sleep!'",
    "Why was the math book sad? Because it had too many problems.",
    "Debugging is like being the detective in a crime movie where you are also the murderer."
]

SITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "wikipedia": "https://www.wikipedia.org",
    "chatgpt": "https://chat.openai.com",
    "leetcode": "https://leetcode.com",
    "github": "https://github.com",
    "whatsapp": "https://web.whatsapp.com",
    "email": "https://mail.google.com"
}

def speak(text):
    engine.say(text)
    engine.runAndWait()

def notify_user(title, msg):
    notification.notify(title=title, message=msg, app_name="Jarvis", timeout=5)

def listen():
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio, language="en-in")
    except:
        return "None"

def internet_available():
    try:
        socket.create_connection(("1.1.1.1", 53), timeout=3)
        return True
    except:
        return False

def mic_available():
    try:
        audio = pyaudio.PyAudio()
        count = audio.get_device_count()
        audio.terminate()
        return count > 0
    except:
        return False

def tell_joke():
    speak(random.choice(JOKES))

def get_weather(city):
    try:
        url = f"https://wttr.in/{city}?format=3"
        response = requests.get(url, timeout=5).text
        speak(response)
    except:
        speak("Unable to fetch information.")

def get_news():
    try:
        url = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
        response = requests.get(url, timeout=5).text
        headlines = [line.split("<title>")[1].split("</title>")[0]
                     for line in response.splitlines() if "<title>" in line]
        if len(headlines) > 1:
            speak("Here are the top 5 headlines:")
            for i, headline in enumerate(headlines[1:6], 1):
                speak(f"{i}: {headline}")
        else:
            speak("Couldn't get the latest news.")
    except:
        speak("Unable to fetch news.")

def get_wiki_summary(query):
    try:
        summary = wikipedia.summary(query, sentences=2)
        speak(summary)
        return True
    except:
        return False

def today_exercise():
    day = datetime.datetime.now().strftime("%A").lower()
    speak(f"Today's exercise: {EXERCISES.get(day, 'Take it easy today!')}")

def authenticate_graph():
    app = PublicClientApplication(CLIENT_ID, authority=AUTHORITY)
    accounts = app.get_accounts()
    result = None
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
    if not result:
        flow = app.initiate_device_flow(scopes=SCOPES)
        print("Use this code to sign in:", flow["user_code"])
        print(flow["verification_uri"])
        result = app.acquire_token_by_device_flow(flow)
    return result

def check_outlook_mail(token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        url = "https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages?$filter=isRead eq false&$top=5"
        res = requests.get(url, headers=headers).json()
        messages = res.get("value", [])
        if not messages:
            speak("You have no new emails.")
        else:
            speak(f"You have {len(messages)} new emails.")
            for msg in messages:
                speak(f"From {msg['from']['emailAddress']['name']}: {msg['subject']}")
    except:
        speak("Unable to access Outlook mails.")

def check_schedule_reminders():
    while True:
        now = datetime.datetime.now().strftime("%H:%M")
        for slot, task in TIMETABLE.items():
            start, _ = slot.split("-")
            remind_time = (datetime.datetime.strptime(start, "%H:%M") - datetime.timedelta(minutes=5)).strftime("%H:%M")
            if now == remind_time:
                notify_user("Upcoming Task", f"In 5 minutes: {task}")
                speak(f"Reminder: In 5 minutes, you have {task}.")
        time.sleep(60)

def handle_query(query, token):
    q = query.lower().strip()
    if not q or q in {"exit", "quit"}:
        return False
    if "shutdown" in q:
        speak("Shutting down now.")
        return False
    if "joke" in q:
        tell_joke()
        return True
    if "exercise" in q:
        today_exercise()
        return True
    if "outlook" in q or "check mail" in q:
        if token:
            check_outlook_mail(token)
        else:
            speak("Outlook access is not configured. Please check your credentials.")
        return True
    if "news" in q:
        get_news()
        return True
    if "weather in" in q:
        city = q.split("weather in")[-1].strip()
        get_weather(city)
        return True
    for name, url in SITES.items():
        if f"open {name}" in q:
            speak(f"Opening {name}")
            webbrowser.open(url)
            return True
    if get_wiki_summary(query):
        return True
    speak("I couldn't find an answer to that.")
    return True

def run_jarvis():
    token = None
    if internet_available():
        token_result = authenticate_graph()
        token = token_result.get("access_token") if token_result else None
    else:
        speak("No internet. Running in offline mode.")

    threading.Thread(target=check_schedule_reminders, daemon=True).start()

    notify_user("Jarvis", "I'm online")
    speak("Hey, I'm Jarvis. Ready to help!")

    while True:
        mode = input("Choose mode: 1 Typing, 2 Voice: ").strip()
        if mode == "1":
            while True:
                query = input("Ask Jarvis: ").strip()
                if query and not handle_query(query, token):
                    break
        elif mode == "2":
            while True:
                print("Speak now (say 'exit' to stop):")
                query = listen().lower()
                if query not in {"none", ""} and not handle_query(query, token):
                    break
        else:
            speak("Invalid mode.")
            continue

        again = input("Continue communicating? (yes/no): ").strip().lower()
        if again != "yes":
            speak("Bye! Have a nice day.")
            break

if __name__ == "__main__":
    run_jarvis()
