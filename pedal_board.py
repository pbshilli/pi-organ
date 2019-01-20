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
import serial
import struct
import time
import queue
from RPi import GPIO
import jack

PI_ORGAN_DIVISIONS = {'pedal': 0, 'accomp': 1, 'great':2, 'solo':3}

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
    return PI_ORGAN_DIVISIONS[division]

def midi_note_get(note):
    '''Get the MIDI note value associated with the pi-organ note'''
    return PI_ORGAN_NOTES.index(note) + 36

# NOTE: The sleep times in the following functions were arbitrarily picked to
# remain well within the 74HC165 timing limits.  They could probably be lowered
# or removed.

def gpio_load(pin_load):
    '''Trigger the load pin on a bank of 74HC165 registers'''
    GPIO.output(pin_load, GPIO.LOW)
    time.sleep(0.000005)
    GPIO.output(pin_load, GPIO.HIGH)
    time.sleep(0.000005)

def gpio_tick(pin_clock):
    '''Cycle the clock pin on a bank of 74HC165 registers'''
    GPIO.output(pin_clock, GPIO.HIGH)
    time.sleep(0.000005)
    GPIO.output(pin_clock, GPIO.LOW)
    time.sleep(0.000005)

# RTP-MIDI port as defined by raveloxmidi
RTP_MIDI_PORT = 5006

# Open the connection to jack-midi
client = jack.Client('Pi-Organ')
outport = client.midi_outports.register('output')
midi_msg_q = queue.Queue()

@client.set_process_callback
def process(frames):
    global midi_msg_q
    outport.clear_buffer()
    try:
        while True:
            midi_msg = midi_msg_q.get(block=False)
            outport.write_midi_event(0, midi_msg)
    except queue.Empty:
        pass

client.activate()
client.connect(outport, 'system:playback_1')
# Set up the GPIO board
GPIO.setmode(GPIO.BOARD)

def midi_note_on(channel, midi_note):
    '''Transmit a MIDI "note on" message'''
    midi_msg_q.put((0x90 | channel, midi_note, 127))

def midi_note_off(channel, midi_note):
    '''Transmit a MIDI "note off" message'''
    midi_msg_q.put((0x80 | channel, midi_note, 0))

def midi_control_change(channel, control, value):
    '''Transmit a MIDI "note off" message'''
    midi_msg_q_.put((0xb0 | channel, control, value))

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
            print("[{}] NOTE ON: {} {}".format(timestamp, self.division, self.note))
            midi_note_on(midi_channel, midi_note)

        # An open pin is defined as "note off"
        else:
            print("[{}] NOTE OFF: {} {}".format(timestamp, self.division, self.note))
            midi_note_off(midi_channel, midi_note)

class OrganShoe(object):
    '''
    Object used to register a pi-organ swell shoe for processing

    Currently the only option for pi-organ notes is to transmit a MIDI volume
    control message on state change, so that action is hard-coded below
    '''
    def __init__(self, name, channel):
        self.name = name
        self.channel = channel
        self.value = None

    def update(self, timestamp, value_new):
        '''Process a swell shoe state update event'''

        scaled_value = value_new >> 1
        assert 0 <= scaled_value < 128

        # Just save the value on the first update
        if self.value is None:
            self.value = scaled_value
            return

        # Send a volume message on change
        if scaled_value != self.value:
            self.value = scaled_value
            print("[{}] VOLUME: {} {}".format(timestamp, self.name, self.value))
            midi_control_change(self.channel, 7, self.value)

# Through some testing, it was found that the RPi can't drive more than about 4
# DIN boards per bank, so split up the banks accordingly

