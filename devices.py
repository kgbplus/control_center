from machine import Pin, SPI
from ili9341 import Display
from xpt2046 import Touch
from xglcd_font import XglcdFont

from sensors import DHTSensor, RemoteDHTSensor


class DeviceManager:
    def __init__(self, debug=False) -> None:
        self.spi1 = SPI(1, baudrate=40000000, sck=Pin(14), mosi=Pin(13))
        self.display = Display(self.spi1, dc=Pin(4), cs=Pin(16), rst=Pin(17))
        self.font = XglcdFont('fonts/EspressoDolce18x24.c', 18, 24)

        self.spi2 = SPI(2, baudrate=1000000, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
        self.touch = Touch(self.spi2, cs=Pin(5), int_pin=Pin(15), int_handler=self.touchscreen_press, x_min=310, y_min=360, x_max=1540, y_max=1700)
        self._touch_xy = None
        self.debug_dot = bytearray(
            b'\x00\x00\x07\xE0\xF8\x00\x07\xE0\x00\x00\x07\xE0\xF8\x00\xF8\x00\xF8\x00\x07\xE0\xF8\x00\xF8\x00\xF8\x00\xF8\x00\xF8\x00\x07\xE0\xF8\x00\xF8\x00\xF8\x00\x07\xE0\x00\x00\x07\xE0\xF8\x00\x07\xE0\x00\x00')

        self.dht_sensor = RemoteDHTSensor(self.spi2, ce_pin=27, csn_pin=26)

        self.debug = debug

    def touchscreen_press(self, x: int, y: int) -> None:
        # X needs to be flipped
        x = (self.display.width - 1) - x
        self._touch_xy = (x, y)

    def touch_pressed(self) -> bool:
        return self._touch_xy is not None

    def get_touch_coordinates(self) -> tuple:
        x, y = self._touch_xy
        self._touch_xy = None
        if self.debug:
            self.display.draw_sprite(self.debug_dot, x - 2, y - 2, 5, 5)
        return x, y

    def shutdown(self) -> None:
        self.display.cleanup()
