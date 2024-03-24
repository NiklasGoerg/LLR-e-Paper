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

import time
import spidev
import threading

import asyncio
import websockets


class WebSocketClient:
    def __init__(self, uri):
        self.uri = uri
        self.websocket = None

    async def connect(self):
        self.websocket = await websockets.connect(self.uri)
        print("Verbunden mit dem WebSocket-Server.")
        await self.receive_loop()

    async def send_message(self, message):
        if self.websocket:
            await self.websocket.send(message)

    async def receive_loop(self):
        try:
            while True:
                message = await self.websocket.recv()
                print("Nachricht vom Server:", message)
                handleMessage(message)
                
        except websockets.exceptions.ConnectionClosed:
            print("Verbindung zum Server wurde geschlossen.")

    async def close(self):
        if self.websocket:
            await self.websocket.close()

# Funktion zum Beenden des Programms
async def shutdown(client):
    print("Programm wird beendet...")
    await client.close()
    asyncio.get_event_loop().stop()


# Beispielverwendung
uri = "ws://192.168.1.100:3000"
client = WebSocketClient(uri)

async def main():
    await client.connect()

# We only have SPI bus 0 available to us on the Pi
bus = 0

#Device is the chip select pin. Set to 0 or 1, depending on the connections
led_matrix = 1

# Enable SPI
spi = spidev.SpiDev()

spi.open(bus, led_matrix)

# Set SPI speed and mode
spi.max_speed_hz = 500000
spi.mode = 0


logging.basicConfig(level=logging.DEBUG)

# consts
button1_pin = 26
button2_pin = 13
button3_pin = 6
button4_pin = 5

switch_pin = 12
led_pin = 16


# vars
button1IsPressed = False
button2IsPressed = False
button3IsPressed = False
button4IsPressed = False

isInAnonymMode = False

button1Text = 'Frage'
button2Text = 'Hilfe'
button3Text = 'Zu schnell'
button4Text = 'Zu langsam'

assignmentText = 'Thema: Das Leben im alten Ägypten'

# functions
def handleMessage(message):
    index = message.find(':')
    typeOfMessage = ""
    contentOfMessage = ""
    if index != -1:
        typeOfMessage = message[:index]
        contentOfMessage = message[index + 1:]
    if typeOfMessage == "task":
        writeText(contentOfMessage)
    else:
        writeButtonText(typeOfMessage, contentOfMessage)

def endProgramm():
    logging.info("Clear...")
    clearLEDMatrix()
    epd.init()
    epd.Clear()

    logging.info("Goto Sleep...")
    epd.sleep()
    uri = "ws://192.168.1.100:3000"  # Ersetzen Sie dies durch die tatsächliche URI des WebSocket-Servers
    client = WebSocketClient(uri)
    shutdown(client)

def switchChanged(*channel):
    global isInAnonymMode
    if GPIO.input(switch_pin):  
        GPIO.output(led_pin, GPIO.HIGH)
        isInAnonymMode = True
        print('anonym on')
    else:
        GPIO.output(led_pin, GPIO.LOW)
        isInAnonymMode = False
        clearLEDMatrix()
        print('anonym off')

def clearLEDMatrix():
    clear = [0x00, 0x00, 0x00]
    spi.xfer2(clear)

def setLEDMatrixColor(button):
    button1Color = [0xff, 0xff, 0xff]
    button2Color = [0xff, 0xff, 0x00, 0xff, 0x00, 0xff]
    button3Color = [0xff, 0xff, 0xff, 0x00, 0xff, 0xff]
    button4Color = [0xff, 0xff, 0xff, 0xff, 0x00, 0xff]
    clearLEDMatrix()
    time.sleep(0.1)
    if (button == 'button1'):
        spi.xfer2(button1Color)
    elif (button == 'button2'):
        spi.xfer2(button2Color)
    elif (button == 'button3'):
        spi.xfer2(button3Color)
    elif (button == 'button4'):
        spi.xfer2(button4Color)
    

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
    epd.display_Partial(epd.getbuffer(Himage),0, 0, epd.width, epd.height)
    

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
    epd.display_Partial(epd.getbuffer(Himage),0, 0, epd.width, epd.height)

def button1Pressed(*channel):
    global button1IsPressed
    global button1Text
    global button1Color
    global client
    print('1 was pressed', channel, button1IsPressed)
    if GPIO.input(button1_pin):  # Überprüfen, ob der Taster losgelassen wurde
        return
        
    epd.display_Partial(epd.getbuffer(Himage),0, 0, epd.width, epd.height)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
        
    if (button1IsPressed):
        writeButtonText('button1', button1Text)
        clearLEDMatrix()
        loop.run_until_complete(client.send_message(button1Text + ":cancel"))
        button1IsPressed = False
    else:
        draw.rectangle((10, 400, 195, 480), outline = 0, fill = 0)
        draw.text((20, 420), button1Text, font = font24, fill = 255)
        if isInAnonymMode == False:
            setLEDMatrixColor('button1')
        loop.run_until_complete(client.send_message(button1Text + ":submit"))
        button1IsPressed = True
        
    epd.display_Partial(epd.getbuffer(Himage),0, 0, epd.width, epd.height)
        
