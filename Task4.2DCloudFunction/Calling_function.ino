#include <WiFiNINA.h>


//Wi-Fi details to be connected
char ssid[] = "REUEL's Galaxy S24";
char password[] = "1234567890";


//Firebase server details that actually makes connection using URL
const char firebaseServer[] =
  "linda-controlling-light-default-rtdb.firebaseio.com";

WiFiSSLClient client;


//LED pins connected with arduino nano 33 IoT
const int livingRoomLED = 2;
const int bathroomLED = 3;
const int closetLED = 5;

String lastRoom = "";


//It will control the LED based on name of area of a house
void controlRoom(String room)
{
  //turn all LEDs off before selecting one
  digitalWrite(livingRoomLED, LOW);
  digitalWrite(bathroomLED, LOW);
  digitalWrite(closetLED, LOW);

  //It will print details according to the light on and off in the terminal
  if (room == "living room")
  {
    digitalWrite(livingRoomLED, HIGH);
    Serial.println("Living Room LED ON");
  }
  else if (room == "bathroom")
  {
    digitalWrite(bathroomLED, HIGH);
    Serial.println("Bathroom LED ON");
  }
  else if (room == "closet")
  {
    digitalWrite(closetLED, HIGH);
    Serial.println("Closet LED ON");
  }
  else if (room == "off")
  {
    Serial.println("All LEDs OFF");
  }
}


//Read room value from Firebase
void readRoom()
{
  Serial.println("Reading Firebase...");

  if (!client.connectSSL(firebaseServer, 443))
  {
    Serial.println("Firebase connection failed!");
    return;
  }

  //request the room value using host URL
  client.println("GET /room.json HTTP/1.1");
  client.println("Host: linda-controlling-light-default-rtdb.firebaseio.com");
  client.println("Connection: close");
  client.println();

  //wait for Firebase response
  unsigned long startTime = millis();

  while (!client.available())
  {
    if (millis() - startTime > 5000)
    {
      Serial.println("Firebase response timeout!");
      client.stop();
      return;
    }
  }

  //It will read the complete response recieved
  String response = "";

  while (client.connected() || client.available())
  {
    if (client.available())
    {
      response += client.readString();
    }
  }

  client.stop();

  //Now, i will check which room was received as input by user
  String room = "";

  if (response.indexOf("\"living room\"") >= 0)
  {
    room = "living room";
  }
  else if (response.indexOf("\"bathroom\"") >= 0)
  {
    room = "bathroom";
  }
  else if (response.indexOf("\"closet\"") >= 0)
  {
    room = "closet";
  }
  else if (response.indexOf("\"off\"") >= 0)
  {
    room = "off";
  }

  if (room != "")
  {
    Serial.print("Room received: ");
    Serial.println(room);

    //only change the LED when the command changes
    if (room != lastRoom)
    {
      lastRoom = room;
      controlRoom(room);
    }
  }
  else
  {
    Serial.println("No valid room command received.");
  }
}


//Main Setup loop
void setup()
{
  Serial.begin(115200);
  delay(2000);

  pinMode(livingRoomLED, OUTPUT);
  pinMode(bathroomLED, OUTPUT);
  pinMode(closetLED, OUTPUT);

  digitalWrite(livingRoomLED, LOW);
  digitalWrite(bathroomLED, LOW);
  digitalWrite(closetLED, LOW);

  //connect to Wi-Fi
  Serial.print("Connecting to Wi-Fi");

  while (WiFi.begin(ssid, password) != WL_CONNECTED)
  {
    Serial.print(".");
    delay(1000);
  }

  Serial.println();
  Serial.println("Wi-Fi connected!");

  Serial.print("Arduino IP: ");
  Serial.println(WiFi.localIP());
}


//Main loop
void loop()
{
  readRoom();

  delay(2000);
}