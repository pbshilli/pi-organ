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
* NetJack1 MIDI output

## How to connect to a jOrgan instance on another computer

### Install the Jack Audio Connection Kit

On both the jOrgan computer and the Raspberry Pi, install jackd as follows:

`sudo apt-get install jackd`

This will allow the Raspberry Pi to send MIDI messages over Ethernet to the
jOrgan computer

### Install the JACK MIDI daemon for ALSA MIDI

`sudo apt-get install a2jmidid`

jOrgan uses virtual ALSA MIDI ports as inputs, which are not directly
compatible with JACK MIDI.  This daemon allows the virtual ports to become
visible in the Connections window of the Jack controller

### Connect the Raspberry Pi to the jOrgan computer via Ethernet

While NetJack1 MIDI can work over any network, only direct wired Ethernet
can deliver the sub-millisecond latency required for playing music

### On the Raspberry Pi, and get the IP address of the Ethernet port

`ifconfig eth0`

This will be needed later for setting up NetJack1

### On the Raspberry Pi, start the NetJack1 slave

`jackd -d netone`

### On the jOrgan computer, start the NetJack1 master

`jack_netsource -i 0 -o 0 -O 0 -H ip.addr.of.pi`

Both slave and master should auto-connect at this point

Notes:
* Add `-R n` to add retries if not all MIDI messages are getting through
* `ip.addr.of.pi` must be the wired Ethernet address from the previous step
* `-i 0 -o 0 -O 0` shuts off the default audio ports and MIDI input port
  normally created by NetJack1 to minimize wasted bandwidth

### On the jOrgan computer, set up the final MIDI connection paths

Start `qjackctl`, open the Connections tab, go to the MIDI page, and
connect "netjack:system\_capture\_1" to "Virtual Raw MIDI 1-0"

In jOrgan, make sure the program and/or organ disposition are configured
such that "VirMIDI [hw:1,0,0]" is processed for all inputs (easiest way
is to enable that device in the jOrgan Midi Merger preferences)

### On the Raspberry Pi, start up the main application

`python3 pedal_board.py`

### Make some music!

At this point, the final paths should be set up for jOrgan:

Arduino and RPi GPIO -> `pedal_board.py` -> NetJack1 slave -> Ethernet ->
NetJack1 master -> `a2jmidid` -> Virtual Raw MIDI 1-0 -> jOrgan Midi Merger
-> jOrgan processing -> Audio Out

## Current Status

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

