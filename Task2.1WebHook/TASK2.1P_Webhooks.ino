// Submitted by: REUEL MENPARA --> 2510994818
// Task 2.1P - Sending Temperature and Light Data to the Web

#include <WiFiNINA.h>
#include <ThingSpeak.h>
#include <DHT.h>
#include <BH1750.h>
#include <Wire.h>

#include "secrets.h"

//dHT22 connection
#define DHT_DATA_PIN 2
#define DHT_SENSOR_TYPE DHT22

DHT roomSensor(DHT_DATA_PIN, DHT_SENSOR_TYPE);
BH1750 lightSensor;

WiFiClient webClient;

//thingSpeak channel details
unsigned long myChannelNumber = SECRET_CH_ID;
const char* myWriteAPIKey = SECRET_WRITE_APIKEY;

// Sensor readings
float roomTemperature = 0;
float roomHumidity = 0;
float lightIntensity = 0;


//connect Arduino to Wi-Fi
void connectWiFi()
{
    if (WiFi.status() == WL_CONNECTED)
    {
        return;
    }

    Serial.print("Connecting to Wi-Fi: ");
    Serial.println(SECRET_SSID);

    while (WiFi.status() != WL_CONNECTED)
    {
        WiFi.begin(SECRET_SSID, SECRET_PASS);
        Serial.print(".");
        delay(3000);
    }

    Serial.println();
    Serial.println("Wi-Fi connected.");
}


//read values from both sensors
void readRoomSensors()
{
    roomTemperature = roomSensor.readTemperature();
    roomHumidity = roomSensor.readHumidity();
    lightIntensity = lightSensor.readLightLevel();

    Serial.println();
    Serial.println("Current room conditions:");

    Serial.print("Temperature: ");
    Serial.print(roomTemperature);
    Serial.println(" °C");

    Serial.print("Humidity: ");
    Serial.print(roomHumidity);
    Serial.println(" %");

    Serial.print("Light Intensity: ");
    Serial.print(lightIntensity);
    Serial.println(" lux");
}


//send the three readings to ThingSpeak
void uploadRoomData()
{
    ThingSpeak.setField(1, roomTemperature);
    ThingSpeak.setField(2, roomHumidity);
    ThingSpeak.setField(3, lightIntensity);

    int uploadResult = ThingSpeak.writeFields(myChannelNumber, myWriteAPIKey);

    if (uploadResult == 200)
    {
        Serial.println("ThingSpeak update successful.");
    }
    else
    {
        Serial.print("ThingSpeak update failed. HTTP error code: ");
        Serial.println(uploadResult);
    }
}


void setup()
{
    Serial.begin(115200);

    while (!Serial)
    {
        ;
    }

    //start the sensors
    roomSensor.begin();
    Wire.begin();

    if (lightSensor.begin())
    {
        Serial.println("BH1750 light sensor ready.");
    }
    else
    {
        Serial.println("BH1750 light sensor not detected.");
    }

    //check Wi-Fi hardware
    if (WiFi.status() == WL_NO_MODULE)
    {
        Serial.println("Wi-Fi module not detected.");
        while (true)
        {
            ;
        }
    }

    ThingSpeak.begin(webClient);

    Serial.println("Smart room monitoring system started.");
}


void loop()
{
    connectWiFi();

    readRoomSensors();

    //sensor reading check
    if (isnan(roomTemperature) ||
        isnan(roomHumidity) ||
        isnan(lightIntensity))
    {
        Serial.println("Error: Unable to read sensor data.");
    }
    else
    {
        uploadRoomData();
    }

    //thingSpeak update required every 30 seconds
    Serial.println("Waiting 30 seconds for the next update...");
    delay(30000);
}