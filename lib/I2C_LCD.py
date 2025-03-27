import time
import board
import busio
from lcd.lcd import LCD
from lcd.i2c_pcf8574_interface import I2CPCF8574Interface

MASK_RS = 0x01
MASK_RW = 0x02
MASK_E = 0x04
SHIFT_BACKLIGHT = 3
SHIFT_DATA = 4

class I2CLcd(LcdApi):
    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr

        while not self.i2c.try_lock():
            pass

        self.i2c.writeto(self.i2c_addr, bytes([0]))
        time.sleep(0.02)  # 20ms en segundos
        self.hal_write_init_nibble(self.LCD_FUNCTION_RESET)
        time.sleep(0.005)
        self.hal_write_init_nibble(self.LCD_FUNCTION_RESET)
        time.sleep(0.001)
        self.hal_write_init_nibble(self.LCD_FUNCTION_RESET)
        time.sleep(0.001)
        self.hal_write_init_nibble(self.LCD_FUNCTION)
        time.sleep(0.001)

        self.hal_backlight_on()  # Encender backlight al iniciar

        self.i2c.unlock()

        LcdApi.__init__(self, num_lines, num_columns)
        cmd = self.LCD_FUNCTION
        if num_lines > 1:
            cmd |= self.LCD_FUNCTION_2LINES
        self.hal_write_command(cmd)
        time.sleep(0.5)  # Espera antes de mostrar texto

    def hal_write_init_nibble(self, nibble):
        byte = ((nibble >> 4) & 0x0F) << SHIFT_DATA
        while not self.i2c.try_lock():
            pass
        self.i2c.writeto(self.i2c_addr, bytes([byte | MASK_E]))
        self.i2c.writeto(self.i2c_addr, bytes([byte]))
        self.i2c.unlock()

    def hal_backlight_on(self):
        while not self.i2c.try_lock():
            pass
        self.i2c.writeto(self.i2c_addr, bytes([0x08]))  # 0x08 enciende el backlight
        self.i2c.unlock()

    def hal_backlight_off(self):
        while not self.i2c.try_lock():
            pass
        self.i2c.writeto(self.i2c_addr, bytes([0x00]))
        self.i2c.unlock()

    def hal_write_command(self, cmd):
        while not self.i2c.try_lock():
            pass
        byte = ((self.backlight << SHIFT_BACKLIGHT) | (((cmd >> 4) & 0x0F) << SHIFT_DATA))
        self.i2c.writeto(self.i2c_addr, bytes([byte | MASK_E]))
        self.i2c.writeto(self.i2c_addr, bytes([byte]))
        byte = ((self.backlight << SHIFT_BACKLIGHT) | ((cmd & 0x0F) << SHIFT_DATA))
        self.i2c.writeto(self.i2c_addr, bytes([byte | MASK_E]))
        self.i2c.writeto(self.i2c_addr, bytes([byte]))
        self.i2c.unlock()
        if cmd <= 3:
            time.sleep(0.005)

    def hal_write_data(self, data):
        while not self.i2c.try_lock():
            pass
        byte = (MASK_RS | (self.backlight << SHIFT_BACKLIGHT) | (((data >> 4) & 0x0F) << SHIFT_DATA))
        self.i2c.writeto(self.i2c_addr, bytes([byte | MASK_E]))
        self.i2c.writeto(self.i2c_addr, bytes([byte]))
        byte = (MASK_RS | (self.backlight << SHIFT_BACKLIGHT) | ((data & 0x0F) << SHIFT_DATA))
        self.i2c.writeto(self.i2c_addr, bytes([byte | MASK_E]))
        self.i2c.writeto(self.i2c_addr, bytes([byte]))
        self.i2c.unlock()