import time
import board
import neopixel
from random import *
from threading import Event
import socket


pixel_pin = board.D18
num_pixels = 8
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=.1, auto_write=True, pixel_order=neopixel.GRB
)

red     = (255, 0, 0)
green   = (0, 255, 0)
blue    = (0, 0, 255)
mozzie_blue = (50, 200, 255)
white   = (255, 255, 255)
pink    = (255, 20, 147)
off     = (0, 0, 0)


def stringToBinary(text: str):
    return ' '.join(format(ord(x), 'b') for x in text)

# Gets local IP of Raspberry
def getLocalIP():
    return [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
    

# Source: https://learn.adafruit.com/adafruit-neopixel-uberguide/python-circuitpython
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)

def rainbow_cycle(stop_event, wait=0.001):
    while not stop_event.is_set():
        for j in range(255):
            for i in range(num_pixels):
                if stop_event.is_set():
                    break
                pixel_index = (i * 256 // num_pixels) + j
                pixels[i] = wheel(pixel_index & 255)
            #pixels.show()
            time.sleep(wait)
# /source: https://learn.adafruit.com/adafruit-neopixel-uberguide/python-circuitpython


# Sweeping red light, like on KITT from Knight Rider
def knight_rider(stop_event, wait=0.05):
    while not stop_event.is_set():
        for i in range(num_pixels):
            pixels[i] = (255, 0, 0)
            time.sleep(wait)
            pixels[i] = (0, 0, 0)

        for i in range(num_pixels - 2, 0, -1):
            pixels[i] = (255, 0, 0)
            time.sleep(wait)
            pixels[i] = (0, 0, 0)

def cycle_colors(stop_event, wait=0.001):
    while not stop_event.is_set():
        for r in range(255):
            pixels.fill((r, 0, 0))
            time.sleep(wait)

        for g in range(255):
            pixels.fill((255, g, 0))
            time.sleep(wait)

        for b in range(255):
            pixels.fill((255, 255, b))
            time.sleep(wait)

        for r in range(255, 0, -1):
            pixels.fill((r, 255, 255))
            time.sleep(wait)

        for g in range(255, 0, -1):
            pixels.fill((0, g, 255))
            time.sleep(wait)

        for b in range(255, 0, -1):
            pixels.fill((0, 0, b))
            time.sleep(wait)

# Flickering orange-reddish, imitating light from a fireplace
def fireplace(stop_event, wait=0.01):
    initialBrightness = pixels.brightness

    maxVariationStepFactor = 0.05
    maxColorVariationStepFactor = 0.1
    orange = 65

    pixels.fill((255, 75, 0)) # Orange
    while not stop_event.is_set():
        for i in range(len(pixels)):
            # Touch of color flicker
            maxColorVariationStep = orange * maxColorVariationStepFactor
            orange = uniform(max(orange - maxColorVariationStep, 45), min(orange + maxColorVariationStep, 80))
            orange = int(orange)
            pixels[i] = (255, orange, 0)

            # Touch of brightness flicker
            maxVariationStep = pixels.brightness * maxVariationStepFactor
            pixels.brightness = uniform(max(pixels.brightness - maxVariationStep, 0.1), min(pixels.brightness + maxVariationStep, 1))

        time.sleep(wait)

    pixels.brightness = initialBrightness

# Blinking 2 outermost right and left LED's in a random interval
def eyes(stop_event, wait=0.1):
    eyeInitDelay = 0.25
    
    # pink = (255, 20, 147)

    pixels.fill((0, 0, 0))

    # Open Eyes
    pixels[0] = pink
    pixels[7] = pink
    time.sleep(eyeInitDelay)
    pixels[1] = pink
    pixels[6] = pink
    # time.sleep(eyeInitDelay)
    # pixels[2] = pink
    # pixels[5] = pink

    while not stop_event.is_set():
        
        # Blinking chance 1/50, calculated every {wait} seconds
        # Ex: 1/50 chance every 0.1s ~ 1 blink every 5 seconds
        if randint(0, 50) == 1:
            initialBrightness = pixels.brightness
            # print(f"Initial Brightness: {initialBrightness}")

            # Fade out (should take 100ms)
            for brightness in range(int(initialBrightness * 100), 0, -1):
                pixels.brightness = brightness / 100
                # print(f"Brightness set to {brightness / 100}")

                sleepTime = 0.1 / (initialBrightness * 100)
                # print(f"sleepTime: {sleepTime}")

                time.sleep(sleepTime)

            # Fade in (should take 100ms)
            for brightness in range(int(initialBrightness * 100)):
                pixels.brightness = brightness / 100
                # print(f"Brightness set to {brightness / 100}")
                
                time.sleep(sleepTime)

            pixels.brightness = initialBrightness

        time.sleep(wait)

# Every pixel white at max brightness
def flashlight(stop_event, wait=0.1):
    initialBrightness = pixels.brightness

    pixels.brightness = 1
    while not stop_event.is_set():
        pixels.fill((255, 255, 255))
        time.sleep(wait)

    pixels.brightness = initialBrightness


# Drone's in-game animation
def r6Idle(stop_event, wait=0.035, rgb=mozzie_blue):
    pixels.fill(off)

    midPoint = int(len(pixels) / 2)

    while not stop_event.is_set():
        for i in range(midPoint):
            pixels[midPoint - 1 - i] = rgb
            pixels[midPoint + i] = rgb
            time.sleep(wait)

        for i in range(midPoint):
            pixels[i] = off
            pixels[-1 - i] = off
            time.sleep(wait)

# Display a single binary character on the 8-bit RGB 
def displayBinaryChar(binaryChar: str, rgb: tuple):
    # Right align
    offset = len(pixels) - len(binaryChar)

    for i in range(len(binaryChar)):
        # Turn pixel on if binary 1 else off
        pixels[offset + i] = rgb if binaryChar[i] == "1" else off

# Display a string character-by-character on 8-bit RGB
def displayBinaryText(stop_event, text: str = getLocalIP() + ":5000", rgb: tuple = red):
    # print(f"Displaying {text}")
    pixels.fill(off)

    textBytes = stringToBinary(text).split(" ")

    firstLoop = True
    while not stop_event.is_set():
        
        # Delay after displaying whole message
        if not firstLoop:
            time.sleep(5)
        
        for byte in textBytes:
            if stop_event.is_set():
                break
            
            displayBinaryChar(byte, rgb)
            time.sleep(1)

            pixels.fill((0, 0, 0))
            time.sleep(1/3)
        
        firstLoop = False


if __name__ == "__main__":
    while True:
        # rainbow_cycle(Event())
        # knight_rider(Event())
        # cycle_colors(Event())
        # fireplace(Event())
        # eyes(Event())
        r6Idle(Event())
        # displayBinaryText(Event())

        # pixels.fill((255, 75, 0))
        # time.sleep(0.2)
        # pixels.fill((0, 0, 0))
        # time.sleep(0.2)

        # pixels.brightness = 1
        # pixels.fill((255, 255, 255))
        
        # pixels.fill((0, 0, 0))