def button2Pressed(*channel):
    global button2IsPressed
    global button2Text
    global button2Color
    global client
    print('2 was pressed')
    if GPIO.input(button2_pin):  # Überprüfen, ob der Taster losgelassen wurde
        return
        
    epd.display_Partial(epd.getbuffer(Himage),0, 0, epd.width, epd.height)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    if button2IsPressed:
        writeButtonText('button2', button2Text)
        clearLEDMatrix()
        loop.run_until_complete(client.send_message(button2Text + ":cancel"))
        button2IsPressed = False
    else:
        draw.rectangle((205, 400, 395, 480), outline=0, fill=0)
        draw.text((215, 420), button2Text, font=font24, fill=255)
        if isInAnonymMode == False:
            setLEDMatrixColor('button2')
        loop.run_until_complete(client.send_message(button2Text + ":submit"))
        button2IsPressed = True
        
    epd.display_Partial(epd.getbuffer(Himage),0, 0, epd.width, epd.height)

def button3Pressed(*channel):
    global button3IsPressed
    global button3Text
    global button3Color
    global client
    print('3 was pressed')
    if GPIO.input(button3_pin):  # Überprüfen, ob der Taster losgelassen wurde
        return
        
    epd.display_Partial(epd.getbuffer(Himage),0, 0, epd.width, epd.height)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    if button3IsPressed:
        writeButtonText('button3', button3Text)
        clearLEDMatrix()
        loop.run_until_complete(client.send_message(button3Text + ":cancel"))
        button3IsPressed = False
    else:
        draw.rectangle((405, 400, 595, 480), outline=0, fill=0)
        draw.text((415, 420), button3Text, font=font24, fill=255)
        if isInAnonymMode == False:
            setLEDMatrixColor('button3')
        loop.run_until_complete(client.send_message(button3Text + ":submit"))
        button3IsPressed = True
        
    epd.display_Partial(epd.getbuffer(Himage),0, 0, epd.width, epd.height)

def button4Pressed(*channel):
    global button4IsPressed
    global button4Text
    global button4Color
    global client
    print('4 was pressed')
    if GPIO.input(button4_pin):  # Überprüfen, ob der Taster losgelassen wurde
        return
        
    epd.display_Partial(epd.getbuffer(Himage),0, 0, epd.width, epd.height)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    if button4IsPressed:
        writeButtonText('button4', button4Text)
        clearLEDMatrix()
        loop.run_until_complete(client.send_message(button4Text + ":cancel"))
        button4IsPressed = False
    else:
        draw.rectangle((605, 400, 790, 480), outline=0, fill=0)
        draw.text((615, 420), button4Text, font=font24, fill=255)
        if isInAnonymMode == False:
            setLEDMatrixColor('button4')
        loop.run_until_complete(client.send_message(button4Text + ":submit"))
        button4IsPressed = True
    epd.display_Partial(epd.getbuffer(Himage),0, 0, epd.width, epd.height)
        
def newAssignment():
    writeButtonText('button1', 'Hilfe')
    writeButtonText('button2', 'Dringende Hilfe')
    writeButtonText('button3', 'Andere Frage')
    writeButtonText('button4', 'Ich bin fertig')
    writeText('Lies das Kapitel über das Leben im alten Ägypten in deinem Geschichtsbuch. Beantworte dann die folgenden Fragen: Welche Rolle spielte der Nil im Leben der alten Ägypter? Wie sah die Gesellschaftsstruktur im alten Ägypten aus? Nenne zwei bedeutende Errungenschaften der alten Ägypter. Warum waren die Pyramiden wichtig für die alten Ägypter?')

    epd.display_Partial(epd.getbuffer(Himage),0, 0, epd.width, epd.height)
        
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
    epd.display_Partial(epd.getbuffer(Himage),0, 0, epd.width, epd.height)
    
    
    GPIO.setup(button1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(button2_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(button3_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(button4_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    GPIO.setup(switch_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(led_pin, GPIO.OUT)

    # Event-Handler für den Button
    GPIO.add_event_detect(button1_pin, GPIO.FALLING, callback=button1Pressed, bouncetime=1000)
    GPIO.add_event_detect(button2_pin, GPIO.FALLING, callback=button2Pressed, bouncetime=1000)
    GPIO.add_event_detect(button3_pin, GPIO.FALLING, callback=button3Pressed, bouncetime=1000)
    GPIO.add_event_detect(button4_pin, GPIO.FALLING, callback=button4Pressed, bouncetime=1000)
    GPIO.add_event_detect(switch_pin, GPIO.BOTH, callback=switchChanged, bouncetime=500)
    
    def key_listener():
        while True:
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
                    endProgramm()
            except KeyboardInterrupt:
                print("Something went wrong")

    # Starte den Tastatur-Hintergrund-Thread
    keyboard_thread = threading.Thread(target=key_listener)
    keyboard_thread.daemon = True  # Damit das Programm beendet wird, wenn das Hauptprogramm endet
    keyboard_thread.start()
 
    
    # Starten Sie die asynchrone Ausführung des Hauptcodes
    asyncio.run(main())

    
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd7in5_V2.epdconfig.module_exit(cleanup=True)
    exit()


