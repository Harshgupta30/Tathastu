import pyttsx3
import speech_recognition as sr
from datetime import date
import time
import webbrowser
from datetime import datetime
from pynput.keyboard import Key, Controller
import pyautogui
import sys
import os
from os import listdir
from os.path import isfile, join
import smtplib
import wikipedia
import app
from threading import Thread
import Gesture_Controller
import random
import json
import pickle
import numpy as np
from datetime import datetime

import nltk
from nltk.stem import WordNetLemmatizer

from tensorflow.keras.models import load_model

lemmatizer = WordNetLemmatizer()

intents = json.loads(open('intents.json').read())

words = pickle.load(open('words.pkl','rb'))
classes = pickle.load(open('classes.pkl','rb'))

#----------------model fetching----------------
model = load_model('chatbotmodel.h5')

#----------------cleaning------------------------
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words

#---------------bagging of words------------------------
def bag_of_words(sentence):
    sentence_word = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_word:
        for i, word in enumerate(words):
            if(word == w):
                bag[i] = 1
    return np.array(bag)

#-----------------predicting----------------
def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent':classes[r[0]],'probability': str(r[1])})
    return return_list

#------------------bot response --------------------------------
def get_response(intents_list, intents_json):
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result
print("bot activated")


# -------------Object Initialization---------------
today = date.today()
r = sr.Recognizer()
keyboard = Controller()
engine = pyttsx3.init('sapi5')
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# ----------------Variables------------------------
file_exp_status = False
files =[]
path = ''
is_awake = True  #Bot status

# ------------------Functions----------------------
def reply(audio):
    app.ChatBot.addAppMsg(audio)

    print(audio)
    engine.say(audio)
    engine.runAndWait()


def wish():
    hour = int(datetime.now().hour)
    # print(hour)
    if hour>=0 and hour<12:
        reply("Good Morning!")
    elif hour>=12 and hour<18:
        reply("Good Afternoon!")   
    else:
        reply("Good Evening!")  
        
    reply("I am john, how may I help you?")

# Set Microphone parameters
with sr.Microphone() as source:
        r.energy_threshold = 500 
        r.dynamic_energy_threshold = False

# Audio to String
def record_audio():
    with sr.Microphone() as source:
        r.pause_threshold = 0.8
        voice_data = ''
        audio = r.listen(source, phrase_time_limit=5)

        try:
            voice_data = r.recognize_google(audio)
        except sr.RequestError:
            reply('Sorry my Service is down. Plz check your Internet connection')
        except sr.UnknownValueError:
            print('cant recognize')
            pass
        return voice_data.lower()


