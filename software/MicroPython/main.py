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

def read_config(file_name):
    config = {}
    with open(file_name, 'r') as file:
        lines = file.readlines()
        for line in lines:
            key, value = line.strip().split('=', 1)
            config[key] = value
    return config

# Function definitions (assuming they are already defined)
def set_blue():
    # Code to set the LED strip to blue
    print("blue")
    pass

def set_red():
    # Code to set the LED strip to red
    pass

def set_green():
    # Code to set the LED strip to green
    pass

def set_rainbow():
    # Code to set the LED strip to rainbow
    pass


# Function to handle setting color by name
def set_color_by_name(color_name):
    if color_name == 'rot':
        set_red()
    elif color_name == 'grün':
        set_green()
    elif color_name == 'blau':
        set_blue()
    elif color_name == 'regenbogen':
        set_rainbow()
    # Add more colors as needed
    else:
        print(f"Color {color_name} not recognized")

# Web server function
def web_page():
    html = """
    <html>
        <head>
            <title>Lukas Lampe</title>
            <style>
                .wrapper {
                    margin: auto;
                    max-width: 100%;
                }
                @media screen and (min-width: 600px) {
                    .wrapper {
                        max-width: 400px; /* Adjust this value as needed */
                    }
                }
                .form-container {
                    margin: auto;
                    max-width: 100%;
                }
                input[type="text"], input[type="submit"] {
                    width: 100%;
                    box-sizing: border-box;
                }
                input[type="submit"] {
                    margin-top: 10px; /* Adds space between the text field and the button */
                }
            </style>
        </head>
        <body>
            <div class="wrapper">
                <h1>Lukas Lampe</h1>
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

def check_for_http_requests():
    try:
        # Use select to wait for the socket to be ready
        read_sockets, _, _ = select.select([s], [], [], 0.1)

        for sock in read_sockets:
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
                        color_name = request_str[color_start:color_end]
                        set_color_by_name(color_name)

                    print("Preparing Response")
                    response = "HTTP/1.1 200 OK\n"
                    response += "Content-Type: text/html\n"
                    response += "Connection: close\n\n"  # Note the double newline
                    response += web_page()  # The HTML content
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

    except KeyboardInterrupt:
        print("Script interrupted by user")
        sys.exit()

    except OSError as e:
        if e.args[0] != 11:  # Log errors other than EAGAIN
            print('An error occurred:', str(e))
        # EAGAIN is expected behavior for non-blocking sockets and is silently handled



def update_leds():
    # Update the LEDs to create the rainbow effect
    # This function should be non-blocking and update only a small part of the effect
    pass

print(f"memory in the beginning: {gc.mem_free()}")

# Read Wi-Fi credentials from config file
wifi_config = read_config('config.txt')
ssid = wifi_config.get('ssid')
password = wifi_config.get('password')

# Connect to Wi-Fi
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

while not station.isconnected():
    pass

print('Connection successful')
print(station.ifconfig())

# # Create a socket and listen for requests
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.bind(('', 80))
# s.listen(5)

# Set up the socket for non-blocking mode
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 80))
s.listen(5)
s.setblocking(False)

print(f"memory before collection: {gc.mem_free()}")
gc.collect()
print(f"memory after collection: {gc.mem_free()}")


while True:
    check_for_http_requests()
    update_leds()
    # Short delay might be needed to prevent the loop from consuming too much CPU
    time.sleep(0.1)
print("loop exited")
# numberOfLeds = 16
# ledPin = Pin(2, Pin.OUT)  # pin 2 is also called D4
# leds = NeoPixel(ledPin, numberOfLeds) 

# # HSV color values to RGB used by the LEDs. See https://en.wikipedia.org/wiki/HSL_and_HSV
# def toRgb(h, s, v):
#     h = float(h)
#     s = float(s)
#     v = float(v)
#     h60 = h / 60.0
#     h60f = math.floor(h60)
#     hi = int(h60f) % 6
#     f = h60 - h60f
#     p = v * (1 - s)
#     q = v * (1 - f * s)
#     t = v * (1 - (1 - f) * s)
#     r, g, b = 0, 0, 0
#     if hi == 0: r, g, b = v, t, p
#     elif hi == 1: r, g, b = q, v, p
#     elif hi == 2: r, g, b = p, v, t
#     elif hi == 3: r, g, b = p, q, v
#     elif hi == 4: r, g, b = t, p, v
#     elif hi == 5: r, g, b = v, p, q
#     r, g, b = int(r * 255), int(g * 255), int(b * 255)
#     return r, g, b

# ### LED Helper ###
# def setAllTo(rgb):
#     for i in range(numberOfLeds):
#       leds[i] = (rgb)
#     leds.write()    

# # turns all LEDs off
# def clear(): 
#     setAllTo (toRgb(0,0,0))

# currentH = 0.0
# currentS = 1.0
# # currentV = 0.8 # aka brightness
# currentV = 0.1 # aka brightness

# def showCurrent():
#     print(f"{currentH} {currentS} {currentV}")
#     setAllTo(toRgb(currentH, currentS, currentV))

# print()

# while True:
#     color = input("Bitte Farbe eingeben: ").lower()
#     if ( color == 'blau'):
#         for i in range(numberOfLeds):
#             leds[i] = 0, 0, 255
#     if ( color == 'rot'):
#         for i in range(numberOfLeds):
#             leds[i] = 255, 0, 0
#     if ( color == 'gruen'):
#         for i in range(numberOfLeds):
#             leds[i] = 0, 255, 0
#     leds.write()   
#     gc.collect()
