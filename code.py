# tankLevel.py - Read and display holding tank level
#
# This program is for the CPE board that is connected to a Scenix
# ultrasonic level sensor.
#
# The Senix outputs a 0-10v signal over a sensing range of 0-36 inches
# This output is converted to 0-3.3V with a voltage divider using a
# 10K and a 20K resistor
#
# The voltage is read on pin A1 using the AnalogIn function and then
# used to control the neopixel LEDs to work as a scale
#

import time
import array
import math
import board
import neopixel
import digitalio
from analogio import AnalogIn
from audioio import RawSample
from audioio import AudioOut

# Setup analog in
analogin = AnalogIn(board.A1)

# Setup neopixel ring
pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=.5)
pixels.fill((0,0,0))
pixels.show()
numPixels = 10

# Set up tone
FREQUENCY = 440
SAMPLERATE = 8000
length = SAMPLERATE // FREQUENCY
sine_wave = array.array("H", [0] * length)
for i in range(length):
    sine_wave[i] = int(math.sin(math.pi*2*i/18) * (2**15) + 2**15)

# Enable speaker
speaker_enable = digitalio.DigitalInOut(board.SPEAKER_ENABLE)
speaker_enable.direction = digitalio.Direction.OUTPUT
speaker_enable.value = True
audio = AudioOut(board.SPEAKER)
sine_wave_sample = RawSample(sine_wave)

# Helper to convert 0-65536 reading to 0 to 3.3V
def getVoltage(pin):
    return (pin.value * 3.3) / 65536


# Main Loop - Runs forever
while True:

    #Echo voltage out serial port
    levelVolts = getVoltage(analogin)
    print("Voltage: %f" % levelVolts)

    # Now turn voltage into a pixel display
    # Each pixel is 0.33 V so find number to light

    # Based on tank installation:
    # Full = 1 volt
    # 1/2 Full = 2.5 volts
    # Empty = 3.3 volts

    # Define zero to match installation
    levelZero = 2.75*.33

    litPixels = 9 - int((levelVolts-levelZero) // 0.33)

    for i in range(numPixels):
        color = (0x10, 0, 0)
        if litPixels <= 7:
            color = (0x10, 0x10, 0)
        if litPixels <= 4:
            color = (0, 0x10, 0)
        if i <= litPixels:
            pixels[9-i] = color
        else:
            pixels[9-i] = (0,0,0)

    pixels.show()

    if litPixels >= 8:
        audio.play(sine_wave_sample, loop=True)
        time.sleep(1)
        audio.stop()

    #Sleep
    time.sleep(0.1)


