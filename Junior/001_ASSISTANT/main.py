# import re
# import threading
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import openai
import os
import time
import random
import multiprocessing
import pywhatkit

# Speech engine initialisation: gTTS


def speak(text):
    tts = gTTS(text)
    # max 6 speaker speak at same time
    try:
        for i in range(5):
            # avoid playsound start at same time and raise error
            time.sleep(random.random())
            if os.path.isfile(f"temp{i}.mp3"):
                continue
            else:
                tts.save(f"temp{i}.mp3")
                playsound(f"temp{i}.mp3")
                os.remove(f"temp{i}.mp3")
                break
    except Exception as e:
        print(f"Error occurred in speak()! Error name: {e}")


def speak_thread(text):
    global proc_speak
    # t = threading.Thread(target=speak, args=[text])
    t = multiprocessing.Process(target=speak, args=[text])
    t.start()
    proc_speak.append(t)


# generate response from openai, please read Documentation for understand parameters
# https://platform.openai.com/docs/api-reference/


def generate_response(promt, type='chat'):
    if type == 'chat':
        response_ai = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"{promt}"}]
        )
        return response_ai.choices[0].message["content"].strip()


# convert speech to text


def speech2text():
    listener = sr.Recognizer()
    print('Listening for a command...')

    with sr.Microphone() as source:
        listener.pause_threshold = 2
        input_speech = listener.listen(source)

    try:
        print('Recognizing speech...')
        query = listener.recognize_google(input_speech, language='en-US')
        # query = listener.recognize_whisper_api(input_speech, api_key=api_key)
        print(f'The input speech was: {query}')
    except Exception as exception:
        print('I did not quite catch that')
        print(exception)
        return 'None'

    return query


# execute command types


def play_music():
    try:
        speak_thread('What do you want to play')
        command = speech2text().lower()
        pywhatkit.playonyt(command)
    except:
        speak_thread('I can not hear it')


def chat_bot():
    try:
        speak_thread('What do you want to ask')
        command = speech2text().lower()
        reply = generate_response(command)
        speak_thread(reply)
        print('Reply: ' + str(reply))
    except:
        speak_thread('I can not hear it')


def google_search():
    try:
        speak_thread('What do you want to search')
        command = speech2text().lower()
        pywhatkit.search(command)
    except:
        speak_thread('I can not hear it')


def stop_active():
    global proc_speak
    # terminate all speak process are currently running
    for p in proc_speak:
        p.terminate()
        del proc_speak[0]
    # delete all remain mp3 file
    for i in range(5):
        if os.path.isfile(f"temp{i}.mp3"):
            os.remove(f"temp{i}.mp3")
    speak_thread('See you again')

def limit_time(seconds):
    time.sleep(seconds)

# active mode
def main():
    #back to sleep mode after 5 seconds
    p = multiprocessing.Process(target=limit_time, args=[5])
    p.start()

    while True:
        try:


            print('main() running...')
            command = speech2text().lower()

            if ('play music' in command):
                play_music()
            elif ('answer question' in command):
                chat_bot()
            elif ('google search' in command):
                google_search()
            # if you want it to stop speaking and return to sleep mode
            elif ('stop speaking' in command):
                stop_active()
                print('Return to sleep mode!')
                break

            # after idle
            if(not p.is_alive()):
                print('Return to sleep mode!')
                break
        except Exception as e:
            print(f"Error occurred in main()! Error name: {e}")


# sleep mode
def run():

    while True:
        try:
            print('run() running...')
            query = speech2text().lower()
            if ('google' in query):  # activate word
                speak_thread('Hello user')
                main()
            elif ('goodbye' in query):  # turn off word
                speak_thread('See you soon')
                exit()
        except Exception as e:
            print(f"Error occurred in run()! Error name: {e}")


# this will only run when the module is used directly, not run when being imported to another module
if __name__ == '__main__':

    # OpenAI API initialisation
    openai.organization = "inset-key-here"
    openai.api_key = "inset-key-here"
    # api_key = "inset-key" # for whisper api speechreconigtion
    proc_speak = []

    run()
