# Submitted by: REUEL MENPARA --> 2510994818
# SIT210 Task 4.1P - Handling Interrupts

## System Overview
This project demonstrates an interrupt-based smart lighting system using an Arduino Nano 33 IoT. 
The PIR sensor is the main input for detecting motion, while the BH1750 measures the surrounding light level. 
Two LEDs are used as the output, and a push button provides manual backup control.

## Hardware Used
The hardware used includes an 
- Arduino Nano 33 IoT
- HC-SR501 PIR motion sensor
- BH1750 light sensor
- push button
- two LEDs
- resistors
- breadboard
- jumper wires

## Software Used
- The project was developed using Arduino IDE
- The Wire and BH1750 libraries were used for communication with the light sensor and the Serial Monitor was used to observe system outputs.

## What is Interrupts?
An interrupt allows the Arduino to respond to an external event without continuously checking the input. 
In this project, the PIR uses a rising-edge interrupt to detect motion, while the push button uses a falling-edge interrupt for manual control.

## Observation
The system successfully detects motion using the PIR and checks the light level using the BH1750. 
When motion is detected in a dark environment below 100 lux, both LEDs turn ON. 
When the environment becomes bright, the LEDs turn OFF. The push button also successfully provides manual control.

## System Working
The PIR acts as the main trigger for the automatic lighting system. When motion is detected, the Arduino checks the BH1750 light level. If the environment is dark, both LEDs turn ON. If there is enough light, the LEDs remain OFF. The push button provides additional manual control using a hardware interrupt.

## Files Uploaded
1) Task4.1P Handling Interrupts main code
2) Circuit wiring image
3) PIR SENSOR wiring image
4) BreadboarBH1750 wiring image
5) +ve and -ve rail wiring image
6) Arduino nano 33 IoT wiring image
