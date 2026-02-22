from tkinter import *
import pyttsx3
import speech_recognition as sr
import os
import webbrowser
import datetime
import subprocess
import logging
import time
import requests
from bs4 import BeautifulSoup

logging.basicConfig(filename='bujji.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  

def speak(text):
    engine.say(text)
    engine.runAndWait()

def take_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        speak("Listening...")
        audio = recognizer.listen(source)
    
    try:
        query = recognizer.recognize_google(audio).lower()
        print(f"You said: {query}")
        return query
    except sr.UnknownValueError:
        speak("Sorry, I did not catch that. Could you please repeat?")
        logging.error("Speech recognition could not understand audio")
        return ""
    except sr.RequestError:
        speak("Sorry, there was an issue with the speech recognition service. Please try again later.")
        logging.error("Could not request results from Google Speech Recognition service")
        return ""

def wish():
    hour = int(datetime.datetime.now().hour)
    if hour < 12:
        greet = "Good morning"
    elif 12 <= hour < 18:
        greet = "Good afternoon"
    else:
        greet = "Good evening"
    
    speak(f"Hi boss, {greet}. How are you today? What can I help you with today?")

def turn_on_wifi():
    try:
        if os.name == 'nt':  # For Windows
            subprocess.run(["netsh", "interface", "set", "interface", "Wi-Fi", "admin=enable"], check=True)
        elif os.name == 'posix':  # For macOS/Linux
            subprocess.run(["nmcli", "radio", "wifi", "on"], check=True)
        speak("Wi-Fi has been turned on.")
    except Exception as e:
        speak("An error occurred while trying to turn on Wi-Fi.")
        logging.error(f"Error turning on Wi-Fi: {e}")

def search_information(query):
    search_query = '+'.join(query.split())
    url = f"https://www.google.com/search?q={search_query}"

    webbrowser.open(url)
    speak("Searching for information. Please wait while I gather details.")

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    result_text = soup.get_text()[:2000]  # Limit text for demonstration

    speak(f"I have found some information. Please check your browser.")

def execute_command(command):
    try:
        if "hi bujji" in command:
            speak("Hi boss, I am your assistant Bujji. How can I help you today?")
        elif "hi" in command or "hello" in command:
            speak("Hi! How can I assist you today?")
        elif "open notepad" in command:
            os.system('notepad')
            speak("Notepad is now open. How can Pandu assist you further?")
        elif "open youtube" in command:
            speak("What video would you like to watch?")
            video_query = take_command()
            webbrowser.open(f"https://www.youtube.com/results?search_query={video_query}")
            speak(f"Searching for {video_query} on YouTube. Anything else?")
        elif "open chrome" in command:
            speak("What would you like to browse?")
            search_query = take_command()
            if not search_query.startswith(('http://', 'https://')):
                search_query = 'https://' + search_query
            webbrowser.open(search_query)
            speak(f"Opening {search_query} in your browser. Is there anything else Pandu can do?")
        elif "turn on wifi" in command:
            turn_on_wifi()
        elif "search" in command:
            speak("What would you like to search for?")
            search_query = take_command()
            search_information(search_query)
        elif "open whatsapp" in command or "send a message on whatsapp" in command:
            speak("Who should Pandu send a message to? Provide the contact number including the country code.")
            contact = take_command()
            speak("What is the message?")
            message = take_command()
            # send_whatsapp_message(contact, message)
            speak("Message sent. Anything else?")
        elif "play music" in command:
            speak("Which song would you like to listen to?")
            song_query = take_command()
            webbrowser.open(f"https://www.spotify.com/search/{song_query}")
            speak(f"Playing {song_query} on Spotify. Enjoy your music! Need anything else?")
        elif "stop listening" in command or "exit" in command:
            speak("Goodbye! Have a great day.")
            logging.info("Program exited by user")
            return False
        elif "what time is it" in command:
            current_time = datetime.datetime.now().strftime("%H:%M")
            speak(f"The time is {current_time}.")
        elif "tell me a joke" in command:
            speak("Why don't scientists trust atoms? Because they make up everything!")
        elif "close all tabs" in command or "close browser" in command:
            subprocess.run(["taskkill", "/IM", "chrome.exe", "/F"])
            speak("All browser tabs are now closed. Is there anything else Pandu can do?")
        else:
            speak("I didn't understand that command. Could you please repeat?")
            logging.warning(f"Unrecognized command: {command}")
    except Exception as e:
        speak("An error occurred while executing the command. Please try again.")
        logging.error(f"Error executing command '{command}': {e}")
    return True

def verify_user():
    """Verify if the user is one of the allowed members."""
    allowed_names = ["sukumar", "varshini", "harsha", "susmitha", "basha",]
    speak("Please say your name.")
    name = take_command()
    if name in allowed_names:
        speak(f"Hi boss, I am your assistant bujji. How can I help you today?")
        return True
    else:
        speak("Sorry, I do not recognize this name. Exiting...")
        logging.warning(f"Unrecognized user: {name}")
        return False

def start_voice_assistant():
    """Start the voice assistant when 'Start' button is clicked."""
    if verify_user():
        wish()
        while True:
            query = take_command()
            if not execute_command(query):
                break
            time.sleep(1)  # Brief pause to reduce CPU usage

# GUI Setup using Tkinter
scr = Tk()
scr.geometry("900x600")
scr.title("Voice Detector")

# Background Image
bg_image = PhotoImage(file="bujji.png")
background_label = Label(scr, image=bg_image)
background_label.place(x=1, y=1, relwidth=1, relheight=1)
scr.configure(background="black")

# Creating Labels
L1 = Label(scr, text="Voice Detector", font=("arial", 40, "bold"), fg="black", bg="sky blue").place(x=300, y=30)
L2 = Label(scr, text="Voice Assistant as Bujji", font=("arial", 20), fg="black", bg="sky blue").place(x=320, y=110)

# Creating Button to Start Assistant
insert = Button(scr, text="Start", font=("bold", 20), fg="blue", bg="white", width=10, command=start_voice_assistant).place(x=600, y=200)

scr.mainloop()

