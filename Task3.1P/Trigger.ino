#include <Wire.h>
#include <BH1750.h>
#include <WiFiNINA.h>
#include <PubSubClient.h>

//wifi details are used to connect the Arduino to the same network as the laptop
const char* WIFI_NAME = "Alfred Nobel";
const char* WIFI_PASSWORD = "CUPunjab";

//this is the laptop address where the MQTT broker is running
const char* MQTT_BROKER = "10.50.10.47";
const int MQTT_PORT = 1883;

//this topic carries the terrarium sunlight status
const char* LIGHT_TOPIC = "terrarium/light";

//this value is used to decide whether enough light is present
const float TERRARIUM_LIGHT_LIMIT = 100.0;

//these objects handle the sensor, wifi and mqtt communication
BH1750 lightSensor;
WiFiClient networkClient;
PubSubClient mqttClient(networkClient);

//this stores the previous sunlight state to avoid repeated messages
bool sunlightWasDetected = false;

//this connects the Arduino to the wifi network
void connectToWiFi()
{
    Serial.print("connecting to Wi-Fi");

    while (WiFi.begin(WIFI_NAME, WIFI_PASSWORD) != WL_CONNECTED)
    {
        Serial.print(".");
        delay(2000);
    }

    Serial.println();
    Serial.println("Wi-Fi connected");

    Serial.print("Arduino IP: ");
    Serial.println(WiFi.localIP());
}

//this connects the Arduino to the MQTT broker
void connectToMQTT()
{
    while (!mqttClient.connected())
    {
        Serial.print("connecting to MQTT broker...");

        if (mqttClient.connect("TerrariumArduino"))
        {
            Serial.println("connected");
        }
        else
        {
            Serial.print("failed, state = ");
            Serial.println(mqttClient.state());
            delay(2000);
        }
    }
}

void setup()
{
    Serial.begin(9600);
    delay(2000);

    //this starts the I2C communication
    Wire.begin();

    //this starts the BH1750 using its detected I2C address
    if (!lightSensor.begin(BH1750::CONTINUOUS_HIGH_RES_MODE, 0x23, &Wire))
    {
        Serial.println("BH1750 sensor not found");

        while (true)
        {
            delay(1000);
        }
    }

    Serial.println("BH1750 sensor started");

    //this connects the Arduino to wifi
    connectToWiFi();

    //this sets the MQTT broker address and port
    mqttClient.setServer(MQTT_BROKER, MQTT_PORT);

    //this connects the Arduino to MQTT
    connectToMQTT();
}

void loop()
{
    //this reconnects to MQTT if the connection is lost
    if (!mqttClient.connected())
    {
        connectToMQTT();
    }

    mqttClient.loop();

    //this reads the current light level in lux
    float lightLevel = lightSensor.readLightLevel();

    //this checks whether the light level has reached the selected limit
    bool sunlightDetected = lightLevel >= TERRARIUM_LIGHT_LIMIT;

    Serial.print("Current light level: ");
    Serial.print(lightLevel);
    Serial.println(" lux");

    //this sends a message only when the sunlight condition changes
    if (sunlightDetected != sunlightWasDetected)
    {
        if (sunlightDetected)
        {
            mqttClient.publish(LIGHT_TOPIC, "sunlight_on");
            Serial.println("Sunlight detected");
        }
        else
        {
            mqttClient.publish(LIGHT_TOPIC, "sunlight_off");
            Serial.println("Sunlight stopped");
        }

        //this remembers the current condition for the next reading
        sunlightWasDetected = sunlightDetected;
    }

    delay(2000);
}