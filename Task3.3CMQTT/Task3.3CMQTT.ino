// Submitted by: REUEL MENPARA --> 2510994818
// Task 3.2C - MQTT

#include <WiFiNINA.h>
#include <PubSubClient.h>

const char wifiName[] = "WIFI NAME";
const char wifiPassword[] = "WIFI PASSWORD";

const char mqttServer[] = "broker.emqx.io";
const int mqttPort = 1883;

const char waveTopic[] = "ES/Wave";
const char patTopic[] = "ES/Pat";

const char taskMessage[] =
  "REUEL MENPARA --> Performing task 3.2C";

const int triggerPin = 7;
const int echoPin = 6;

const int bathroomLed = 2;
const int hallwayLed = 3;

//gesture thresholds based on the tested sensor position
const float gestureStartDistance = 40.0;
const float gestureEndDistance = 60.0;
const float patDistance = 10.0;

bool gestureActive = false;
float closestDistance = 200.0;

unsigned long lastGestureTime = 0;

WiFiClient networkClient;
PubSubClient mqttClient(networkClient);

float getDistance()
{
  //send a short ultrasonic pulse from the sensor
  digitalWrite(triggerPin, LOW);
  delayMicroseconds(3);

  digitalWrite(triggerPin, HIGH);
  delayMicroseconds(10);

  digitalWrite(triggerPin, LOW);

  //measure the time taken for the echo to return
  unsigned long echoTime = pulseIn(echoPin, HIGH, 30000);

  if (echoTime == 0)
  {
    return -1;
  }

  //convert echo time into distance in centimetres
  return (echoTime * 0.0343) / 2.0;
}

void controlLights(bool state)
{
  //control both LEDs together
  digitalWrite(bathroomLed, state);
  digitalWrite(hallwayLed, state);
}

void receivedMessage(char* topic, byte* payload, unsigned int length)
{
  Serial.println();
  Serial.print("Message received on: ");
  Serial.println(topic);

  Serial.print("Message: ");

  //display the received MQTT message
  for (unsigned int i = 0; i < length; i++)
  {
    Serial.print((char)payload[i]);
  }

  Serial.println();

  //turn on both lights when a wave message is received
  if (strcmp(topic, waveTopic) == 0)
  {
    Serial.println("WAVE received -> both lights ON");

    controlLights(true);
  }

  //turn off both lights when a pat message is received
  else if (strcmp(topic, patTopic) == 0)
  {
    Serial.println("PAT received -> both lights OFF");

    controlLights(false);
  }
}

void connectToWifi()
{
  Serial.print("Connecting to Wi-Fi");

  //start the Wi-Fi connection
  WiFi.begin(wifiName, wifiPassword);

  //wait until the Arduino connects to Wi-Fi
  while (WiFi.status() != WL_CONNECTED)
  {
    Serial.print(".");
    delay(1000);
  }

  Serial.println();
  Serial.println("Wi-Fi connected!");

  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void connectToMqtt()
{
  //keep trying until the MQTT connection is successful
  while (!mqttClient.connected())
  {
    Serial.println("Connecting to EMQX...");

    //create a unique MQTT client ID
    String clientName = "Nano33IoT-" + String(random(1000, 9999));

    if (mqttClient.connect(clientName.c_str()))
    {
      Serial.println("MQTT connected!");

      //subscribe to both required gesture topics
      mqttClient.subscribe(waveTopic);
      mqttClient.subscribe(patTopic);

      Serial.println("Subscribed to ES/Wave");
      Serial.println("Subscribed to ES/Pat");
    }
    else
    {
      Serial.print("MQTT connection failed. State: ");
      Serial.println(mqttClient.state());

      delay(3000);
    }
  }
}

void detectGesture(float distance)
{
  //start tracking when the hand enters below 40 cm
  if (!gestureActive && distance < gestureStartDistance)
  {
    gestureActive = true;
    closestDistance = distance;

    Serial.println("Gesture started");
  }

  if (gestureActive)
  {
    //store the closest distance reached during the gesture
    if (distance < closestDistance)
    {
      closestDistance = distance;
    }

    //wait until the hand moves away before deciding the gesture
    if (distance > gestureEndDistance)
    {
      if (millis() - lastGestureTime > 1500)
      {
        Serial.print("Closest distance: ");
        Serial.print(closestDistance);
        Serial.println(" cm");

        //a very close movement is treated as a pat
        if (closestDistance <= patDistance)
        {
          Serial.println("PAT detected");

          //publish the pat message to the MQTT broker
          mqttClient.publish(patTopic, taskMessage);
        }

        //a normal hand movement is treated as a wave
        else
        {
          Serial.println("WAVE detected");

          //publish the wave message to the MQTT broker
          mqttClient.publish(waveTopic, taskMessage);
        }

        lastGestureTime = millis();
      }

      //reset gesture tracking for the next movement
      gestureActive = false;
      closestDistance = 200.0;
    }
  }
}

void setup()
{
  Serial.begin(9600);

  //set the ultrasonic sensor pins
  pinMode(triggerPin, OUTPUT);
  pinMode(echoPin, INPUT);

  //set both LED pins as outputs
  pinMode(bathroomLed, OUTPUT);
  pinMode(hallwayLed, OUTPUT);

  //start with both lights turned off
  controlLights(false);

  //set the MQTT broker and message callback
  mqttClient.setServer(mqttServer, mqttPort);
  mqttClient.setCallback(receivedMessage);

  //connect the Arduino to Wi-Fi and MQTT
  connectToWifi();
  connectToMqtt();

  Serial.println();
  Serial.println("Final MQTT gesture system started");
}

void loop()
{
  //reconnect if Wi-Fi connection is lost
  if (WiFi.status() != WL_CONNECTED)
  {
    connectToWifi();
  }

  //reconnect if MQTT connection is lost
  if (!mqttClient.connected())
  {
    connectToMqtt();
  }

  //check for incoming MQTT messages
  mqttClient.loop();

  float distance = getDistance();

  if (distance >= 0)
  {
    Serial.print("Distance: ");
    Serial.print(distance);
    Serial.println(" cm");

    //check the distance for a wave or pat gesture
    detectGesture(distance);
  }

  delay(100);
}
