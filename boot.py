import network
import utime as time
import Paanaak
from machine import Pin
import esp32


wlan = network.WLAN(network.STA_IF) # create station interface
wlan.active(True)       # activate the interface
wlan.connect('FTTH_TANOMA', '1qazxsw2$$%%') # connect to an AP
while not wlan.isconnected():
    print("connecting...")
    time.sleep(1)
print("connected to wifi")
device=Paanaak.PaanaakDevice(secret_key="5e1c175a-d830-42b8-8ac2-3627f5cff818")
#this method adds a sensor with name and type(float,bool,string)
device.add_sensor(name="temperature",data_type="float")
device.add_sensor(name="power",data_type="bool")
device.add_sensor(name="status",data_type="str")
#this method create and send and http request to cloud and get the 
# current state of relays as a bit array
while(True):
    tf = esp32.raw_temperature()
    tc = (tf-32.0)/1.8
    response=device.send_sensors_and_relays(    
        {
            "temperature": tc,
            "power":True,        
        },state="10")
    print('response:',response)
    if(response['error']):
        print("error : ",response.message)
    else:
        print("Relays:",response['Relays'])
        p18 = Pin(18, Pin.OUT)    # LED1
        p19 = Pin(19, Pin.OUT)    # LED2
        if(response['Relays'][0]==1):
            p18.on()
        else:
            p18.off()
        if(response['Relays'][1]==1):
            p19.on()
        else:
            p19.off()
        time.sleep(120)
        

