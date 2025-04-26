import subprocess
import sys

# check for required packages and install any that are missing
required_packages = ['openai', 'pyautogui', 'pyperclip', 'pygetwindow', 'openpyxl', 'pandas']

for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        print(f"Installing missing package: {package}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

import pandas as pd
import pyautogui
import pyperclip
import random
import time
import os
import sys
import pygetwindow as gw
from openai import OpenAI
from datetime import datetime, timedelta

# variable to save the successful Copilot shortcut into
copilot_shortcut = None

# get the folder from where the script is running
import sys

if getattr(sys, 'frozen', False):
    # Running from a bundled .exe
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Running from .py file
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# load the user's API key from a text file
def load_api_key(filename="api_key.txt"):
    try:
        with open(os.path.join(BASE_DIR, filename), "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("Error: api_key.txt not found.")
        return None

# load the list of user created topics
def load_topics(filename="PromptTopics.txt"):
    try:
        with open(os.path.join(BASE_DIR, filename), "r") as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print("Error: PromptTopics.txt not found.")
        return[]

# initialize API key
api_key = load_api_key()
if not api_key:
    print("No API key found: Exiting.")
    exit()

# initialize OpenAI client
client = OpenAI(api_key=api_key)

# get a prompt from GPT
def get_prompt_from_gpt(topic):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant who generates prompts to be sent to an AI"},
                {"role": "user", "content": f"Please generate a prompt based on this topic: {topic}"}
            ],
            max_tokens=100,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error getting GPT: {e}")
        return None

# function to check if the Copilot window opens
def is_copilot_open(timeout=5):
    for _ in range(timeout):
        titles = [w.title.strip() for w in gw.getWindowsWithTitle("Copilot")]
        if "Copilot" in titles:
            return True
        time.sleep(1)
    return False

# open Copilot using an automated key press
def open_copilot():

    global copilot_shortcut

    # try to open with alt+space
    print('Trying to open Copilot with alt+space...')
    pyautogui.hotkey('alt', 'space')
    time.sleep(5) # give time to open


    if is_copilot_open():
        copilot_shortcut = 'alt+space'
        print('Copilot opened with alt+space')
        return

    else:
        # if alt+space doesn't work, try windows+c
        print('Copilot not detected. Trying windows+c...')
        pyautogui.hotkey('win', 'c')
        time.sleep(5)

        if is_copilot_open():
            copilot_shortcut = 'win+c'
            print('Copilot Successfully opened with windows+c')
            return

        else:
            print('Failed to open Copilot. Exiting.')
            exit()

# get the message bar X-Y coordinates from an Excel file
def load_coordinates_from_excel(filename='XY_coordinates.xlsx'):
    try:
        df = pd.read_excel(os.path.join(BASE_DIR, filename))
        setting = {row['setting']: row['value'] for _, row in df.iterrows()}
        x = int(setting.get('X Coordinates', 0))
        y = int(setting.get('Y Coordinates', 0))
        return x, y
    except Exception as e:
        print(f"Error reading coordinates from Excell {e}")
        return None, None

# click on the message bar
def focus_message_bar():
    x, y = load_coordinates_from_excel()
    if x is not None and y is not None:
        print(f'Clicking message bar at X:{x}, Y:{y}')
        pyautogui.click(x, y)
        time.sleep(1)
    else:
        print('Failed to load coordinates: Exiting.')
        exit()

# paste and send message to copilot
def send_message(text):
    pyperclip.copy(text)
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('enter')

# exit Copilot
def close_copilot():
    if copilot_shortcut == 'alt+space':
        pyautogui.hotkey('alt', 'space')

    elif copilot_shortcut == 'win+c':
        pyautogui.hotkey('win', 'c')

    else:
        print('Closing Copilot via shortcut failed. Please exit Copilot.')

    time.sleep(2)

# main
def run_task():
    topics = load_topics()
    if not topics:
        print("Error finding topics.")
        return

    topic = random.choice(topics)
    print(f'Selected topic: {topic}')

    prompt = get_prompt_from_gpt(topic)
    if not prompt:
        print("No prompt generated.")
        return
    print(f"Generated Prompt: {prompt}")
    open_copilot()
    focus_message_bar()
    time.sleep(1)
    send_message(prompt)
    time.sleep(10)
    close_copilot()

    # wait for a response
    time.sleep(10)

# choose a random amount of time between 30 and 70 minutes, and then set that as the time until the next prompt
def time_until_next_run():
    return random.randint(30,70)

# tell the user that the program is running
print('PromptBot is running. To exit the program, press Ctrl+C')

# schedule the next prompt
while True:
    run_task() # initial run happens immediately

    wait_minutes = time_until_next_run()
    next_run_time = datetime.now() + timedelta(minutes=wait_minutes)
    print(f"Run complete. The next run will happen in {wait_minutes} minutes, ({next_run_time.strftime('%I:%M %p')})\n")

    time.sleep(wait_minutes * 60) # convert the wait time from minutes into seconds, and wait for the next run