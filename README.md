pi-organ
===

## Overview

pi-organ is a project to create software for a custom MIDI pipe organ
console.  Plans are to use the following:

* MIDIBox DIN modules for digital input
** Note: Based on the 74HC165 shift register
* Raspberri Pi and Python for main processing
* MIDI Output (method TBD)

## Status

Proof-of-concept: din-monitor.py can successfully read 1 DIN module

## Ideas for other features later

* Basic music generation directly on the pi
* Scripting capability (program your own console effects like loops,
  delays, weird couplers, etc)
* Other non-MIDI outputs:
** Secret code entry (like Batman's piano)
** Other organ relay communication formats (Uniflex?)

