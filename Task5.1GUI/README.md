# Submitted by: REUEL MENPARA --> 2510994818
# SIT210 Task 5.1P - Making a Graphical User Interface

## System Overview
This project demonstrates a simple graphical user interface (GUI) based smart lighting system using a Raspberry Pi 4 Model B.
The GUI allows the user to control three LEDs representing different areas of a house: Living Room, Bathroom, and Closet.
Each room can be selected using a radio button, and only the selected room's LED is turned ON.

## Hardware Used
The hardware used includes an
- Raspberry Pi 4 Model B
- three LEDs
- three resistors
- breadboard
- jumper wires

The LEDs are connected to different GPIO pins of the Raspberry Pi:
- Living Room LED - GPIO 17
- Bathroom LED - GPIO 27
- Closet LED - GPIO 22

## Software Used
- The project was developed using Python
- Tkinter was used to create the graphical user interface
- GPIO Zero was used to control the LEDs through the Raspberry Pi GPIO pins
- The Python program was developed and executed on the Raspberry Pi

## What is Tkinter and GPIO Zero?
Tkinter is a Python library used to create graphical user interfaces. 
In this project, it is used to create the main window, radio buttons for room selection, and the Exit button.

GPIO Zero is a Python library that provides a simple way to control Raspberry Pi GPIO devices.
In this project, it is used to turn the three LEDs ON and OFF using the `on()` and `off()` functions.

## Observation
The GUI successfully controls all three LEDs connected to the Raspberry Pi.
When the user selects the Living Room, the Living Room LED turns ON while the other LEDs remain OFF.
Similarly, selecting the Bathroom or Closet turns ON only the corresponding LED.
The Exit button also turns OFF all LEDs before closing the GUI.

## System Working
The user selects a room using one of the radio buttons in the GUI.
The program first turns OFF all three LEDs and then checks the selected room.
Using simple `if` and `elif` conditions, the LED connected to the selected room is turned ON.
This allows only one room light to remain ON at a time.
When the Exit button is pressed, all LEDs are turned OFF and the GUI is safely closed.

## Files Uploaded
1) Task5.1P GUI Python code
2) Complete circuit wiring image
3) Raspberry Pi wiring image
4) LED and negative rail wiring image
