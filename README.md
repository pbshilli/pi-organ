pi-organ
===

## Overview

pi-organ is a project to create software for a custom MIDI pipe organ
console.  Plans are to use the following:

* MIDIBox DIN modules for digital input
** Note: Based on the 74HC165 shift register
* Raspberri Pi and Python for main processing
* Arduino Leonardo for pedal board processing
** This is required since the pedal board is physically separate from
   the rest of the console.  The Arduino connects to the Raspberry Pi
   via USB.
* RTP-MIDI Output

## Status

Proof-of-concept: pedal\_board.py can read in a 3-manual console's worth of
digital inputs and generate MIDI messages accordingly

## Development on the raspberry pi

### Arduino development

Arduino development on the pi is done by installing the "Linux ARM"
version of the Arduino IDE as per https://www.arduino.cc/en/Main/Software.

Command to build and load the pedal board Arduino Leonardo sketch file:
`~/path/to/arduino --upload --board arduino:avr:leonardo --port /dev/ttyACM0 pedal\_board.ino`

## Ideas for other features later

* Basic music generation directly on the pi
* Scripting capability (program your own console effects like loops,
  delays, weird couplers, etc)
* Other non-MIDI outputs:
** Secret code entry (like Batman's piano)
** Other organ relay communication formats (Uniflex?)

