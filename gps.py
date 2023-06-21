from machine import Pin, UART, I2C, Timer
from ssd1306 import SSD1306_I2C
from micropyGPS import MicropyGPS

import utime, time

i2c=I2C(0,sda=Pin(0), scl=Pin(1), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)
# ref: https://dev.webonomic.nl/blinking-a-led-on-the-raspberry-pi-pico-w/comment-page-1
led = machine.Pin("LED", Pin.OUT)
gpsModule = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))
print(gpsModule)
mgps = MicropyGPS(+9)

buff = bytearray(255)

TIMEOUT = False
FIX_STATUS = False

latitude = ""
longitude = ""
satellites = ""
GPStime = ""

timer = Timer()

def ledblink(timer):
    led.toggle()

timer.init(freq=2.5, mode=Timer.PERIODIC, callback=ledblink)

def getGPS(gpsModule):
    global FIX_STATUS, TIMEOUT, latitude, longitude, satellites, GPStime
    
    timeout = time.time() + 8 
    while True:
        buff = gpsModule.readline()
        if buff == None:
            continue
        try:
            string = str(buff, 'utf-8')
        except UnicodeError:
            continue
        for i in string:
            mgps.update(i)
        latitude = mgps.latitude_string()
        longitude = mgps.longitude_string()
        if latitude == '0" 0.0\' M' or longitude == '0" 0.0\' W':
            TIMEOUT = True
            break
        satellites = str(mgps.satellites_in_use)
        GPStime = mgps.timestamp_string()
        
        FIX_STATUS = True
        break
                
        if (time.time() > timeout):
            TIMEOUT = True
            break
        utime.sleep_ms(500) 

while True:
    getGPS(gpsModule)

    if(FIX_STATUS == True):
        print("Printing GPS data...")
        print(" ")
        print("Latitude: "+latitude)
        print("Longitude: "+longitude)
        print("Satellites: " +satellites)
        print("Time: "+GPStime)
        print("----------------------")
        
        oled.fill(0)
        oled.text("Lat: "+latitude, 0, 0)
        oled.text("Lng: "+longitude, 0, 10)
        oled.text("Satellites: "+satellites, 0, 20)
        oled.text("Time: "+GPStime, 0, 30)
        oled.show()
        
        FIX_STATUS = False
        
    if(TIMEOUT == True):
        oled.fill(0)
        oled.text("No GPS data is", 0, 0)
        oled.text("found.", 0, 10)
        oled.show()
        print("No GPS data is found.")
        TIMEOUT = False
