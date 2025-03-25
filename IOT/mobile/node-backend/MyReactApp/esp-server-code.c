#include <WiFi.h>
#include <Firebase_ESP_Client.h>
#include <vector>

// Wi-Fi credentials
#define WIFI_SSID "Abhishek iPhone"
#define WIFI_PASSWORD "hacker55"

// Firebase project credentials
#define API_KEY "AIzaSyB6W1DJLDT1mJ3X_DDR3AmKAPwyU27J2Ao"
#define DATABASE_URL "https://iot-sever-c8192-default-rtdb.europe-west1.firebasedatabase.app/"

// Define flex sensor pins (adjust as needed)
const int numFlexSensors = 1;
const int flexPins[numFlexSensors] = {4};  // Example pins for sensors 1-5
const int ledPin = 13;   // External LED connected to pin 13 (controlled by sensor 1)

// Firebase objects
FirebaseData fbdo;
FirebaseConfig config;
FirebaseAuth auth;
bool signupOK = false;

// For controlling Firebase update frequency
unsigned long sendDataPrevMillis = 0;

// Global array to store the last known state of each flex sensor
std::vector<bool> lastFlexStates(numFlexSensors, false);

void tokenStatusCallback(TokenInfo info) {
  if (info.status == token_status_ready) {
    Serial.println("Token Ready");
  } else {
    Serial.print("Token Status: ");
    Serial.println(info.status);
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(ledPin, OUTPUT);        // Set external LED pin as output

  // Initialize Wi-Fi connection
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(300);
  }
  Serial.println("\nWiFi connected.");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  // Configure Firebase
  config.api_key = API_KEY;
  config.database_url = DATABASE_URL;
  config.token_status_callback = tokenStatusCallback;

  if (Firebase.signUp(&config, &auth, "", "")) {
    Serial.println("Anonymous Sign-Up Successful");
    signupOK = true;
  } else {
    Serial.printf("Sign-Up Failed: %s\n", config.signer.signupError.message.c_str());
  }
  
  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);
  Serial.println("Firebase Initialized");
}

void loop() {
  // Update every 100 ms
  if (Firebase.ready() && (millis() - sendDataPrevMillis > 100 || sendDataPrevMillis == 0)) {
    sendDataPrevMillis = millis();

    // Loop through each flex sensor
    for (int i = 0; i < numFlexSensors; i++) {
      int flexValue = analogRead(flexPins[i]); // Read sensor value
      Serial.print("Flex Sensor ");
      Serial.print(i + 1);
      Serial.print(" Value: ");
      Serial.println(flexValue);

      // Determine the sensor state based on a threshold (adjust as needed)
      bool flexState = (flexValue < 2770);

      // For sensor 1, update the external LED accordingly (assuming LOW turns LED on)
      if (i == 0) {
        digitalWrite(ledPin, flexState ? LOW : HIGH);
      }
      
      // Update Firebase only if the state has changed
      if (flexState != lastFlexStates[i]) {
        String path = "/frets/" + String(i);
        if (Firebase.RTDB.setBool(&fbdo, path.c_str(), flexState)) {
          Serial.print("Updated ");
          Serial.print(path);
          Serial.print(" to ");
          Serial.println(flexState ? "ON" : "OFF");
        } else {
          Serial.print("Failed to update ");
          Serial.print(path);
          Serial.print(": ");
          Serial.println(fbdo.errorReason());
        }
        // Save the current state
        lastFlexStates[i] = flexState;
      } else {
        Serial.print("No change for sensor ");
        Serial.println(i + 1);
      }
    }
  }
}