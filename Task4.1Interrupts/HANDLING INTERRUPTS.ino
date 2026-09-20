// Submitted by: REUEL MENPARA --> 2510994818
// Task 4.2D - Calling functions from the web

#include <Wire.h>
#include <BH1750.h>

BH1750 lightSensor;

//pin connections
const int pirPin = 2;
const int buttonPin = 3;

const int firstLight = 6;
const int secondLight = 7;

//light level below this value is treated as dark
const float darkThreshold = 100.0;

//interrupt event flags
volatile bool motionDetected = false;
volatile bool buttonPressed = false;

bool lightsOn = false;
bool pirLocked = false;

unsigned long lastButtonPress = 0;
const unsigned long buttonDebounce = 250;

//pir interrupt handler
void pirInterrupt()
{
    if (!pirLocked)
    {
        motionDetected = true;
    }
}

//button interrupt handler
void buttonInterrupt()
{
    buttonPressed = true;
}

//control both leds
void controlLights(bool state)
{
    lightsOn = state;

    digitalWrite(firstLight, state);
    digitalWrite(secondLight, state);
}

void setup()
{
    Serial.begin(9600);
    Wire.begin();

    pinMode(pirPin, INPUT);
    pinMode(buttonPin, INPUT_PULLUP);

    pinMode(firstLight, OUTPUT);
    pinMode(secondLight, OUTPUT);

    controlLights(false);

    //start the bh1750 light sensor
    if (lightSensor.begin())
    {
        Serial.println("BH1750 connected successfully.");
    }
    else
    {
        Serial.println("BH1750 connection failed.");
    }

    //setup hardware interrupts
    attachInterrupt(
        digitalPinToInterrupt(pirPin),
        pirInterrupt,
        RISING
    );

    attachInterrupt(
        digitalPinToInterrupt(buttonPin),
        buttonInterrupt,
        FALLING
    );

    Serial.println("SMART LIGHTING SYSTEM READY");
    Serial.println("PIR: D2");
    Serial.println("BUTTON: D3");
    Serial.println("LED 1: D6");
    Serial.println("LED 2: D7");
    Serial.println("LIGHT THRESHOLD: 100 lux");

    delay(2000);
}

void loop()
{
    float luxValue = lightSensor.readLightLevel();

    //turn lights off when the environment becomes bright
    if (luxValue >= darkThreshold && lightsOn)
    {
        controlLights(false);

        Serial.print("Bright environment: ");
        Serial.print(luxValue);
        Serial.println(" lux -> Lights OFF.");
    }

    //handle motion interrupt
    if (motionDetected)
    {
        motionDetected = false;
        pirLocked = true;

        Serial.print("PIR motion event. Light level: ");
        Serial.print(luxValue);
        Serial.println(" lux.");

        if (luxValue < darkThreshold)
        {
            controlLights(true);

            Serial.println("Dark environment -> Lights ON automatically.");
        }
        else
        {
            controlLights(false);

            Serial.println("Bright environment -> Lights remain OFF.");
        }
    }

    //allow the next pir event after the sensor returns low
    if (pirLocked && digitalRead(pirPin) == LOW)
    {
        pirLocked = false;
    }

    //handle button interrupt
    if (buttonPressed)
    {
        buttonPressed = false;

        unsigned long currentTime = millis();

        //ignore very quick repeated button presses
        if (currentTime - lastButtonPress >= buttonDebounce)
        {
            lastButtonPress = currentTime;

            if (luxValue < darkThreshold)
            {
                controlLights(!lightsOn);

                if (lightsOn)
                {
                    Serial.println("Button pressed -> Lights ON manually.");
                }
                else
                {
                    Serial.println("Button pressed -> Lights OFF manually.");
                }
            }
            else
            {
                controlLights(false);

                Serial.println(
                    "Button pressed -> Environment is bright, lights OFF."
                );
            }
        }
    }

    delay(100);
}
