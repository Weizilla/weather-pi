import time
import argparse
import board
import busio
import adafruit_bme280
import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd

class Weather(object):
    def __init__(self, debug=False):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
        self.lcd = character_lcd.Character_LCD_RGB_I2C(i2c, 16, 2)
        self.debug = debug
        self.backlight = True
        self.button = True

    def read_sensor(self):
        self.temp = self.sensor.temperature *1.8 + 32
        self.pressure = self.sensor.pressure
        self.humidity = self.sensor.humidity

    def update_lcd(self):
        msg = "Temp = {0:0.3f}\nHumidity = {1:0.2f} %".format(self.temp, self.humidity)
        self.lcd.message = msg

    def check_button(self):
        if self.lcd.select_button:
            if self.button:
                self.backlight = not self.backlight
                if self.backlight:
                    self.lcd.color = [100, 0, 0]
                else:
                    self.lcd.backlight = False
            self.button = False
        else:
            self.button = True

    def start(self, debug=False):
        try:
            self.lcd.clear()
            self.lcd.color = [100, 0, 0]

            self.button = True
            self.backlight = True

            while True:
                self.read_sensor()
                self.update_lcd()
                self.check_button()
                time.sleep(1)

        except KeyboardInterrupt:
            pass

    def stop(self):
        self.lcd.clear()
        self.lcd.backlight = False

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    return parser.parse_args()

if __name__ == "__main__":
    args = parseArgs()
    weather = Weather(debug=args.debug)
    weather.start()
    weather.stop()
