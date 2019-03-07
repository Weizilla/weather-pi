import argparse
import time
from decimal import Decimal

import boto3
from adafruit_bme280 import Adafruit_BME280_I2C
from adafruit_character_lcd.character_lcd_rgb_i2c import Character_LCD_RGB_I2C
from board import SCL
from board import SDA
from busio import I2C


READING_PERIOD_SEC = 60 * 5


class Weather(object):
    def __init__(self, location):
        i2c = I2C(SCL, SDA)
        self.sensor = Adafruit_BME280_I2C(i2c, address=0x76)
        self.lcd = Character_LCD_RGB_I2C(i2c, 16, 2)
        self.location = location
        self.temperature = None
        self.pressure = None
        self.humidity = None
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        self.table = dynamodb.Table("weather")

    def start(self):
        try:
            self.lcd.clear()
            self.lcd.color = [100, 0, 0]
            self.lcd.backlight = True

            while True:
                self._read_sensor()
                self._update_lcd()
                self._record_reading()
                time.sleep(READING_PERIOD_SEC)
        except KeyboardInterrupt:
            pass

    def stop(self):
        self.lcd.clear()
        self.lcd.backlight = False

    def _read_sensor(self):
        self.temperature = self.sensor.temperature
        self.pressure = self.sensor.pressure
        self.humidity = self.sensor.humidity

    def _update_lcd(self):
        temp_f = self.temperature * 1.8 + 32
        msg = "Temp = {0:0.3f}\nHumidity = {1:0.2f} %".format(temp_f, self.humidity)
        self.lcd.message = msg

    def _record_reading(self):
        epoch = int(time.time())
        item = {
            "reading_date": time.strftime("%Y-%m-%d", time.gmtime(epoch)),
            "reading_time": epoch,
            "location": self.location,
            "location_time": "{l}-{e}".format(l=self.location, e=epoch),
            "time_location": "{e}-{l}".format(l=self.location, e=epoch),
        }

        if self.temperature:
            item["temperature"] = Decimal(str(self.temperature))

        if self.humidity:
            item["humidity"] = Decimal(str(self.humidity))

        if self.pressure:
            item["pressure"] = Decimal(str(self.pressure))

        self.table.put_item(Item=item)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("location", help="name of location")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    weather = Weather(location=args.location)
    weather.start()
    weather.stop()
