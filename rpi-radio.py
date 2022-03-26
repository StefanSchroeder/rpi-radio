# Better Raspberry Pi Radio
# (C) 2017 M4rc3lv
# Additions and updates by Stefan Schroeder, 2019
# import RPi.GPIO as GPIO
import os
import csv
import sys
import time, shlex
import subprocess
import curses
from curses import wrapper

# GPIO.setmode(GPIO.BOARD)
CurChannel = 0
current_channel = 0
ChannelURL = []
ChannelName = []
Last = ""

with open('radio.csv') as csvfile:
    channelreader = csv.reader(csvfile)
    for row in channelreader:
        if row[0].startswith("#"): continue 
        ChannelName.append(row[0])
        ChannelURL.append(row[1])

for s in ChannelName:
    print(str(s) + "\n")

PIN_A = 5 # CLK Geel
PIN_B = 7 # CLK Oranje

PIN_ROTARY_BUTTON=32
PIN_SHUTOWN_SWITCH=37
VOL_UP = 38
PIN_VOL_DOWN = 40
volume = 50

Prev=0

def shutdownRadio(dummy):
    print("Shutdown")
    os.system("sudo halt")

def Rot(channel):
    global Last
    global Prev
    
    #level = GPIO.input(channel)
    level= 5
    Last = str(channel)+":"+str(level)
    if Last=="5:0" and Prev=="7:0": VolUp(1)
    if Last=="7:0" and Prev=="5:0": VolDown(1)
    Prev = Last

def VolUp(dummy):
    global volume
    volume = volume + 4
    if volume>=100: volume = 100    
    subprocess.Popen(shlex.split("amixer sset 'PCM' "+str(volume)+"%"))
    file = open("lastvolume.txt","w")
    file.write(str(volume)+"\n")
    file.close()

def VolDown(dummy):
    global volume
    volume = volume - 4
    if volume<=0: volume = 0    
    subprocess.Popen(shlex.split("amixer sset 'PCM' "+str(volume)+"%"))
    file = open("lastvolume.txt","w")
    file.write(str(volume)+"\n")
    file.close()

def SetRadioChannel(chan):
    os.system("pkill mplayer");
    os.system('echo "'+ChannelName[chan]+'" | festival --tts')
    args = shlex.split("mplayer "+ChannelURL[chan]+" &")
    my_env = os.environ.copy()
    my_env["MPLAYER_VERBOSE"] = "-1"
    subprocess.Popen(args, env=my_env)

def SetRadioChannelIndex(c):
    global current_channel
    current_channel = c
    SetRadioChannel(current_channel)

def SetRadioChannelUp():
    global current_channel
    current_channel = ( current_channel + 1 ) % len(ChannelName)
    SetRadioChannel(current_channel)
    
def SetRadioChannelDown():
    global current_channel
    current_channel = ( current_channel - 1 ) 
    if current_channel < 0: current_channel += len(ChannelName)
    SetRadioChannel(current_channel)

def cleanup():
    os.system("pkill mplayer");
    GPIO.cleanup()        
    curses.nocbreak()
    # screen.keypad(0)
    curses.echo()
    curses.endwin()
    sys.exit()

def RotButton(dummy):
    SetRadioChannelUp()

def main():
    try:
        try:
            file = open("lastvolume.txt","r")
            volume = int(file.read())
            subprocess.Popen(shlex.split("amixer sset 'PCM' "+str(volume)+"%"))
            file.close()
        except: pass

        file = open("LastChannel.txt","r")
        CurChannel = int(file.read())
        file.close()
    except:
        CurChannel=0

        SetRadioChannel(0)

        GPIO.setup(VOL_UP, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(VOL_UP, GPIO.RISING, callback=VolUp, bouncetime=150)

        GPIO.setup(PIN_VOL_DOWN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(PIN_VOL_DOWN, GPIO.RISING, callback=VolDown, bouncetime=150)
        
        GPIO.setup(PIN_A, GPIO.IN) # pull_up_down=GPIO.PUD_UP)
        GPIO.setup(PIN_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(PIN_A, GPIO.FALLING, callback=Rot)
        GPIO.add_event_detect(PIN_B, GPIO.FALLING, callback=Rot)        

        GPIO.setup(PIN_SHUTOWN_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(PIN_SHUTOWN_SWITCH, GPIO.FALLING, callback=shutdownRadio, bouncetime=200)

        GPIO.setup(PIN_ROTARY_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(PIN_ROTARY_BUTTON, GPIO.FALLING, callback=RotButton, bouncetime=250)


        damn = curses.initscr()
        damn.nodelay(1)
        while True:
            c = damn.getch()
            if c > 1:
                print("<" + str(c) + ">")
            if c == 122: # 'z'
                cleanup()
            if c == 109: # 'm'
                SetRadioChannelUp()
            if c == 110: # 'n'
                SetRadioChannelDown()
            if c == 120: # 'x'
                VolUp(1)
            if c == 121: # 'y'
                VolDown(1)
            if c == 49: # '1'
                SetRadioChannelIndex(1)
    finally:
        GPIO.cleanup()        

wrapper(main())
