# Submitted by: REUEL MENPARA --> 2510994818
# SIT210 Task 4.2D - Calling a Function from the Web

## System Overview
This project demonstrates a simple web-based smart lighting system using an Arduino Nano 33 IoT and Firebase Realtime Database.
The web interface allows the user to control three LEDs representing different areas of a house: Living Room, Bathroom, and Closet.
When a room is selected, the corresponding LED is turned ON while the other LEDs remain OFF.

## Hardware Used
The hardware used includes an
- Arduino Nano 33 IoT
- three LEDs
- three resistors
- breadboard
- jumper wires

The LEDs are connected to different digital pins of the Arduino:
- Living Room LED - D2
- Bathroom LED - D3
- Closet LED - D5

## Software Used
- The project was developed using Arduino IDE
- HTML and JavaScript were used to create the web interface
- Firebase Realtime Database was used to store the selected room
- WiFiNINA library was used for Wi-Fi communication
- HTTPS requests were used to communicate between the Arduino and Firebase

## What is Firebase Realtime Database and WiFiNINA?
Firebase Realtime Database is a cloud database that allows data to be stored and accessed through the internet.
In this project, it is used to store the selected room command such as "living room", "bathroom", "closet", or "off".

WiFiNINA is a library used to connect the Arduino Nano 33 IoT to a Wi-Fi network.
In this project, it is used to connect the Arduino to the internet so that it can read the room command from Firebase.


## System Working
The user selects a room from the web interface.
The selected room is sent to the Firebase Realtime Database and stored under the `room` value.
The Arduino Nano 33 IoT reads this value from Firebase using an HTTPS request.

The Arduino then calls the `controlRoom()` function.
The function first turns OFF all three LEDs and then checks the selected room using simple `if` and `else if` conditions.
The LED connected to the selected room is then turned ON.

The system works as follows:

Web Page --> Firebase Realtime Database --> Arduino Nano 33 IoT --> controlRoom() function --> Selected LED

## Files Uploaded
1) Main Arduino code
2) HTML web page code
3) Complete circuit
4) Arduino Nano 33 IoT wiring
5) LED wiring
6) Rail wiring
