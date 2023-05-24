import utime
import network 
import urequests 
import ntptime
from machine import I2C, Pin, Timer
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd



wlan = network.WLAN(network.STA_IF)
wlan.active(True)

ssid = ""
password = ""
my_ip = ""

request_url = "https://api.weatherapi.com/v1/current.json?key="


c = 0

while True:
    try:
        
        I2C_ADDR     = 39
        I2C_NUM_ROWS = 2
        I2C_NUM_COLS = 16

        i2c = I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)
        lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)
        
        
        wlan.connect(ssid, password)
        
        lcd.move_to(0,0)
        lcd.putstr("Temp Sensor")
        utime.sleep(1)
        
        for x in range(16):
            lcd.move_to(x,1)
            lcd.putstr(".")
            utime.sleep(.1)
        
        lcd.clear()
        
        print(wlan.ifconfig())
        my_ip = wlan.ifconfig()[0]
        
        
        ntptime.settime()
        
        dt = utime.localtime()
        
        print(utime.localtime(utime.mktime(utime.localtime()) + 19800))

        lcd.move_to(0,0)
        lcd.putstr("Connected To")
        lcd.move_to(0,1)
        lcd.putstr(ssid)
        print("Connected to " + ssid + " successfully!")
        utime.sleep(3)
        lcd.clear()

        print("My IP - " + my_ip)
        lcd.move_to(0,0)
        lcd.putstr("My IP Address")
        lcd.move_to(0,1)
        lcd.putstr(my_ip)
        

        c = 0;
        break;
    
    except:
        c += 1
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("Whoops!")
        print("Something Went Wrong!")
        utime.sleep(1)
        lcd.move_to(0, 1)
        lcd.putstr("Attempt #" + str(c))
        utime.sleep(3)
        continue




def read_temp():
    sensor_temp = machine.ADC(4)
    conversion_factor = 3.3 / (65535)
    reading = sensor_temp.read_u16() * conversion_factor 
    temperature = 27 - (reading - 0.706)/0.001721
    return temperature

def get_api_data():
    r = urequests.get(request_url)
    print(r.json())
    return r.json()

def set_day_status(Source):
    current_time = utime.localtime(utime.mktime(utime.localtime()) + 19800)
    
    d = get_api_data()
    string_temp = str(round(float(d['current']['temp_c']))) + "->" +  str(round(float(d['current']['feelslike_c'])))
    string_cond = str(d['current']['condition']['text'])
    string_humidity = str(d['current']['humidity'])
    string_cloudy = str(d['current']['cloud'])
    
    string_date = str(current_time[1]) + "/" +  str(current_time[2])
    
    print("T:"+ string_temp + " " + "D:" + string_date)
    print("H:" + string_humidity)
    
    lcd.move_to(0,0)
    lcd.putstr("T:"+ string_temp + " " + "D:" + string_date)
    lcd.move_to(0,1)
    lcd.putstr("H:" + string_humidity + " " + "C:" + string_cloudy +  " " + string_cond)
    

def set_temp_status(Source):
    temperature = float(read_temp())
    current_time = utime.localtime(utime.mktime(utime.localtime()) + 19800)
    
    formatted_temperature = "{:.1f}".format(temperature)
    string_temperature = str("Temp:" + formatted_temperature)
    string_date = "D:" + str(current_time[1]) + "/" +  str(current_time[2])

    print(string_temperature + " " + string_date)

    lcd.move_to(0, 0)
    lcd.putstr(string_temperature + " " + string_date)
      

set_day_status("")
status_timer = Timer(period=1000*60*15, mode=Timer.PERIODIC, callback=set_day_status)
