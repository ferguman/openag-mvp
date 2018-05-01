#Check sensors and log to file
from sys import path
import time
import datetime
from si7021 import *
from logData import logData
from atlasPH import *
from ds18b20 import *
from send_mqtt_data import send_sensor_data_via_mqtt

path.append('/opt/mvp/config')
from config import device_1, device_2
#from config import enable_mqtt, mqtt_publish_sensor_readings 

def start_sensor_data_logger(mqtt_client):

   si=si7021()

   while True:

      try:
         date_time = datetime.datetime.utcnow()
         temp = si.getTempC()
         logData("si7021_top", "Success", "temperature", "air", "{:+.1f}".format(temp), "celsius", '')
         send_sensor_data_via_mqtt(device_1, mqtt_client, "si7021_top", "temperature", "air", 
                                   "{:+.1f}".format(temp), "celsius", date_time)
      except Exception as e:
         logData("si7021_top", "Failure", "temperature", "air", '', "celsius", str(e))

      try:
         humid = si.getHumidity()
         logData("si7021_top", "Success", "humidity", "air", "{:+.1f}".format(humid), 
                 "percentage", '')
         send_sensor_data_via_mqtt(device_1, mqtt_client, "si7021_top", "humidity", "air", 
                                   "{:+.1f}".format(temp), "percentage", date_time)
      except Exception as e:
         logData("si7921_top", "Failure", "humidity", "air", '', "percentage", str(e))

      try:
         ph = atlasPH().getPH()
         logData("PH", "Success", "ph", "water", "{:+.2f}".format(ph), "scalar", '')
         send_sensor_data_via_mqtt(device_1, mqtt_client, "PH", "ph", "water", 
                                   "{:+.1f}".format(temp), "none", date_time)
      except Exception as e:
         logData("PH", "Failure", "ph", "water", '', "scalar", str(e))

      try:
         water_temp = ds18b20().getTempC()
         logData("ds18b20_1", "Success", "temperature", "water", "{:+.1f}".format(water_temp), 
                 "celsius", '')
         send_sensor_data_via_mqtt(device_2, mqtt_client, "ds18b20_1", "temperature", "water", 
                                   "{:+.1f}".format(temp), "celsius", date_time)
      except Exception as e:
         logData("ds18b20_1", "Failure", "temperature", "water", '', "celsius", str(e))
      
      time.sleep(5)
