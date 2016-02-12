import time
from Adafruit_BME280 import *
import Adafruit_CharLCD as LCD

sensor = BME280(mode=BME280_OSAMPLE_8)
lcd = LCD.Adafruit_CharLCDPlate()

button = False
backlight = True

lcd.clear()
lcd.set_color(1.0, 0.0, 0.0)

while(True): 
    degrees = sensor.read_temperature() * 1.8 + 32
    pascals = sensor.read_pressure()
    hectopascals = pascals / 100
    humidity = sensor.read_humidity()

    lcd.message("Temp = {0:0.3f}\nHumidity = {1:0.2f} %"
        .format(degrees, humidity))

    #print 'Timestamp = {0:0.3f}'.format(sensor.t_fine)
    #print 'Temp      = {0:0.3f} deg C'.format(degrees)
    #print 'Pressure  = {0:0.2f} hPa'.format(hectopascals)
    #print 'Humidity  = {0:0.2f} %'.format(humidity)

    try:
        time.sleep(1)
    except:
        lcd.clear()
        break
