from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
import speech_recognition as sr
import os
import time
import playsound
import pyttsx3
import pytz
import subprocess

MONTHS=["january","february","march","april","may","june","july","august","september","october","november","december"]
DAYS = ["monday","tuesday","wednesday","thursday","friday"]
DAYS_EXTENSION=["st","rd","th","nd"]


def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:#using microphone for input
        audio = r.listen(source)#using speech recognizer to listen to microphone
        said = ""
        try:
            said = r.recognize_google(audio)#using google api to recognize the speech
            print(said)#printing the speech in text form
        except Exception as e:
            print("Exception:"+str(e))
    return said.lower()

#text = get_audio()


#if "hello" in text:
 #   speak("hello how are u??")
#if "what is your name" in text:
#    speak("I am Jarvis!!!")



def authenticate_google_calendar():

    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    return service

def get_events(day,service):
    #converting to utc time stamp
       date = datetime.datetime.combine(day, datetime.datetime.min.time())
       end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
       utc = pytz.UTC
       date = date.astimezone(utc)
       end_date = end_date.astimezone(utc)

       events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(),timeMax=end_date.isoformat(),
                                         singleEvents=True,
                                        orderBy='startTime').execute()
       events = events_result.get('items', [])

       if not events:
         speak('No upcoming events found.')
       else:
         speak(f"You have{len(events)}events on this day.")

         for event in events:
          start = event['start'].get('dateTime', event['start'].get('date'))
          print(start, event['summary'])
          start_time = str(start.split("T")[1].split("-")[0])
          if int(start_time.split(":")[0]<12):
              start_time+="am"
          else:
              start_time = str(start.split("T")[1].split("-")[0]-12)+start_time.split(":")[1]
              start_time+="pm"
          speak(event["summary"] + "at" + start_time)

def get_date(text):
    text = text.lower()
    today = datetime.date.today()

    if text.count("today")>0:
        return today

    day = -1
    day_of_week = -1
    month = -1
    year = today.year

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
            for ext in DAYS_EXTENSION:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[:found])
                    except:
                        pass

    if month<today.month and month!=-1:
        year+=1 #when in november what do we have on jan 3rd
    if day<today.day and month==-1 and day!=-1:
        month+=1 #say today is 6th november when i say whats on 1st i am refering to next month
    if month==-1 and day==-1 and day_of_week!=-1:
        current_day_of_week = today.weekday()#day of week(0-6)range
        dif = day_of_week - current_day_of_week
        #what do i have on tuesday
        if dif < 0:#if the day is tuesday and user says monday
            dif+=7
            if text.count("next")>=1:
                dif+=7
        return today+datetime.timedelta(dif)
    if month==-1 and day==-1:
        return None
    return datetime.date(month=month,day=day,year=year)

def note(text):
    date = datetime.datetime.now()#date at the moment
    file_name = str(date).replace(":","-") + "-note.txt"
    with open(file_name,"w") as f:
        f.write(text)
    iexplore = "C:\Program Files\Internet Explorer\iexplore.exe"
    subprocess.Popen(["notepad.exe",file_name])
#note("sahil is the best")

WAKE="stark"
service = authenticate_google_calendar()
print("Start")
#get_events(2,service)
while True:
    text = get_audio()
    #print(get_date(text))
    if text.count(WAKE)>0:
        speak("At your service sir")
        text = get_audio()
        CALENDAR_STRS=["what do i have","do i have plans","am i busy"]
        for phrase in CALENDAR_STRS:
            if phrase in text.lower():
                date = get_date(text)
                if date:
                    get_events(date,service)
                else:
                    speak("Sorry I didn't get you")


        NOTE_STRS = ["make a note","write this down","remember this"]

        for phrase in NOTE_STRS:
            if phrase in text:
                speak("What would you like me to write down??")
                note_txt = get_audio()
                note(note_txt)
                speak("I have made of this..")