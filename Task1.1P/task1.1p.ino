// Submitted by: REUEL MENPARA --> 2510994818
// Task 1.1P - Switching ON Lights

int porch = 5;
int hallway = 6;
int switchPin = 2;

// This function sets up the pins
void setupLights()
{
  pinMode(porch, OUTPUT);
  pinMode(hallway, OUTPUT);
  pinMode(switchPin, INPUT_PULLUP);

  // At the start both lights should be OFF
  digitalWrite(porch, LOW);
  digitalWrite(hallway, LOW);
}

// This function turns both lights ON
void lightsOn()
{
  digitalWrite(porch, HIGH);
  digitalWrite(hallway, HIGH);
}

// This function controls how long each light stays ON
void lightsTimer()
{
  // Porch light stays ON for 30 seconds
  delay(30000);
  digitalWrite(porch, LOW);

  // Hallway light stays ON for another 30 seconds
  delay(30000);
  digitalWrite(hallway, LOW);
}

void setup()
{
  setupLights();
}

void loop()
{
  // Button gives LOW when it is pressed
  if (digitalRead(switchPin) == LOW)
  {
    lightsOn();
    lightsTimer();

    // Small delay before checking the button again
    delay(300);
  }
}