from machine import Pin, freq
from neopixel import NeoPixel
from sys import platform

import time 
import math
import gc

numberOfLeds = 16
ledPin = Pin(4, Pin.OUT)  # pin 4 is also called D2
leds = NeoPixel(ledPin, numberOfLeds) 

# HSV color values to RGB used by the LEDs. See https://en.wikipedia.org/wiki/HSL_and_HSV
def toRgb(h, s, v):
    h = float(h)
    s = float(s)
    v = float(v)
    h60 = h / 60.0
    h60f = math.floor(h60)
    hi = int(h60f) % 6
    f = h60 - h60f
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    r, g, b = 0, 0, 0
    if hi == 0: r, g, b = v, t, p
    elif hi == 1: r, g, b = q, v, p
    elif hi == 2: r, g, b = p, v, t
    elif hi == 3: r, g, b = p, q, v
    elif hi == 4: r, g, b = t, p, v
    elif hi == 5: r, g, b = v, p, q
    r, g, b = int(r * 255), int(g * 255), int(b * 255)
    return r, g, b

### LED Helper ###
def setAllTo(rgb):
    for i in range(numberOfLeds):
      leds[i] = (rgb)
    leds.write()    

# turns all LEDs off
def clear(): 
    setAllTo (toRgb(0,0,0))

currentH = 0.0
currentS = 1.0
currentV = 0.2

def showCurrent():
    print(f"{currentH} {currentS} {currentV}")
    setAllTo(toRgb(currentH, currentS, currentV))

setAllTo(255,0,0)

while True:
    currentH += 2.0
    if currentH >= 360.0:
        currentH = 0.0

    for i in range(numberOfLeds):
      leds[i] = toRgb(currentH+20*i, currentS, currentV)
    
    leds.write()   

    time.sleep(0.01)
    gc.collect()
