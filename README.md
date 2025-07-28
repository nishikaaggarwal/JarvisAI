# JarvisAI

A smart Python-based personal assistant that keeps you updated, organized, and entertained via voice or text.

---

# Features
- Outlook mail integration via Microsoft Graph
- Schedule and exercise reminders from your own JSON files
- News and weather updates using free APIs
- Wikipedia-powered Q&A for general knowledge
- Fun and engaging jokes
- Voice or text-based communication modes

---

# Setup
1. Clone the repo and install dependencies:
    ```bash
    git clone https://github.com/yourusername/JarvisAI.git
    cd JarvisAI
    pip install -r requirements.txt
    ```

2. Add two JSON files:
    - **`timetable.json`** – for your daily schedule  
    - **`exercise_plan.json`** – for your exercise plan  

3. Configure your Microsoft Graph **CLIENT_ID** and **TENANT_ID** in `main.py` for Outlook mail access.

# Future Plans
I will soon add a **voice cloning feature** so that Jarvis can replicate my voice in my absence.
