import argparse
import time
from decimal import Decimal

from boto3.session import Session
import boto3
from adafruit_bme280 import Adafruit_BME280_I2C
from adafruit_character_lcd.character_lcd_rgb_i2c import Character_LCD_RGB_I2C
from board import SCL
from board import SDA
from busio import I2C
from elasticsearch import Elasticsearch


READING_PERIOD_SEC = 60 * 10
DYNAMODB_TABLE = "weather"
ES_INDEX_NAME = "weather"
ES_DOC_TYPE = "weather"
ES_HOST = "192.168.2.156"


class Weather(object):
    def __init__(self, location, enable_lcd, test):
        self.location = location
        self.test = test
        self.temperature = None
        self.pressure = None
        self.humidity = None

        session = Session(profile_name="weather")
        dynamodb = session.resource("dynamodb", region_name="us-east-1")
        self.table = dynamodb.Table(DYNAMODB_TABLE)
        self.es = Elasticsearch(hosts=[ES_HOST])

        i2c = I2C(SCL, SDA)
        self.sensor = Adafruit_BME280_I2C(i2c, address=0x76)
        self.lcd = Character_LCD_RGB_I2C(i2c, 16, 2) if enable_lcd else None

    def start(self):
        try:
            if self.lcd:
                self.lcd.clear()
                self.lcd.color = [100, 0, 0]
                self.lcd.backlight = True

            while True:
                if self.test:
                    print("Starting test...")

                self._read_sensor()
                self._update_lcd()
                self._write_dynamodb()
                self._write_elastic_search()

                if self.test:
                    print("Test completed")
                    break

                time.sleep(READING_PERIOD_SEC)
        except KeyboardInterrupt:
            pass

    def stop(self):
        if self.lcd:
            self.lcd.clear()
            self.lcd.backlight = False

    def _read_sensor(self):
        self.epoch = int(time.time())
        self.temperature = self.sensor.temperature
        self.pressure = self.sensor.pressure
        self.humidity = self.sensor.humidity
        self.time_location = "{e}-{l}".format(l=self.location, e=self.epoch)
        if self.test:
            print("Readings: temp={t} pressure={p} humidity={h}".format(t=self.temperature, p=self.pressure, h=self.humidity))

    def _update_lcd(self):
        if self.lcd:
            temp_f = self.temperature * 1.8 + 32
            msg = "Temp = {0:0.3f}\nHumidity = {1:0.2f} %".format(temp_f, self.humidity)
            self.lcd.message = msg

    def _write_dynamodb(self):
        item = {
            "reading_date": time.strftime("%Y-%m-%d", time.gmtime(self.epoch)),
            "reading_time": self.epoch,
            "location": self.location,
            "location_time": "{l}-{e}".format(l=self.location, e=self.epoch),
            "time_location": "{e}-{l}".format(l=self.location, e=self.epoch),
        }

        if self.temperature:
            item["temperature"] = Decimal(str(self.temperature))

        if self.humidity:
            item["humidity"] = Decimal(str(self.humidity))

        if self.pressure:
            item["pressure"] = Decimal(str(self.pressure))

        if self.test:
            print("Dynamodb table={t} status={s}".format(t=self.table.table_name, s=self.table.table_status))
        else:
            self.table.put_item(Item=item)

    def _write_elastic_search(self):
        reading = {
            "location": self.location,
            "reading_time": self.epoch * 1000,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "pressure": self.pressure,
            "id": self.time_location,
        }

        if self.test:
            print("Elasticsearch host={h} ping={p} info={i}".format(h=ES_HOST, p=self.es.ping(), i=self.es.info()))
        else:
            self.es.index(index=ES_INDEX_NAME, doc_type=ES_DOC_TYPE, id=self.time_location, body=reading)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("location", help="name of location")
    parser.add_argument("--lcd", action="store_true", help="Turn on LCD")
    parser.add_argument("--test", action="store_true", help="Test sensor and connections")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    weather = Weather(location=args.location, enable_lcd=args.lcd, test=args.test)
    weather.start()
    weather.stop()
