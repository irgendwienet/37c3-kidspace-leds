import select
import sys
from machine import Pin, freq
from neopixel import NeoPixel
from sys import platform

import time 
import math
import gc

import network
import socket

BRIGHTNESS = 0.8
BLINKINTERVAL = 1.0  # Blink every 1 second

isBlinking = False
blinkLastToggle = time.time()
blinkDarkPhase = False

ledsSave = []

def read_config(file_name):
    config = {}
    with open(file_name, 'r') as file:
        lines = file.readlines()
        for line in lines:
            key, value = line.strip().split('=', 1)
            config[key] = value
    return config

def init_leds():
    global isBlinking, blinkLastToggle, ledsSave

    numberOfLeds = 16
    ledPin = Pin(2, Pin.OUT)  # pin 2 is also called D4
    leds = NeoPixel(ledPin, numberOfLeds) 
    for i in range(numberOfLeds):
        ledsSave.append((0, 0, 0)) 

    currentH = 0.0
    currentS = 1.0
    # currentV = 0.8 # aka brightness
    currentV = BRIGHTNESS 

    rainbow = False
    isBlinking = False
    blinkLastToggle = time.time()
    update_leds(currentH, currentS, currentV, numberOfLeds, leds, rainbow, 'weiß')

    return currentH, currentS, currentV, numberOfLeds, leds, rainbow, 
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

def update_leds(currentH, currentS, currentV, numberOfLeds, leds, rainbow, color_choice):
    global isBlinking, blinkLastToggle, blinkDarkPhase, ledsSave

    if color_choice:
        currentV = BRIGHTNESS
        if color_choice == 'regenbogen':
            rainbow = True
        elif color_choice == 'blink':
            if not isBlinking:  # Only save the state when blinking starts
                isBlinking = True
                blinkLastToggle = time.time()
                blinkDarkPhase = False # will be inverted on first toggle and I want to start with dark :)

        elif color_choice == 'stop':
            isBlinking = False
        else:
            rainbow = False
            if color_choice == 'rot':
                print("setting rot")
                currentH = 1
                currentS = 1
            elif color_choice == 'grün' \
                or color_choice == 'gr%fcn' \
                or color_choice == 'gruen':
                currentH = 120
                currentS = 1
            elif color_choice == 'blau':
                currentH = 240
                currentS = 1
            elif color_choice == 'pink':
                currentH = 340
                currentS = 1
            elif color_choice == 'lila' \
            or color_choice == 'violett':
                currentH = 280
                currentS = 1
            elif color_choice == 'gelb':
                currentH = 60
                currentS = 1
            elif color_choice == 'schwarz' \
            or color_choice == 'aus':
                currentH = 0
                currentS = 0
                currentV = 0
            elif color_choice == 'weiss' \
                or color_choice == 'weiß' \
                or color_choice == 'weis' \
                or color_choice == 'wei%df':
                currentH = 0
                currentS = 0

            for i in range(numberOfLeds):
                leds[i] = toRgb(currentH, currentS, currentV)
                ledsSave[i] = toRgb(currentH, currentS, currentV)



            
    if isBlinking:
        if time.time() - blinkLastToggle > BLINKINTERVAL:
            blinkDarkPhase = not blinkDarkPhase
            blinkLastToggle = time.time()
            if blinkDarkPhase:
                for i in range(numberOfLeds):
                    leds[i] = (0, 0, 0)  # Turn off all LEDs
            else:
                for i in range(numberOfLeds):
                    leds[i] = ledsSave[i]  # Restore the saved state
    if rainbow:
        currentH += 2.0
        if currentH >= 360.0:
            currentH = 0.0
        for i in range(numberOfLeds):
            ledsSave[i] = toRgb(currentH+20*i, currentS, currentV)
            if not isBlinking or not blinkDarkPhase:
                leds[i] = toRgb(currentH+20*i, currentS, currentV)

    leds.write()

    return currentH, currentS, currentV, numberOfLeds, leds, rainbow

