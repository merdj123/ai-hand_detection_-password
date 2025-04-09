// Define LED pins and buzzer pin
const int ledPins[] = {2, 3, 4, 5, 6};
const int numLeds = 5;
const int buzzerPin = 7;  // Connect your passive buzzer here

void setup() {
  // Initialize LED pins as outputs
  for (int i = 0; i < numLeds; i++) {
    pinMode(ledPins[i], OUTPUT);
    digitalWrite(ledPins[i], LOW);
  }
  // Set buzzer pin as output
  pinMode(buzzerPin, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    char incoming = Serial.read();
    
    // If incoming is a digit from '1' to '5', light up that many LEDs
    if (incoming >= '1' && incoming <= '5') {
      int count = incoming - '0';
      for (int i = 0; i < numLeds; i++) {
        digitalWrite(ledPins[i], (i < count) ? HIGH : LOW);
      }
    }
    // If incoming is 'S', indicate success by blinking LEDs and playing a tone
    else if (incoming == 'S') {
      blinkLeds(3);
      // Play a success tone (e.g., 1000 Hz for 500ms)
      tone(buzzerPin, 1000, 500);
    }
    // If incoming is 'F', indicate failure by blinking LEDs and playing a different tone
    else if (incoming == 'F') {
      blinkLeds(1);
      // Play an error tone (e.g., 400 Hz for 500ms)
      tone(buzzerPin, 400, 500);
    }
  }
}

void blinkLeds(int times) {
  for (int t = 0; t < times; t++) {
    for (int i = 0; i < numLeds; i++) {
      digitalWrite(ledPins[i], HIGH);
    }
    delay(300);
    for (int i = 0; i < numLeds; i++) {
      digitalWrite(ledPins[i], LOW);
    }
    delay(300);
  }
}
