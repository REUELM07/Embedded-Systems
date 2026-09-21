# Submitted by: REUEL MENPARA --> 2510994818
# SIT210 Task 5.2C - Change the Light Intensity Using GUI

## System Overview
This project demonstrates a simple GUI-based lighting system using a Raspberry Pi and three LEDs.
The GUI allows the user to control the brightness of each light using sliders.
PWM is used to change the intensity of the LEDs according to the selected slider value.

## Hardware Used
The hardware used includes an
- Raspberry Pi 4 Model B
- three LEDs
- three resistors
- breadboard
- jumper wires

The LEDs are connected to PWM-capable GPIO pins of the Raspberry Pi:
- Light 1 - GPIO18
- Light 2 - GPIO12
- Light 3 - GPIO13

Each LED is connected through a resistor to protect the LED from excessive current.
The negative terminals of the LEDs are connected to the Raspberry Pi GND.

## Software Used
- Raspberry Pi OS
- Python
- Tkinter library for creating the GUI
- RPi.GPIO library for controlling the GPIO pins and PWM

## What is PWM and Tkinter?
PWM (Pulse Width Modulation) is a method used to control the average power supplied to an electronic component by switching the signal ON and OFF very quickly.
In this project, PWM is used to control the brightness of the LEDs. A higher duty cycle makes the LED brighter, while a lower duty cycle makes it dimmer.

Tkinter is a Python library used to create graphical user interfaces.
In this project, it is used to create sliders that allow the user to select the required light intensity.

## System Working
The user changes the brightness of a light using its slider in the GUI.
The slider provides a value between 0 and 100, which represents the required brightness level.

The selected value is passed to the `set_brightness()` function.
The function applies the value as the PWM duty cycle for the corresponding LED.

For example, a value of 0 turns the LED OFF, while a value of 100 provides maximum brightness.

The system works as follows:

GUI Slider --> set_brightness() function --> PWM Signal --> Selected LED

## Files Uploaded
1) Main Python code
2) Complete circuit
3) Pi wiring
4) LED wiring
5) -ve rail wiring