# Executes Commands (input: string)
def respond(voice_data):
    global file_exp_status, files, is_awake, path
    print(voice_data)
    voice_data.replace('john','')
    app.eel.addUserMsg(voice_data)
    message = voice_data
    print("inside response",message)
    ints = predict_class(message)
    res = get_response(ints, intents)
    if(res=="Activating Gesture Controle"):
        if Gesture_Controller.GestureController.gc_mode:
            reply('Gesture recognition is already active')
            print('Gesture recognition is already active')
        else:
            print(res+"...")
            gc = Gesture_Controller.GestureController()
            t = Thread(target = gc.start)
            t.start()
            reply("Launch Sucessfully")
            print("Launch Sucessfully")
    elif(res=="Deactivateing Gesture Controle"):
        if Gesture_Controller.GestureController.gc_mode:
            print(res+"...")
            Gesture_Controller.GestureController.gc_mode = 0
            reply("Gesture Control is deactivated")
            print("Gesture Control is deactivated")
        else:
            reply("Gesture Controller is not active")
            print("Gesture Controller is not active")
    elif(res=='Copied to clipboard'):
        time.sleep(5)
        x, y = pyautogui.position()
        pyautogui.move(5, 5)
        pyautogui.hotkey("ctrl", "c")
        print(res)
        reply(res)
    elif(res=='Pasted'):
        time.sleep(5)
        x, y = pyautogui.position()
        pyautogui.move(5, 5)
        pyautogui.hotkey("ctrl", "v")
        print(res)
        reply(res)
    elif(res=='Searching'):
        print("res"+"..")
        url = f"https://www.google.com/search?q={message}"
        print("Here is what I found")
        reply("Here is what I found")
        webbrowser.open_new_tab(url)
    else:
        print(res)
        reply(res)
    # global file_exp_status, files, is_awake, path
    # print(voice_data)
    # voice_data.replace('darwin','')
    # app.eel.addUserMsg(voice_data)

    # if is_awake==False:
    #     if 'wake up' in voice_data:
    #         is_awake = True
    #         wish()

    # # STATIC CONTROLS
    # elif 'hello' in voice_data:
    #     wish()

    # elif 'what is your name' in voice_data:
    #     reply('My name is darwin!')

    # elif 'date' in voice_data:
    #     reply(today.strftime("%B %d, %Y"))

    # elif 'time' in voice_data:
    #     reply(str(datetime.datetime.now()).split(" ")[1].split('.')[0])

    # elif 'search' in voice_data:
    #     reply('Searching for ' + voice_data.split('search')[1])
    #     url = 'https://google.com/search?q=' + voice_data.split('search')[1]
    #     try:
    #         webbrowser.get().open(url)
    #         reply('This is what I found Sir')
    #     except:
    #         reply('Please check your Internet')

    # elif 'location' in voice_data:
    #     reply('Which place are you looking for ?')
    #     temp_audio = record_audio()
    #     app.eel.addUserMsg(temp_audio)
    #     reply('Locating...')
    #     url = 'https://google.nl/maps/place/' + temp_audio + '/&amp;'
    #     try:
    #         webbrowser.get().open(url)
    #         reply('This is what I found Sir')
    #     except:
    #         reply('Please check your Internet')

    # elif ('bye' in voice_data) or ('by' in voice_data):
    #     reply("Good bye Sir! Have a nice day.")
    #     is_awake = False

    # elif ('exit' in voice_data) or ('terminate' in voice_data):
    #     import Gesture_Controller
    #     if Gesture_Controller.GestureController.gc_mode:
    #         Gesture_Controller.GestureController.gc_mode = 0
    #     app.ChatBot.close()
    #     #sys.exit() always raises SystemExit, Handle it in main loop
    #     sys.exit()
        
    
    # # DYNAMIC CONTROLS
    # elif 'launch gesture recognition' in voice_data:
    #     import Gesture_Controller
    #     if Gesture_Controller.GestureController.gc_mode:
    #         reply('Gesture recognition is already active')
    #     else:
    #         gc = Gesture_Controller.GestureController()
    #         t = Thread(target = gc.start)
    #         t.start()
    #         reply('Launched Successfully')

    # elif ('stop gesture recognition' in voice_data) or ('top gesture recognition' in voice_data):
    #     import Gesture_Controller
    #     if Gesture_Controller.GestureController.gc_mode:
    #         Gesture_Controller.GestureController.gc_mode = 0
    #         reply('Gesture recognition stopped')
    #     else:
    #         reply('Gesture recognition is already inactive')
        
    # elif 'copy' in voice_data:
    #     with keyboard.pressed(Key.ctrl):
    #         keyboard.press('c')
    #         keyboard.release('c')
    #     reply('Copied')
          
    # elif 'page' in voice_data or 'pest'  in voice_data or 'paste' in voice_data:
    #     with keyboard.pressed(Key.ctrl):
    #         keyboard.press('v')
    #         keyboard.release('v')
    #     reply('Pasted')
        
    # # File Navigation (Default Folder set to C://)
    # elif 'list' in voice_data:
    #     counter = 0
    #     path = 'C://'
    #     files = listdir(path)
    #     filestr = ""
    #     for f in files:
    #         counter+=1
    #         print(str(counter) + ':  ' + f)
    #         filestr += str(counter) + ':  ' + f + '<br>'
    #     file_exp_status = True
    #     reply('These are the files in your root directory')
    #     app.ChatBot.addAppMsg(filestr)
        
    # elif file_exp_status == True:
    #     counter = 0   
    #     if 'open' in voice_data:
    #         if isfile(join(path,files[int(voice_data.split(' ')[-1])-1])):
    #             os.startfile(path + files[int(voice_data.split(' ')[-1])-1])
    #             file_exp_status = False
    #         else:
    #             try:
    #                 path = path + files[int(voice_data.split(' ')[-1])-1] + '//'
    #                 files = listdir(path)
    #                 filestr = ""
    #                 for f in files:
    #                     counter+=1
    #                     filestr += str(counter) + ':  ' + f + '<br>'
    #                     print(str(counter) + ':  ' + f)
    #                 reply('Opened Successfully')
    #                 app.ChatBot.addAppMsg(filestr)
                    
    #             except:
    #                 reply('You do not have permission to access this folder')
                                    
    #     if 'back' in voice_data:
    #         filestr = ""
    #         if path == 'C://':
    #             reply('Sorry, this is the root directory')
    #         else:
    #             a = path.split('//')[:-2]
    #             path = '//'.join(a)
    #             path += '//'
    #             files = listdir(path)
    #             for f in files:
    #                 counter+=1
    #                 filestr += str(counter) + ':  ' + f + '<br>'
    #                 print(str(counter) + ':  ' + f)
    #             reply('ok')
    #             app.ChatBot.addAppMsg(filestr)
                   
    # else: 
    #     reply('I am not functioned to do this !')

# ------------------Driver Code--------------------

t1 = Thread(target = app.ChatBot.start)
t1.start()

# Lock main thread until Chatbot has started
while not app.ChatBot.started:
    time.sleep(0.5)

wish()
voice_data = None
while True:
    if app.ChatBot.isUserInput():
        #take input from GUI
        voice_data = app.ChatBot.popUserInput()
    else:
        #take input from Voice
        voice_data = record_audio()
    print("inside main",voice_data)
    #process voice_data
    if 'john' in voice_data:
        try:
            #Handle sys.exit()
            respond(voice_data)
        except SystemExit:
            reply("Exit Successfull")
            break
        except:
            #some other exception got raised
            print("EXCEPTION raised while closing.") 
            break