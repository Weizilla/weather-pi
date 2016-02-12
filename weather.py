import time
from Adafruit_BME280 import *
import Adafruit_CharLCD as LCD
import argparse

class Weather(object):
    def __init__(self, debug=False):
        self.sensor = BME280(mode=BME280_OSAMPLE_8)
        self.lcd = LCD.Adafruit_CharLCDPlate()
        self.debug = debug

    def read_sensor(self):
        self.temp = self.sensor.read_temperature() * 1.8 + 32
        self.pressure = self.sensor.read_pressure() / 100
        self.humidity = self.sensor.read_humidity()

    def update_lcd(self):
        msg = "Temp = {0:0.3f}\nHumidity = {1:0.2f} %".format(self.temp, self.humidity)
        self.lcd.set_cursor(0,0)
        self.lcd.message(msg)

    def check_button(self):
        if self.lcd.is_pressed(LCD.SELECT):
            if self.button:
                self.backlight = not self.backlight
                if self.backlight:
                    self.lcd.set_color(1.0, 0.0, 0.0)
                else:
                    self.lcd.set_backlight(0)
            self.button = False
        else:
            self.button = True

    def start(self, debug=False): 
        try:
            self.lcd.clear()
            self.lcd.set_color(1.0, 0.0, 0.0)

            self.button = True
            self.backlight = True

            while(True): 
                self.read_sensor()
                self.update_lcd()
                self.check_button()
                time.sleep(1)

        except KeyboardInterrupt:
            pass

    def stop(self):
        self.lcd.clear()
        self.lcd.set_backlight(0)

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    return parser.parse_args()

if __name__ == "__main__":
    args = parseArgs()
    weather = Weather(debug=args.debug)
    weather.start()
    weather.stop()