def web_page(kidName):

    html = f"""
    <html>
        <head>
            <title>{kidName} Lampe</title>
            <style>
                html {{
                    font-size: 300%; /* Increase base font-size */
                }}
                .wrapper {{
                    margin: auto;
                    max-width: 100%;
                }}
                @media screen and (min-width: 600px) {{
                    .wrapper {{
                        max-width: 600px; /* Adjust this value as needed */
                    }}
                }}
                .form-container {{
                    margin: auto;
                    max-width: 100%;
                }}
                input[type="text"], input[type="submit"] {{
                    width: 100%;
                    box-sizing: border-box;
                    padding: 10px; /* Adjust padding */
                    font-size: 1em; /* Adjust font size */
                }}
                input[type="submit"] {{
                    margin-top: 30px; /* Increase space between the text field and the button */
                }}
                h1 {{
                    font-size: 1.5em; /* Adjust heading font size */
                }}
            </style>
        </head>
        <body>
            <div class="wrapper">
                <h1>{kidName} Lampe</h1>  <!-- Replaced with the kidName variable -->
                <div class="form-container">
                    <form action="/" method="get">
                        <input type="text" name="color" placeholder="Farbe"><br>
                        <input type="submit" value="Los!">
                    </form>
                </div>
            </div>
        </body>
    </html>
    """

    return html


def check_for_http_requests(kidName):
    try:
        # Use select to wait for the socket to be ready
        read_sockets, _, _ = select.select([s], [], [], 0.1)

        for sock in read_sockets:
            color_name = None
            if sock is s:
                conn, addr = s.accept()
                print('Got a connection from %s' % str(addr))
                print (f"conn: {conn}")
                print (f"addr: {addr}")

                # Wait briefly for data to become available
                ready_to_read, _, _ = select.select([conn], [], [], 1)
                if ready_to_read:
                    request = conn.recv(1024)  # Reading the request in one go
                    request_str = request.decode("utf-8")
                    print('Content = %s' % request_str)

                    # Process request and set color
                    color_start = request_str.find('/?color=') + 8
                    if color_start > 7:
                        color_end = request_str.find(' ', color_start)
                        color_name = request_str[color_start:color_end].lower()
                        # set_color_by_name(color_name)

                    print("Preparing Response")
                    response = "HTTP/1.1 200 OK\n"
                    response += "Content-Type: text/html\n"
                    response += "Connection: close\n\n"  # Note the double newline
                    response += web_page(kidName)  # The HTML content
                    conn.setblocking(True)
                    try:
                        print("Sending Response")
                        conn.sendall(response.encode())
                    except Exception as e:
                        print("Error sending response:", e)
                    finally:
                        conn.setblocking(False)
                        print("Closing Connection")
                        conn.close()

                    # Memory management
                    print(f"memory before collection: {gc.mem_free()}")
                    gc.collect()
                    print(f"memory after collection: {gc.mem_free()}")
                    return color_name
    except KeyboardInterrupt:
        print("Script interrupted by user")
        sys.exit()

    except OSError as e:
        # if e.args[0] != 11:  # Log errors other than EAGAIN
        print('An error occurred:', str(e))
        # EAGAIN is expected behavior for non-blocking sockets and is silently handled

print(f"memory in the beginning: {gc.mem_free()}")

currentH, currentS, currentV, numberOfLeds, leds, rainbow = init_leds()


# Read Wi-Fi credentials from config file
config = read_config('config.txt')
ssid = config.get('ssid')
password = config.get('password')
kidName = config.get('kidName')

# Connect to Wi-Fi
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

start_time = time.time()  # Record the start time
timeout = 10  # Timeout in seconds

connectionFailed = False
while not station.isconnected():
    if time.time() - start_time > timeout:
        print("Connection timed out after 10 seconds")
        connectionFailed = True
        break
    time.sleep(0.1)  # Add a short delay to prevent the loop from consuming too much CPU

if connectionFailed:
    print('Connection Failed')
else:
    print('Connection successful')
    print(station.ifconfig())

# After connection attempt, set to rainbow as default
rainbow = True

# Set up the socket for non-blocking mode
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 80))
s.listen(5)
s.setblocking(False)

gc.collect()


while True:
    color_choice = check_for_http_requests(kidName)
    currentH, currentS, currentV, numberOfLeds, leds, rainbow = update_leds(currentH, currentS, currentV, numberOfLeds, leds, rainbow, color_choice)    # Short delay might be needed to prevent the loop from consuming too much CPU
    time.sleep(0.01)
    gc.collect()
