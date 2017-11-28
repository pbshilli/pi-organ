#!/usr/bin/python
'''
pedal_board.py - Pedal board test program

This script reads in a single MIDIBox DIN module (4 daisy-chained 74HC165) and
processes note change events for transmission via RTP-MIDI

RTP-MIDI transmission is performed by the raveloxmidi project found at
https://www.github.com/ravelox/pimidi

Special terms used in this file:

    division - similar to a standard organ division, here its particularly
    being used to describe a particular "address space" of notes or commands.
    For example, a division can have only one "Db4" note defined.  Typically, a
    division will define a contiguous set of notes.
    
    bank - A bank of registers connected to a common set of GPIO pins.
    Currently, only one bank of 74HC165 registers is defined
'''

import socket
import struct
import time
from RPi import GPIO

PI_ORGAN_DIVISIONS = ['pedal']

PI_ORGAN_NOTES = [ 'C2', 'Db2', 'D2', 'Eb2',
        'E2', 'F2', 'Gb2', 'G2', 'Ab2', 'A2',
        'Bb2', 'B2', 'C3', 'Db3', 'D3', 'Eb3',
        'E3', 'F3', 'Gb3', 'G3', 'Ab3', 'A3',
        'Bb3', 'B3', 'C4', 'Db4', 'D4', 'Eb4',
        'E4', 'F4', 'Gb4', 'G4', 'Ab4', 'A4',
        'Bb4', 'B4', 'C5', 'Db5', 'D5', 'Eb5',
        'E5', 'F5', 'Gb5', 'G5', 'Ab5', 'A5',
        'Bb5', 'B5', 'C6', 'Db6', 'D6', 'Eb6',
        'E6', 'F6', 'Gb6', 'G6', 'Ab6', 'A6',
        'Bb6', 'B6', 'C7', ]

def midi_channel_get(division):
    '''Get the MIDI channel associated with the pi-organ division'''
    return PI_ORGAN_DIVISIONS.index(division)

def midi_note_get(note):
    '''Get the MIDI note value associated with the pi-organ note'''
    return PI_ORGAN_NOTES.index(note) + 36

# NOTE: The sleep times in the following functions were arbitrarily picked to
# remain well within the 74HC165 timing limits.  They could probably be lowered
# or removed.

def gpio_load(pin_load):
    '''Trigger the load pin on a bank of 74HC165 registers'''
    GPIO.output(pin_load, GPIO.LOW)
    time.sleep(0.0001)
    GPIO.output(pin_load, GPIO.HIGH)
    time.sleep(0.0001)

def gpio_tick(pin_clock):
    '''Cycle the clock pin on a bank of 74HC165 registers'''
    GPIO.output(pin_clock, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(pin_clock, GPIO.LOW)
    time.sleep(0.00001)

# RTP-MIDI port as defined by raveloxmidi
RTP_MIDI_PORT = 5006

# Open the connection to raveloxmidi
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("localhost", RTP_MIDI_PORT))

# Set up the GPIO board
GPIO.setmode(GPIO.BOARD)

def midi_note_on(channel, midi_note):
    '''Transmit a MIDI "note on" message'''
    pkt_midi = struct.pack("BBBB", 0xaa, 0x90 | channel, midi_note, 0x7f)
    s.send(pkt_midi)

def midi_note_off(channel, midi_note):
    '''Transmit a MIDI "note off" message'''
    pkt_midi = struct.pack("BBBB", 0xaa, 0x80 | channel, midi_note, 0x7f)
    s.send(pkt_midi)

class OrganNote(object):
    '''
    Object used to register a pi-organ note for processing

    Currently the only option for pi-organ notes is to transmit a MIDI message
    on state change, so that action is hard-coded below
    '''
    def __init__(self, division, note):
        self.division = division
        self.note = note

    def state_change(self, timestamp, state_new):
        '''Process a pin state change event'''
        
        # Translate the note to MIDI data
        midi_channel = midi_channel_get(self.division)
        midi_note = midi_note_get(self.note)

        # A grounded pin is defined as "note on"
        if state_new == 0:
            print "[{}] NOTE ON: {} {}".format(timestamp, self.division, self.note)
            midi_note_on(midi_channel, midi_note)

        # An open pin is defined as "note off"
        else:
            print "[{}] NOTE OFF: {} {}".format(timestamp, self.division, self.note)
            midi_note_off(midi_channel, midi_note)

# Define a single bank of 32 pins (1 DIN module) that corresponds to a standard
# 32-note pedal board
BANK_0_PINS = (
        OrganNote('pedal', 'G4'),  # Chip 0 D7
        OrganNote('pedal', 'Gb4'),
        OrganNote('pedal', 'F4'),
        OrganNote('pedal', 'E4'),
        OrganNote('pedal', 'Eb4'),
        OrganNote('pedal', 'D4'),
        OrganNote('pedal', 'Db4'),
        OrganNote('pedal', 'C4'),  # Chip 0 D0
        OrganNote('pedal', 'B3'),  # Chip 1 D7
        OrganNote('pedal', 'Bb3'),
        OrganNote('pedal', 'A3'),
        OrganNote('pedal', 'Ab3'),
        OrganNote('pedal', 'G3'),
        OrganNote('pedal', 'Gb3'),
        OrganNote('pedal', 'F3'),
        OrganNote('pedal', 'E3'),  # Chip 1 D0
        OrganNote('pedal', 'Eb3'), # Chip 2 D7
        OrganNote('pedal', 'D3'),
        OrganNote('pedal', 'Db3'),
        OrganNote('pedal', 'C3'),
        OrganNote('pedal', 'B2'),
        OrganNote('pedal', 'Bb2'),
        OrganNote('pedal', 'A2'),
        OrganNote('pedal', 'Ab2'), # Chip 2 D0
        OrganNote('pedal', 'G2'),  # Chip 3 D7
        OrganNote('pedal', 'Gb2'),
        OrganNote('pedal', 'F2'),
        OrganNote('pedal', 'E2'),
        OrganNote('pedal', 'Eb2'),
        OrganNote('pedal', 'D2'),
        OrganNote('pedal', 'Db2'),
        OrganNote('pedal', 'C2'),  # Chip 3 D0
    )

BANKS_74HC165 = {
        'pedalboard': (24, 23, 26, BANK_0_PINS),
        }

pin_states = {}
for bank, (pin_load, pin_clock, pin_data, pins) in BANKS_74HC165.items():
    # Initialize all pins to "open"
    pin_states[bank] = [ 1 ] * len( pins )

    # Initialize GPIO pins
    GPIO.setup(pin_load, GPIO.OUT)
    GPIO.output(pin_load, GPIO.HIGH)
    GPIO.setup(pin_clock, GPIO.OUT)
    GPIO.output(pin_clock, GPIO.LOW)
    GPIO.setup(pin_data, GPIO.IN)

try:
    while True:
        for bank, (pin_load, pin_clock, pin_data, pins) in BANKS_74HC165.items():
            gpio_load(pin_load)
            for pin_idx, pin in enumerate(pins):
                state_new = GPIO.input(pin_data)
                if state_new != pin_states[bank][pin_idx]:
                    pin_states[bank][pin_idx] = state_new
                    pin.state_change(time.time(), state_new)
                gpio_tick(pin_clock)

except KeyboardInterrupt:
    print "Exit Signal Received"

finally:
    print "Cleaning up...",
    GPIO.cleanup()
    s.close()
    print "Done"
