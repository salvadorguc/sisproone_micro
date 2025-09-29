# lcd16x2.py  (driver mínimo para LCD 1602 con PCF8574)
from machine import I2C
import time

LCD_BACKLIGHT = 0x08
ENABLE = 0x04
RS = 0x01

class LCD1602:
    def __init__(self, i2c: I2C, addr=0x27):
        self.i2c = i2c
        self.addr = addr
        self.bl = LCD_BACKLIGHT
        time.sleep_ms(50)
        self._write4(0x03<<4); time.sleep_ms(5)
        self._write4(0x03<<4); time.sleep_us(150)
        self._write4(0x03<<4)
        self._write4(0x02<<4)      # 4-bit
        self.command(0x28)         # 2 lines, 5x8
        self.command(0x08)         # display off
        self.command(0x01)         # clear
        time.sleep_ms(2)
        self.command(0x06)         # entry
        self.command(0x0C)         # display on, cursor off

    def _strobe(self, data):
        self.i2c.writeto(self.addr, bytes([data | ENABLE | self.bl]))
        time.sleep_us(500)
        self.i2c.writeto(self.addr, bytes([(data & ~ENABLE) | self.bl]))
        time.sleep_us(100)

    def _write4(self, data):
        self.i2c.writeto(self.addr, bytes([data | self.bl]))
        self._strobe(data)

    def command(self, cmd):
        self._write4(cmd & 0xF0)
        self._write4((cmd<<4) & 0xF0)

    def write_char(self, ch):
        d = ord(ch)
        self._write4((d & 0xF0) | RS)
        self._write4(((d<<4) & 0xF0) | RS)

    def clear(self):
        self.command(0x01); time.sleep_ms(2)

    def home(self):
        self.command(0x02); time.sleep_ms(2)

    def set_cursor(self, col, row):
        addr = col + (0x40 if row else 0x00)
        self.command(0x80 | addr)

    def print(self, s):
        for ch in s:
            self.write_char(ch)

