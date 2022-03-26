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
import json

current_channel = 0

json_string = """
{ 
    "radio": [ 
        "mplayer -playlist http://www.ndr.de/resources/metadaten/audio/m3u/ndrinfo.m3u", 
        "mplayer https://st01.dlf.de/dlf/01/128/mp3/stream.mp3",
        "mplayer https://wdr-wdr5-live.icecastssl.wdr.de/wdr/wdr5/live/mp3/128/stream.mp3"
    ],
    "amixer": "Master",
    "current": 0,
    "volume": 60
} 
"""
data = json.loads(json_string)

# Clamp value btw 0 and 100
clamp = lambda n: max(min(100, n), 0)

def shutdownRadio(dummy):
    print("Shutdown")
#    os.system("sudo halt")

def VolUp():
    applyVolume(data["volume"] + 4)

def VolDown():
    applyVolume(data["volume"] - 4)

def applyVolume(volume):
    data["volume"] = clamp(volume)
    subprocess.Popen(shlex.split("amixer sset '"+data["amixer"]+"' "+str(data["volume"])+"%"))

def SetRadioChannel():
    os.system("pkill mplayer");
    chan = data["current"]
    args = shlex.split(data["radio"][chan]+" &")
    my_env = os.environ.copy()
    my_env["MPLAYER_VERBOSE"] = "-1"
    subprocess.Popen(args, env=my_env)

def SetRadioChannelIndex(c):
    data["current"] = c
    SetRadioChannel()

def SetRadioChannelUp():
    data["current"] = ( data["current"] + 1 ) % len(data["radio"])
    SetRadioChannel()
    
def SetRadioChannelDown():
    data["current"] = ( data["current"] - 1 + len(data["radio"])) % len(data["radio"])
    SetRadioChannel()

def cleanup():
    os.system("pkill mplayer");
    curses.nocbreak()
    # screen.keypad(0)
    curses.echo()
    curses.endwin()
    sys.exit()

def main():
    SetRadioChannelIndex(data["current"])

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
            VolUp()
        if c == 121: # 'y'
            VolDown()
        if c == 48: # '0'
            SetRadioChannelIndex(0)
        if c == 49: # '1'
            SetRadioChannelIndex(1)

wrapper(main())

