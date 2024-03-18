#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd7in5_V2
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

import keyboard
import RPi.GPIO as GPIO

logging.basicConfig(level=logging.DEBUG)

# consts
button1_pin = 26

# vars
button1IsPressed = False
button2IsPressed = False
button3IsPressed = False
button4IsPressed = False

button1Text = 'Frage'
button2Text = 'Hilfe'
button3Text = 'Zu schnell'
button4Text = 'Zu langsam'

assignmentText = 'Thema: Das Leben im alten Ägypten'

# functions
def breakString(text):
    words = text.split()  # Zerlegen des Textes in Wörter
    lines = []  # Liste für die resultierenden Zeilen
    
    current_line = ''  # Aktuelle Zeile

    for word in words:
        if len(current_line + word) <= 68:
            current_line += word + ' '  # Wort zur aktuellen Zeile hinzufügen
        else:
            lines.append(current_line.strip())  # Aktuelle Zeile zur Liste hinzufügen (ohne überflüssige Leerzeichen)
            current_line = word + ' '  # Neuen Satz beginnen
    
    # Rest der aktuellen Zeile hinzufügen
    if current_line:
        lines.append(current_line.strip())
    
    return lines

def writeText(text):
    draw.rectangle((0, 0, 800, 300), fill=255)
    lines = breakString(text)
    y = 40
    for line in lines:
        draw.text((10, y), line, font=font24, fill=0)
        y += 24  # 24 Pixel Abstand zwischen den Zeilen
    

def writeButtonText(button, text):
    global button1Text
    global button2Text
    global button3Text
    global button4Text
    if (button == 'button1'):
        button1Text = text
        draw.rectangle((10, 400, 195, 480), outline = 0, fill = 255)
        draw.text((20, 420), text, font = font24, fill = 0)
    elif (button == 'button2'):
        button2Text = text
        draw.rectangle((205, 400, 395, 480), outline=0, fill= 255)
        draw.text((215, 420), text, font=font24, fill=0)
    elif (button == 'button3'):
        button3Text = text
        draw.rectangle((405, 400, 595, 480), outline=0, fill= 255)
        draw.text((415, 420), text, font=font24, fill=0)
    elif (button == 'button4'):
        button4Text = text
        draw.rectangle((605, 400, 790, 480), outline=0, fill= 255)
        draw.text((615, 420), text, font=font24, fill= 0)

def button1Pressed(*test):
    global button1IsPressed
    global button1Text
    print('1 was pressed', test)
        
    epd.display_Partial(epd.getbuffer(Himage),0, 0, epd.width, epd.height)
    
    if (button1IsPressed):
        writeButtonText('button1', button1Text)
        button1IsPressed = False
    else:
        draw.rectangle((10, 400, 195, 480), outline = 0, fill = 0)
        draw.text((20, 420), button1Text, font = font24, fill = 255)
        button1IsPressed = True
        
def button2Pressed():
    global button2IsPressed
    global button2Text
    global button3Text
    print('2 was pressed')
    
    if button2IsPressed:
        writeButtonText('button2', button2Text)
        button2IsPressed = False
    else:
        draw.rectangle((205, 400, 395, 480), outline=0, fill=0)
        draw.text((215, 420), button2Text, font=font24, fill=255)
        button2IsPressed = True

def button3Pressed():
    global button3IsPressed
    global button3Text
    print('3 was pressed')
    
    if button3IsPressed:
        writeButtonText('button3', button3Text)
        button3IsPressed = False
    else:
        draw.rectangle((405, 400, 595, 480), outline=0, fill=0)
        draw.text((415, 420), button3Text, font=font24, fill=255)
        button3IsPressed = True

def button4Pressed():
    global button4IsPressed
    global button4Text
    print('4 was pressed')
    
    if button4IsPressed:
        writeButtonText('button4', button4Text)
        button4IsPressed = False
    else:
        draw.rectangle((605, 400, 790, 480), outline=0, fill=0)
        draw.text((615, 420), button4Text, font=font24, fill=255)
        button4IsPressed = True
        
def newAssignment():
    writeButtonText('button1', 'Hilfe')
    writeButtonText('button2', 'Dringende Hilfe')
    writeButtonText('button3', 'Andere Frage')
    writeButtonText('button4', 'Ich bin fertig')
    writeText('Lies das Kapitel über das Leben im alten Ägypten in deinem Geschichtsbuch. Beantworte dann die folgenden Fragen: Welche Rolle spielte der Nil im Leben der alten Ägypter? Wie sah die Gesellschaftsstruktur im alten Ägypten aus? Nenne zwei bedeutende Errungenschaften der alten Ägypter. Warum waren die Pyramiden wichtig für die alten Ägypter?')

        
try:
    logging.info("epd7in5_V2 Demo")
    epd = epd7in5_V2.EPD()
    
    logging.info("init and Clear")
    epd.init()
    epd.Clear()

    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)

    # Drawing on the Horizontal image
    logging.info("Drawing on the Horizontal image...")
    epd.init_fast()
    Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(Himage)

    # partial update
    logging.info("5.show time")
    epd.init_part()
    
    # Assignment Text
    writeText(assignmentText)
    # Button 1
    draw.rectangle((10, 400, 195, 480), outline = 0)
    draw.text((20, 420), button1Text, font = font24, fill = 0)
    # Button 2
    draw.rectangle((205, 400, 395, 480), outline = 0)
    draw.text((215, 420), button2Text, font = font24, fill = 0)
    # Button 3
    draw.rectangle((405, 400, 595, 480), outline = 0)
    draw.text((415, 420), button3Text, font = font24, fill = 0)
    # Button 4
    draw.rectangle((605, 400, 790, 480), outline = 0)
    draw.text((615, 420), button4Text, font = font24, fill = 0)
    
    
    GPIO.setup(button1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Event-Handler für den Button
    GPIO.add_event_detect(button1_pin, GPIO.FALLING, callback=button1Pressed, bouncetime=1000)
    
    while (True):
        epd.display_Partial(epd.getbuffer(Himage),0, 0, epd.width, epd.height)
        try:
            key_pressed = keyboard.read_event(suppress=True).name
            print(key_pressed)
            if key_pressed == '1':
                button1Pressed()
            elif key_pressed == '2':
                button2Pressed()
            elif key_pressed == '3':
                button3Pressed()
            elif key_pressed == '4':
                button4Pressed()
            elif key_pressed == 'n':
                newAssignment()
            elif key_pressed == 'x':
                break
        except KeyboardInterrupt:
            print("smth is wrong")
            
    logging.info("Clear...")
    epd.init()
    epd.Clear()

    logging.info("Goto Sleep...")
    epd.sleep()
    
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd7in5_V2.epdconfig.module_exit(cleanup=True)
    exit()


