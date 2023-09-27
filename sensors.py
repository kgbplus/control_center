import dht
import ustruct as struct
from machine import Pin
from nrf24l01 import *


class DHTSensor:
    def __init__(self, pin) -> None:
        self.sensor = dht.DHT11(pin)

    def read(self):
        self.sensor.measure()
        temp = self.sensor.temperature()
        hum = self.sensor.humidity()
        return temp, hum
    

class RemoteDHTSensor:
    def __init__(self, spi, ce_pin, csn_pin) -> None:
        self.pipes = (b"1Node", b"2Node")
        csn = Pin(csn_pin, mode=Pin.OUT, value=1)
        ce = Pin(ce_pin, mode=Pin.OUT, value=0)
        self.nrf = NRF24L01(spi, csn, ce, channel=115, payload_size=8)
        self.nrf.set_power_speed(POWER_3, SPEED_250K)
        self.nrf.open_rx_pipe(1, self.pipes[0])
        self.nrf.start_listening()

    def read(self):
        temp, hum = None, None
        if self.nrf.any():
            while self.nrf.any():
                buf = self.nrf.recv()
                temp, hum = struct.unpack("ff", buf)
        return temp, hum
