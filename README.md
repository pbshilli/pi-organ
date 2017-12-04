pi-organ
===

## Overview

pi-organ is a project to create software for a custom MIDI pipe organ
console.  Plans are to use the following:

* MIDIBox DIN modules for digital input
** Note: Based on the 74HC165 shift register
* Adafruit ADS1115 ADC for analog input
* Raspberri Pi and Python for main processing
* RTP-MIDI Output

## Status

Proof-of-concept: pedal\_board.py can read in a 3-manual console's worth of
digital inputs and generate MIDI messages accordingly

## Ideas for other features later

* Basic music generation directly on the pi
* Scripting capability (program your own console effects like loops,
  delays, weird couplers, etc)
* Other non-MIDI outputs:
** Secret code entry (like Batman's piano)
** Other organ relay communication formats (Uniflex?)

