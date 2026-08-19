# SIT210 Task 2.1P - Sending Temperature and Light Data to the Web

## Overview
This task implements a simple embedded monitoring system using an **Arduino Nano 33 IoT**, **DHT22 temperature and humidity sensor**, and **BH1750 light sensor**. The Arduino collects temperature, humidity, and light intensity data and sends the readings to **ThingSpeak** through Wi-Fi.


## Modular Programming
The program was developed by modifying the ThingSpeak **WriteMultipleFields** example. Modular functions were added to make the program easier to understand and maintain.

Main functions used:

* `connectWiFi()` - connects the Arduino to the Wi-Fi network.
* `readRoomSensors()` - collects temperature, humidity, and light intensity readings.
* `uploadRoomData()` - sends the three sensor readings to ThingSpeak.

## Observations
The temperature remained relatively stable during testing, while the light intensity changed noticeably when the lighting conditions were changed. The humidity remained above 90% because the actual room environment had high humidity, so only small fluctuations were observed in the humidity graph.
During testing, a loose sensor connection caused some readings to be recorded incorrectly. After checking and fixing the connection, the system was restarted and the data collection was continued successfully.

## Files uploaded
1) The main code file with secrets.h template
2) The circuit that i have made to fetch the data with ThingSpeak
3) The circuit i designed on Wokwi software to showcase the wiring
4) The graphs data fetched using ThingSpeak
   
**Note:** The actual `secrets.h` file is not included in this repository because it contains private Wi-Fi and ThingSpeak credentials, I have removed the personal details and have added the template to showcase the code. 
