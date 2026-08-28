# Submitted by: REUEL MENPARA --> 2510994818
# SIT210 Task 3.1P - Trigger and Notification System

## System Overview
This project uses an Arduino Nano 33 IoT, HC-SR04 ultrasonic sensor, two LEDs, Wi-Fi, and MQTT to control the bathroom and hallway lights using hand gestures.

MQTT (Message Queuing Telemetry Transport) is a lightweight communication protocol used for sending messages between devices. In this system, the Arduino acts as both an MQTT client and communicates with the EMQX broker.

- **Client:** The Arduino Nano 33 IoT that sends and receives MQTT messages.
- **Broker:** EMQX (`broker.emqx.io`) that receives messages from the Arduino and forwards them to subscribed clients.
- **Publisher:** The Arduino publishes the detected gesture to `ES/Wave` or `ES/Pat`.
- **Subscriber:** The Arduino subscribes to both topics and responds to received messages.

The system detects a WAVE or PAT using the HC-SR04 sensor. A WAVE publishes a message to `ES/Wave` and turns both LEDs ON. A PAT publishes a message to `ES/Pat` and turns both LEDs OFF.

## Hardware Used
- Arduino Nano 33 IoT
- HC-SR04 Ultrasonic Sensor
- 2 × LEDs
- Resistors
- Breadboard
- Jumper wires
- USB cable

## Software Used
- Arduino IDE
- WiFiNINA Library
- PubSubClient MQTT Library
- EMQX Public MQTT Broker
- MQTTX Desktop

## Observation
A separate tester code was first used to observe the HC-SR04 readings for different hand movements. Multiple WAVE and PAT tests were performed to determine suitable detection thresholds for the new sensor position.

The final thresholds were selected based on the observed readings:

Gesture start:     < 40 cm
Gesture end:       > 60 cm
PAT:               <= 10 cm
WAVE:              > 10 cm

During testing, the sensor showed approximately 194 cm with no hand and around 67-69 cm when the hand was far away. The WAVE reached a minimum of approximately 31.35 cm, while the PAT reached approximately 1.84 cm.

## System working
The final system successfully detects the defined WAVE and PAT gestures using the HC-SR04 ultrasonic sensor.

- **WAVE:**
Hand WAVE --> WAVE detected --> Publish to ES/Wave --> EMQX Broker --> ES/Wave received --> Both LEDs ON

- **PAT:**
Hand PAT --> PAT detected Publish to ES/Pat --> EMQX Broker --> ES/Pat received --> Both LEDs OFF

## Files Uploaded
1) Task3.3CMQTT main code
2) Circuit image
3) HC-SR04 wiring image
4) Breadboard wiring image
5) +ve and -ve rail wiring image
6) Arduino nano 33 IoT wiring image
