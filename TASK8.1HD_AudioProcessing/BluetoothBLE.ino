#include <ArduinoBLE.h>
#include <Wire.h>
#include <BH1750.h>
#include <Servo.h>

//PIN SETTINGS 
const int hallwayLedPin = 2;
const int bathroomLedPin = 3;
const int servoPin = 9;

//LIGHT SETTINGS
const float LIGHT_THRESHOLD = 40.0;

//SERVO SETTINGS
const int VENT_OPEN_ANGLE = 90;
const int VENT_CLOSED_ANGLE = 20;

//BLE SETTINGS
BLEService lightService(
  "19B10000-E8F2-537E-4F6C-D104768A1214"
);

BLEStringCharacteristic lightCharacteristic(
  "19B10001-E8F2-537E-4F6C-D104768A1214",
  BLERead | BLEWrite,
  100
);

//DEVICES 
BH1750 lightSensor;
Servo ventServo;

//DEVICE STATES
bool hallwayOn = false;
bool bathroomOn = false;
bool fanOn = false;

bool sensorReady = false;
float lux = -1.0;

unsigned long lastSensorRead = 0;

const unsigned long SENSOR_INTERVAL = 500;


//UPDATE LIGHTS

void updateLights() {
  //Never permit lights to remain on when the
  //sensor reading is invalid or too bright.

  if (!sensorReady || lux < 0 || lux >= LIGHT_THRESHOLD) {
    hallwayOn = false;
    bathroomOn = false;
  }

  digitalWrite(
    hallwayLedPin,
    hallwayOn ? HIGH : LOW
  );

  digitalWrite(
    bathroomLedPin,
    bathroomOn ? HIGH : LOW
  );
}


//READ LIGHT SENSOR

void readLightSensor() {
  unsigned long currentTime = millis();

  if (currentTime - lastSensorRead < SENSOR_INTERVAL) {
    return;
  }

  lastSensorRead = currentTime;

  // BH1750 read errors can produce invalid values.
  float newLux = lightSensor.readLightLevel();

  if (newLux < 0 || newLux > 100000) {
    sensorReady = false;
    lux = -1.0;

    Serial.println("ERROR: BH1750 reading invalid.");

    updateLights();
    return;
  }

  lux = newLux;
  sensorReady = true;

  Serial.print("Ambient light: ");
  Serial.print(lux);
  Serial.println(" lux");

  //If the room becomes bright enough, turn off any lights that are currently on.
  updateLights();
}


//RETURN DEVICE STATUS
String getStatus() {
  String status = "";

  status += "LUX=";

  if (sensorReady) {
    status += String(lux, 2);
  } else {
    status += "INVALID";
  }

  status += ";HALLWAY=";
  status += hallwayOn ? "ON" : "OFF";

  status += ";BATHROOM=";
  status += bathroomOn ? "ON" : "OFF";

  status += ";FAN=";
  status += fanOn ? "ON" : "OFF";

  return status;
}


//PROCESS BLE COMMAND
void processCommand(String command) {
  command.trim();
  command.toUpperCase();

  Serial.print("Received command: ");
  Serial.println(command);

  if (command == "HALLWAY_ON") {
    if (!sensorReady || lux < 0) {
      hallwayOn = false;
      Serial.println("Hallway light denied: sensor unavailable.");
    }
    else if (lux >= LIGHT_THRESHOLD) {
      hallwayOn = false;
      Serial.println("Hallway light denied: room is bright.");
    }
    else {
      hallwayOn = true;
      Serial.println("Hallway light ON.");
    }
  }

  else if (command == "HALLWAY_OFF") {
    hallwayOn = false;
    Serial.println("Hallway light OFF.");
  }

  else if (command == "BATHROOM_ON") {
    if (!sensorReady || lux < 0) {
      bathroomOn = false;
      Serial.println("Bathroom light denied: sensor unavailable.");
    }
    else if (lux >= LIGHT_THRESHOLD) {
      bathroomOn = false;
      Serial.println("Bathroom light denied: room is bright.");
    }
    else {
      bathroomOn = true;
      Serial.println("Bathroom light ON.");
    }
  }

  else if (command == "BATHROOM_OFF") {
    bathroomOn = false;
    Serial.println("Bathroom light OFF.");
  }

  else if (command == "FAN_ON") {
    fanOn = true;
    ventServo.write(VENT_OPEN_ANGLE);
    Serial.println("Vent opened.");
  }

  else if (command == "FAN_OFF") {
    fanOn = false;
    ventServo.write(VENT_CLOSED_ANGLE);
    Serial.println("Vent closed.");
  }

  else if (command == "GET_STATUS") {
    Serial.println(getStatus());
  }

  else {
    Serial.println("Unknown command.");
  }

  updateLights();

  //Update the characteristic so the connected central can read the current status later.
  lightCharacteristic.writeValue(getStatus());
}


//SETUP

void setup() {
  Serial.begin(9600);

  pinMode(hallwayLedPin, OUTPUT);
  pinMode(bathroomLedPin, OUTPUT);

  digitalWrite(hallwayLedPin, LOW);
  digitalWrite(bathroomLedPin, LOW);

  //Attach the servo and close the vent.
  ventServo.attach(servoPin);
  ventServo.write(VENT_CLOSED_ANGLE);

  //Initialise I2C and BH1750.
  Wire.begin();

  if (lightSensor.begin(BH1750::CONTINUOUS_HIGH_RES_MODE)) {
    sensorReady = true;
    Serial.println("BH1750 initialised.");
  }
  else {
    sensorReady = false;
    Serial.println("ERROR: BH1750 initialisation failed.");
  }

  //Initialise Bluetooth.
  if (!BLE.begin()) {
    Serial.println("ERROR: BLE initialisation failed.");

    while (true) {
      digitalWrite(hallwayLedPin, LOW);
      digitalWrite(bathroomLedPin, LOW);
    }
  }

  BLE.setLocalName("AudioLight");
  BLE.setAdvertisedService(lightService);

  lightService.addCharacteristic(lightCharacteristic);
  BLE.addService(lightService);

  lightCharacteristic.writeValue(getStatus());

  BLE.advertise();

  Serial.println("AudioLight system ready.");
  Serial.println("Waiting for Raspberry Pi...");
}


//MAIN LOOP
void loop() {
  BLE.poll();

  //Read sensor regularly, whether or not BLE is connected.
  readLightSensor();

  //Process incoming BLE commands.
  if (lightCharacteristic.written()) {
    String command = lightCharacteristic.value();
    processCommand(command);
  }

  //Keep the LEDs safe if the sensor fails.
  if (!sensorReady || lux < 0 || lux >= LIGHT_THRESHOLD) {
    updateLights();
  }
}

