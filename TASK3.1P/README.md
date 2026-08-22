# Submitted by: REUEL MENPARA --> 2510994818
# SIT210 Task 3.1P - Trigger and Notification System


## System Overview
This system uses a BH1750 light sensor connected to an Arduino Nano 33 IoT through I2C communication. The Arduino continuously measures the light level and compares it with a selected threshold of **100 lux**.
When the light level changes from below 100 lux to 100 lux or above, the Arduino detects that sunlight has started and publishes `sunlight_on` through MQTT. When the light level falls below 100 lux, it publishes `sunlight_off`.
The MQTT message is sent through a Mosquitto MQTT broker to Node-RED. Node-RED receives the message through an MQTT input node and passes it to a Function node. The Function node prepares the appropriate email subject and message, which is then sent to the user through Gmail.


## Software and Platforms Used
* Arduino IDE
* BH1750 Library
* WiFiNINA Library
* PubSubClient Library
* Mosquitto MQTT Broker
* Node-RED
* Gmail SMTP

## Trigger Mechanism
The Arduino uses a **100 lux threshold** to determine the sunlight condition. The current light reading is compared with the threshold, and the previous sunlight state is stored to make sure a message is sent only when the condition changes.

The Arduino publishes:
* `sunlight_on` when the light level becomes 100 lux or higher.
* `sunlight_off` when the light level falls below 100 lux.

This prevents repeated messages while the sensor remains in the same light condition.


## Notifications

### Sunlight Detected

**Subject:** Terrarium Sunlight Detected

**Message:** Sunlight has started reaching the terrarium.

### Sunlight Stopped

**Subject:** Terrarium Sunlight Stopped

**Message:** Sunlight is no longer reaching the terrarium.

## Files Uploaded
1) Main code used in ArduinoIDE
2) Sunlight-ON email received
3) Sunlight-OFF email received
4) Sunlight-ON function message
5) Sunlight-OFF function message
6) Function code 
