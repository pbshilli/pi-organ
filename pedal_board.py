#!/usr/bin/python
'''
pedal_board.py - Pedal board test program

This script reads in MIDIBox DIN modules (each containing 4 daisy-chained
74HC165) and processes note change events for transmission via RTP-MIDI

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

PI_ORGAN_DIVISIONS = ['pedal', 'accomp', 'great', 'solo']

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
    time.sleep(0.000001)
    GPIO.output(pin_load, GPIO.HIGH)
    time.sleep(0.000001)

def gpio_tick(pin_clock):
    '''Cycle the clock pin on a bank of 74HC165 registers'''
    GPIO.output(pin_clock, GPIO.HIGH)
    time.sleep(0.0000001)
    GPIO.output(pin_clock, GPIO.LOW)
    time.sleep(0.0000001)

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

# Through some testing, it was found that the RPi can't drive more than about 4
# DIN boards per bank, so split up the banks accordingly

BANK_0_PINS = (
        None,                     # Chip 0 D0
        None,
        None,
        OrganNote('solo', 'C7'),
        OrganNote('solo', 'B6'),
        OrganNote('solo', 'Bb6'),
        OrganNote('solo', 'A6'),
        OrganNote('solo', 'Ab6'), # Chip 0 D7
        OrganNote('solo', 'G6'),  # Chip 1 D0
        OrganNote('solo', 'Gb6'),
        OrganNote('solo', 'F6'),
        OrganNote('solo', 'E6'),
        OrganNote('solo', 'Eb6'),
        OrganNote('solo', 'D6'),
        OrganNote('solo', 'Db6'),
        OrganNote('solo', 'C6'),  # Chip 1 D0
        OrganNote('solo', 'B5'),  # Chip 2 D7
        OrganNote('solo', 'Bb5'),
        OrganNote('solo', 'A5'),
        OrganNote('solo', 'Ab5'),
        OrganNote('solo', 'G5'),
        OrganNote('solo', 'Gb5'),
        OrganNote('solo', 'F5'),
        OrganNote('solo', 'E5'),  # Chip 2 D0
        OrganNote('solo', 'Eb5'), # Chip 3 D7
        OrganNote('solo', 'D5'),
        OrganNote('solo', 'Db5'),
        OrganNote('solo', 'C5'),
        OrganNote('solo', 'B4'),
        OrganNote('solo', 'Bb4'),
        OrganNote('solo', 'A4'),
        OrganNote('solo', 'Ab4'), # Chip 3 D0
        OrganNote('solo', 'G4'),  # Chip 4 D7
        OrganNote('solo', 'Gb4'),
        OrganNote('solo', 'F4'),
        OrganNote('solo', 'E4'),
        OrganNote('solo', 'Eb4'),
        OrganNote('solo', 'D4'),
        OrganNote('solo', 'Db4'),
        OrganNote('solo', 'C4'),  # Chip 4 D0
        OrganNote('solo', 'B3'),  # Chip 5 D7
        OrganNote('solo', 'Bb3'),
        OrganNote('solo', 'A3'),
        OrganNote('solo', 'Ab3'),
        OrganNote('solo', 'G3'),
        OrganNote('solo', 'Gb3'),
        OrganNote('solo', 'F3'),
        OrganNote('solo', 'E3'),  # Chip 5 D0
        OrganNote('solo', 'Eb3'), # Chip 6 D7
        OrganNote('solo', 'D3'),
        OrganNote('solo', 'Db3'),
        OrganNote('solo', 'C3'),
        OrganNote('solo', 'B2'),
        OrganNote('solo', 'Bb2'),
        OrganNote('solo', 'A2'),
        OrganNote('solo', 'Ab2'), # Chip 6 D0
        OrganNote('solo', 'G2'),  # Chip 7 D7
        OrganNote('solo', 'Gb2'),
        OrganNote('solo', 'F2'),
        OrganNote('solo', 'E2'),
        OrganNote('solo', 'Eb2'),
        OrganNote('solo', 'D2'),
        OrganNote('solo', 'Db2'),
        OrganNote('solo', 'C2'),  # Chip 7 D0
        None,                     # Chip 8 D0
        None,
        None,
        OrganNote('great', 'C7'),
        OrganNote('great', 'B6'),
        OrganNote('great', 'Bb6'),
        OrganNote('great', 'A6'),
        OrganNote('great', 'Ab6'), # Chip 8 D7
        OrganNote('great', 'G6'),  # Chip 9 D0
        OrganNote('great', 'Gb6'),
        OrganNote('great', 'F6'),
        OrganNote('great', 'E6'),
        OrganNote('great', 'Eb6'),
        OrganNote('great', 'D6'),
        OrganNote('great', 'Db6'),
        OrganNote('great', 'C6'),  # Chip 9 D0
        OrganNote('great', 'B5'),  # Chip 10 D7
        OrganNote('great', 'Bb5'),
        OrganNote('great', 'A5'),
        OrganNote('great', 'Ab5'),
        OrganNote('great', 'G5'),
        OrganNote('great', 'Gb5'),
        OrganNote('great', 'F5'),
        OrganNote('great', 'E5'),  # Chip 10 D0
        OrganNote('great', 'Eb5'), # Chip 11 D7
        OrganNote('great', 'D5'),
        OrganNote('great', 'Db5'),
        OrganNote('great', 'C5'),
        OrganNote('great', 'B4'),
        OrganNote('great', 'Bb4'),
        OrganNote('great', 'A4'),
        OrganNote('great', 'Ab4'), # Chip 11 D0
        OrganNote('great', 'G4'),  # Chip 12 D7
        OrganNote('great', 'Gb4'),
        OrganNote('great', 'F4'),
        OrganNote('great', 'E4'),
        OrganNote('great', 'Eb4'),
        OrganNote('great', 'D4'),
        OrganNote('great', 'Db4'),
        OrganNote('great', 'C4'),  # Chip 12 D0
        OrganNote('great', 'B3'),  # Chip 13 D7
        OrganNote('great', 'Bb3'),
        OrganNote('great', 'A3'),
        OrganNote('great', 'Ab3'),
        OrganNote('great', 'G3'),
        OrganNote('great', 'Gb3'),
        OrganNote('great', 'F3'),
        OrganNote('great', 'E3'),  # Chip 13 D0
        OrganNote('great', 'Eb3'), # Chip 14 D7
        OrganNote('great', 'D3'),
        OrganNote('great', 'Db3'),
        OrganNote('great', 'C3'),
        OrganNote('great', 'B2'),
        OrganNote('great', 'Bb2'),
        OrganNote('great', 'A2'),
        OrganNote('great', 'Ab2'), # Chip 14 D0
        OrganNote('great', 'G2'),  # Chip 15 D7
        OrganNote('great', 'Gb2'),
        OrganNote('great', 'F2'),
        OrganNote('great', 'E2'),
        OrganNote('great', 'Eb2'),
        OrganNote('great', 'D2'),
        OrganNote('great', 'Db2'),
        OrganNote('great', 'C2'),  # Chip 15 D0
        )

BANK_1_PINS = (
        None,                     # Chip 0 D0
        None,
        None,
        OrganNote('accomp', 'C7'),
        OrganNote('accomp', 'B6'),
        OrganNote('accomp', 'Bb6'),
        OrganNote('accomp', 'A6'),
        OrganNote('accomp', 'Ab6'), # Chip 0 D7
        OrganNote('accomp', 'G6'),  # Chip 1 D0
        OrganNote('accomp', 'Gb6'),
        OrganNote('accomp', 'F6'),
        OrganNote('accomp', 'E6'),
        OrganNote('accomp', 'Eb6'),
        OrganNote('accomp', 'D6'),
        OrganNote('accomp', 'Db6'),
        OrganNote('accomp', 'C6'),  # Chip 1 D0
        OrganNote('accomp', 'B5'),  # Chip 2 D7
        OrganNote('accomp', 'Bb5'),
        OrganNote('accomp', 'A5'),
        OrganNote('accomp', 'Ab5'),
        OrganNote('accomp', 'G5'),
        OrganNote('accomp', 'Gb5'),
        OrganNote('accomp', 'F5'),
        OrganNote('accomp', 'E5'),  # Chip 2 D0
        OrganNote('accomp', 'Eb5'), # Chip 3 D7
        OrganNote('accomp', 'D5'),
        OrganNote('accomp', 'Db5'),
        OrganNote('accomp', 'C5'),
        OrganNote('accomp', 'B4'),
        OrganNote('accomp', 'Bb4'),
        OrganNote('accomp', 'A4'),
        OrganNote('accomp', 'Ab4'), # Chip 3 D0
        OrganNote('accomp', 'G4'),  # Chip 4 D7
        OrganNote('accomp', 'Gb4'),
        OrganNote('accomp', 'F4'),
        OrganNote('accomp', 'E4'),
        OrganNote('accomp', 'Eb4'),
        OrganNote('accomp', 'D4'),
        OrganNote('accomp', 'Db4'),
        OrganNote('accomp', 'C4'),  # Chip 4 D0
        OrganNote('accomp', 'B3'),  # Chip 5 D7
        OrganNote('accomp', 'Bb3'),
        OrganNote('accomp', 'A3'),
        OrganNote('accomp', 'Ab3'),
        OrganNote('accomp', 'G3'),
        OrganNote('accomp', 'Gb3'),
        OrganNote('accomp', 'F3'),
        OrganNote('accomp', 'E3'),  # Chip 5 D0
        OrganNote('accomp', 'Eb3'), # Chip 6 D7
        OrganNote('accomp', 'D3'),
        OrganNote('accomp', 'Db3'),
        OrganNote('accomp', 'C3'),
        OrganNote('accomp', 'B2'),
        OrganNote('accomp', 'Bb2'),
        OrganNote('accomp', 'A2'),
        OrganNote('accomp', 'Ab2'), # Chip 6 D0
        OrganNote('accomp', 'G2'),  # Chip 7 D7
        OrganNote('accomp', 'Gb2'),
        OrganNote('accomp', 'F2'),
        OrganNote('accomp', 'E2'),
        OrganNote('accomp', 'Eb2'),
        OrganNote('accomp', 'D2'),
        OrganNote('accomp', 'Db2'),
        OrganNote('accomp', 'C2'),  # Chip 7 D0
        OrganNote('pedal', 'G4'), # Chip 8 D7
        OrganNote('pedal', 'Gb4'),
        OrganNote('pedal', 'F4'),
        OrganNote('pedal', 'E4'),
        OrganNote('pedal', 'Eb4'),
        OrganNote('pedal', 'D4'),
        OrganNote('pedal', 'Db4'),
        OrganNote('pedal', 'C4'),  # Chip 8 D0
        OrganNote('pedal', 'B3'),  # Chip 9 D7
        OrganNote('pedal', 'Bb3'),
        OrganNote('pedal', 'A3'),
        OrganNote('pedal', 'Ab3'),
        OrganNote('pedal', 'G3'),
        OrganNote('pedal', 'Gb3'),
        OrganNote('pedal', 'F3'),
        OrganNote('pedal', 'E3'),  # Chip 9 D0
        OrganNote('pedal', 'Eb3'), # Chip 10 D7
        OrganNote('pedal', 'D3'),
        OrganNote('pedal', 'Db3'),
        OrganNote('pedal', 'C3'),
        OrganNote('pedal', 'B2'),
        OrganNote('pedal', 'Bb2'),
        OrganNote('pedal', 'A2'),
        OrganNote('pedal', 'Ab2'), # Chip 10 D0
        OrganNote('pedal', 'G2'),  # Chip 11 D7
        OrganNote('pedal', 'Gb2'),
        OrganNote('pedal', 'F2'),
        OrganNote('pedal', 'E2'),
        OrganNote('pedal', 'Eb2'),
        OrganNote('pedal', 'D2'),
        OrganNote('pedal', 'Db2'),
        OrganNote('pedal', 'C2'),  # Chip 11 D0
    )

# On a MIDIBox DIN board, the load, clock, and data pins are marked RC, SC, and
# SI, respectively

BANKS_74HC165 = {
        'solo_great': (19, 21, 23, BANK_0_PINS),
        'accomp_pedal': (37, 38, 40, BANK_1_PINS),
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

# TODO: Zip the bank processing together since the longest operations, the GPIO
# functions, can be done in parallel for each bank.  The banks currently defined
# can all be processed in about 3ms, so it's good enough for now
try:
    while True:
        for bank, (pin_load, pin_clock, pin_data, pins) in BANKS_74HC165.items():
            gpio_load(pin_load)
            for pin_idx, pin in enumerate(pins):
                state_new = GPIO.input(pin_data)
                if state_new != pin_states[bank][pin_idx]:
                    pin_states[bank][pin_idx] = state_new
                    if pin is not None:
                        pin.state_change(time.time(), state_new)
                gpio_tick(pin_clock)

except KeyboardInterrupt:
    print "Exit Signal Received"

finally:
    print "Cleaning up...",
    GPIO.cleanup()
    s.close()
    print "Done"
