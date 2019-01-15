#!/usr/bin/python3

import RPi.GPIO as gpio
import time

DIN_LOAD = 23
DIN_CLK = 21
DIN_DATA = 19

gpio.setmode(gpio.BOARD)

gpio.setup(DIN_LOAD, gpio.OUT)
gpio.output(DIN_LOAD, gpio.LOW)
gpio.setup(DIN_CLK, gpio.OUT)
gpio.output(DIN_CLK, gpio.LOW)
gpio.setup(DIN_DATA, gpio.IN)

def start():
    gpio.output(DIN_LOAD, gpio.LOW)
    time.sleep(0.0001)
    gpio.output(DIN_LOAD, gpio.HIGH)
    time.sleep(0.0001)

def tick():
    gpio.output(DIN_CLK, gpio.HIGH)
    time.sleep(0.00001)
    gpio.output(DIN_CLK, gpio.LOW)
    time.sleep(0.00001)

while True:
    for spinner in ('\\', '|', '/', '-',):
        value=0 
        start()
        for bit in range(64):
            value |= gpio.input(DIN_DATA) << bit
            tick()

        print spinner, bin(value)
        time.sleep(0.1)

