from wifi_manager import WifiManager
import machine
import time
import ujson
import ubinascii
import network
from umqtt.simple import MQTTClient # ตรวจสอบว่ามีไฟล์ umqtt/simple.py ใน ESP32
import struct
import ujson as json
import requests
import os
import wash
 
def resetWIFI():
        coder_version = {"version":0}
        f = open('version.json','w') 
        f.write(json.dumps(coder_version)) 
        f.close()
        if check_file_exists('wifi.dat') :
            os.remove('wifi.dat') 

        
def read_credentials(selffle):
        lines = []
        try:
            with open(selffle) as file:
                lines = file.readlines()
        except Exception as error:
            if selffle:
                print(error)
            pass
        profiles = {}
        for line in lines:
            ssid, password = line.strip().split(';')
            profiles['ssid'] = ssid
            profiles['password'] = password
        return profiles
def check_file_exists(filename):
    try:
        os.stat(filename)
        return True
    except OSError:
        return False
    
def get_device_serial_number():
        try:
            import machine
            import ubinascii
            return ubinascii.hexlify(machine.unique_id()).decode('utf-8').upper()
        except :
            return "UNKNOWN_SERIAL"
        
led = machine.Pin(2, machine.Pin.OUT, value=0)
debounce_delay = 1000
timer_direction = 0

def button_pressed(pin):
    global timer_direction
    time.sleep_ms(debounce_delay)
    now = time.ticks_ms()
    print("button_pressed",pin.value(),timer_direction,now,debounce_delay)
    if pin.value() == 0:
            led.value(1)
            timer_direction += 1
    if pin.value() == 1:
            led.value(0)
            timer_direction = 0

    if timer_direction == 1 and pin.value() == 0 :
        wash.main() 
        for _ in range(3):
            led.value(0)
            time.sleep(0.5)
            led.value(1)
            time.sleep(0.5)
        resetWIFI()
        #led.value(0) 
        machine.reset()
        print("######Rebooting...")
    


reset_button = machine.Pin(0, mode=machine.Pin.IN, pull=machine.Pin.PULL_UP)
reset_button.irq(trigger=machine.Pin.IRQ_FALLING, handler=button_pressed)

            
def interpret_status_data(data):
    try:
        url = str('http://34.124.162.209/api-wash/') +str(get_device_serial_number())
        response = requests.get(url , headers={'Content-Type': 'application/json'})
        data_json = response.json()
        if 'command' in data_json :
            
            if data_json['command']['key'] == 'update_wash' and data_json['command']['value']  :
                urls = str(data_json['command']['value'])
                response_update = requests.get(urls)
                print(response_update.status_code)
                if response_update.status_code == 200 :
                    print("update_wash")
                    f = open('wash.txt','w')
                    f.write(str(response_update.text))
                    f.close()
                    time.sleep(5)
                    print("success")
                data = {}
                requests.put(url+str('/command') , data=json.dumps(data), headers={'Content-Type': 'application/json'})
                print("reboot")
                return machine.reset()
                
            if data_json['command']['key'] == 'update_main' and data_json['command']['value']  :
                urls = str(data_json['command']['value'])
                response_update = requests.get(urls)
                print(response_update.status_code)
                if response_update.status_code == 200 :
                    print("update_main")
                    f = open('main.txt','w')
                    f.write(str(response_update.text))
                    f.close()
                    time.sleep(5)
                    print("success")
                data = {}
                requests.put(url+str('/command') , data=json.dumps(data), headers={'Content-Type': 'application/json'})
                print("reboot")
                return machine.reset()
            
            
            if data_json['command']['key'] == 'reset_error' :
                txt = wash.reset_error()
                print(txt)
                time.sleep(1)
                data = {}
                requests.put(url+str('/command') , data=json.dumps(data), headers={'Content-Type': 'application/json'})
                return print("reset_error")
            
            if data_json['command']['key'] == 'get_status' :
                txt = wash.get_machine_status()
                print(txt)
                data = {}
                requests.put(url+str('/command') , data=json.dumps(data), headers={'Content-Type': 'application/json'})
                return print("get_statement")
                
            if data_json['command']['key'] == 'menu' and data_json['command']['value'] :
                txt = wash.select_program(int(data_json['command']['value']))
                data = {}
                requests.put(url+str('/command') , data=json.dumps(data), headers={'Content-Type': 'application/json'})
                return print(txt)
                
            if data_json['command']['key'] == 'coins' and data_json['command']['value'] :
                txt = wash.add_coins(int(data_json['command']['value']))
                data = {}
                requests.put(url+str('/command') , data=json.dumps(data), headers={'Content-Type': 'application/json'})
                time.sleep(1)
                return print(txt)
                
            if data_json['command']['key'] == 'start' :
                txt = wash.start_operation()
                data = {}
                requests.put(url+str('/command') , data=json.dumps(data), headers={'Content-Type': 'application/json'})
                time.sleep(1)
                return print(txt)
                
            if data_json['command']['key'] == 'stop' :
                txt = wash.stop_operation()
                data = {}
                requests.put(url+str('/command') , data=json.dumps(data), headers={'Content-Type': 'application/json'})
                time.sleep(1)
                return print(txt)

            if data_json['command']['key'] == 'command' and data_json['command']['address'] :
                txt = wash.sendcommand(int(data_json['command']['address']),int(data_json['command']['value']))
                data = {}
                requests.put(url+str('/command') , data=json.dumps(data), headers={'Content-Type': 'application/json'})
                time.sleep(1)
                return print(txt)
            
            if data_json['command']['key'] == 'reboot' :
                data = {}
                requests.put(url+str('/command') , data=json.dumps(data), headers={'Content-Type': 'application/json'})
                time.sleep(5)
                return machine.reset()
                
        requests.put(url , data=json.dumps(data), headers={'Content-Type': 'application/json'})
        print(f"Success sending status to API")
    except :
        url = str('http://34.124.162.209/api-wash/') +str(get_device_serial_number())
        requests.put(url , data=json.dumps(data), headers={'Content-Type': 'application/json'})
        print(f"Error occurred while sending status data to API")
        
# --- WIFI ---
WiFIManager = WifiManager()
WiFIManager.connect()
checkCnnect = 0
while True:
        if WiFIManager.is_connected():
            print('Connected to WiFi!')
            break
        else:
            if checkCnnect >= 10:
                print('Resetting WiFi...')
                resetWIFI()
                time.sleep(1)
                machine.reset()
            if check_file_exists() == False :
                machine.reset()
            print('Error connecting to WiFi!',checkCnnect) 
            checkCnnect+=1
            time.sleep(10)

led.value(1)
print(str(WiFIManager.get_address()[0]))
if str(WiFIManager.get_address()[0]) == '0.0.0.0' :
        print('Rebooting due to no IP address')
        led.value(0)
        machine.reset()

while True:
  try:
    led.value(1)
    wash_status = json.loads(wash.get_machine_status())
    data = {"ip":str(WiFIManager.get_address()[0]),"client_id":get_device_serial_number(),"status":wash_status}
    interpret_status_data(data)
    led.value(0)
    time.sleep(1)
  except :
    machine.reset()