BANK_0_PINS = (
        OrganNote('great', 'C2'),  # Chip 15 D0
        OrganNote('great', 'Db2'),
        OrganNote('great', 'D2'),
        OrganNote('great', 'Eb2'),
        OrganNote('great', 'E2'),
        OrganNote('great', 'F2'),
        OrganNote('great', 'Gb2'),
        OrganNote('great', 'G2'),  # Chip 15 D7
        OrganNote('great', 'Ab2'), # Chip 14 D0
        OrganNote('great', 'A2'),
        OrganNote('great', 'Bb2'),
        OrganNote('great', 'B2'),
        OrganNote('great', 'C3'),
        OrganNote('great', 'Db3'),
        OrganNote('great', 'D3'),
        OrganNote('great', 'Eb3'), # Chip 14 D7
        OrganNote('great', 'E3'),  # Chip 13 D0
        OrganNote('great', 'F3'),
        OrganNote('great', 'Gb3'),
        OrganNote('great', 'G3'),
        OrganNote('great', 'Ab3'),
        OrganNote('great', 'A3'),
        OrganNote('great', 'Bb3'),
        OrganNote('great', 'B3'),  # Chip 13 D7
        OrganNote('great', 'C4'),  # Chip 12 D0
        OrganNote('great', 'Db4'),
        OrganNote('great', 'D4'),
        OrganNote('great', 'Eb4'),
        OrganNote('great', 'E4'),
        OrganNote('great', 'F4'),
        OrganNote('great', 'Gb4'),
        OrganNote('great', 'G4'),  # Chip 12 D7
        OrganNote('great', 'Ab4'), # Chip 11 D0
        OrganNote('great', 'A4'),
        OrganNote('great', 'Bb4'),
        OrganNote('great', 'B4'),
        OrganNote('great', 'C5'),
        OrganNote('great', 'Db5'),
        OrganNote('great', 'D5'),
        OrganNote('great', 'Eb5'), # Chip 11 D7
        OrganNote('great', 'E5'),  # Chip 10 D0
        OrganNote('great', 'F5'),
        OrganNote('great', 'Gb5'),
        OrganNote('great', 'G5'),
        OrganNote('great', 'Ab5'),
        OrganNote('great', 'A5'),
        OrganNote('great', 'Bb5'),
        OrganNote('great', 'B5'),  # Chip 10 D7
        OrganNote('great', 'C6'),  # Chip 9 D0
        OrganNote('great', 'Db6'),
        OrganNote('great', 'D6'),
        OrganNote('great', 'Eb6'),
        OrganNote('great', 'E6'),
        OrganNote('great', 'F6'),
        OrganNote('great', 'Gb6'),
        OrganNote('great', 'G6'),  # Chip 9 D0
        OrganNote('great', 'Ab6'), # Chip 8 D7
        OrganNote('great', 'A6'),
        OrganNote('great', 'Bb6'),
        OrganNote('great', 'B6'),
        OrganNote('great', 'C7'),
        None,                     # Chip 8 D0
        None,
        None,
        )

BANK_PEDAL_PINS = (
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

SWELL_SHOES = (
        OrganShoe('Great', 1),      # Arduino A0
        OrganShoe('Swell', 2),      # Arduino A1
        OrganShoe('Crescendo', 3),  # Arduino A2
    )

# On a MIDIBox DIN board, the load, clock, and data pins are marked RC, SC, and
# SI, respectively

BANKS_74HC165 = {
        'great': (23, 21, 19, BANK_0_PINS),
        #'solo': (37, 38, 40, BANK_1_PINS),
        }


pin_states = {}
for bank, (pin_load, pin_clock, pin_data, pins) in BANKS_74HC165.items():
    # Initialize all pins to "open"
    pin_states[bank] = [1] * len(pins)

    # Initialize GPIO pins
    GPIO.setup(pin_load, GPIO.OUT)
    GPIO.output(pin_load, GPIO.HIGH)
    GPIO.setup(pin_clock, GPIO.OUT)
    GPIO.output(pin_clock, GPIO.LOW)
    GPIO.setup(pin_data, GPIO.IN)

pedal_board = serial.Serial('/dev/ttyACM0', timeout=0)
pin_states['pedal'] = [1] * len(BANK_PEDAL_PINS)
pedal_state_new = 0xFFFF

try:
    while True:
        # TODO: Zip the bank processing together since the longest operations, the GPIO
        # functions, can be done in parallel for each bank.  The banks currently defined can
        # all be processed in about 3ms, so it's good enough for now
        for bank, (pin_load, pin_clock, pin_data, pins) in BANKS_74HC165.items():
            gpio_load(pin_load)
            for pin_idx, pin in enumerate(pins):
                state_new = GPIO.input(pin_data)
                if state_new != pin_states[bank][pin_idx]:
                    pin_states[bank][pin_idx] = state_new
                    if pin is not None:
                        pin.state_change(time.time(), state_new)
                gpio_tick(pin_clock)

        # Get the most recent pedal board state
        # Note: The following algorithm assumes there was time
        #       to send at least one full message since the last read
        new_data = pedal_board.read(256)
        try:
            # Find the last CRLF, which indicates the latest end of a full message
            last_newline = new_data.rfind(b'\r')

            # Find the next CRLF from the end to get the beginning of the last full message
            second_last_newline = new_data[:last_newline].rfind(b'\n')

            # Extract the last full message
            newest_data = new_data[second_last_newline+1:last_newline].decode()

            # Parse out the comma-separated hex data
            (pedals, shoe_0, shoe_1, shoe_2) = newest_data.split(",")
            pedal_state_new = int(pedals, 16)
            shoe_state_new = (int(shoe_0, 16), int(shoe_1, 16), int(shoe_2, 16))
        except:
            pass

        # If the newset data is valid, process it
        else:
            # Process pedal board pins
            for pin_idx, pin in enumerate(BANK_PEDAL_PINS):
                state_new = (pedal_state_new >> pin_idx) & 1
                if state_new != pin_states['pedal'][pin_idx]:
                    pin_states['pedal'][pin_idx] = state_new
                    if pin is not None:
                        pin.state_change(time.time(), state_new)

            # Process swell shoes
            for shoe_idx, shoe in enumerate(SWELL_SHOES):
                shoe.update(time.time(), shoe_state_new[shoe_idx])

except KeyboardInterrupt:
    print("Exit Signal Received")

finally:
    print("Cleaning up..."),
    GPIO.cleanup()
    client.disconnect(outport, 'system:playback_1')
    client.deactivate()
    pedal_board.close()
    print("Done")
