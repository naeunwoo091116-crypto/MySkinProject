/*
 * MySkin LED Mask Controller for Seeed Xiao BLE (nRF52840)
 *
 * This sketch controls RGB LED strips for skin therapy
 * Supports RED (630nm), BLUE (415nm), and GOLD (590nm) modes
 *
 * Hardware Setup:
 * - Seeed Xiao BLE (nRF52840)
 * - RGB LED Strip (WS2812B or similar) on D10 (or any GPIO pin)
 * - Alternative: Separate LED pins for R, G, B
 *
 * BLE Service UUID: 0000ffe0-0000-1000-8000-00805f9b34fb
 * BLE Characteristic UUID: 0000ffe1-0000-1000-8000-00805f9b34fb
 *
 * Commands: "START:MODE:DURATION"
 * Example: "START:RED:20" (Red mode for 20 minutes)
 */

#include <ArduinoBLE.h>

// Pin Definitions (Seeed Xiao BLE Sense Plus - Onboard RGB LED)
// 실제 핀맵: https://wiki.seeedstudio.com/XIAO_BLE/#hardware-overview
#define LED_PIN_R 11   // Red LED (actual pin)
#define LED_PIN_G 12   // Green LED (actual pin)
#define LED_PIN_B 13   // Blue LED (actual pin)
#define STATUS_LED LED_BUILTIN  // 내장 상태 LED

// BLE Service and Characteristic
BLEService ledService("0000FFE0-0000-1000-8000-00805F9B34FB");
BLEStringCharacteristic commandCharacteristic("0000FFE1-0000-1000-8000-00805F9B34FB",
                                               BLEWrite | BLERead | BLENotify, 100);

// LED Mode RGB values (0-255)
struct LEDMode {
  String name;
  int r, g, b;
};

LEDMode modes[3] = {
  {"RED", 255, 0, 0},      // 630nm equivalent (주름, 탄력)
  {"BLUE", 0, 0, 255},     // 415nm equivalent (여드름, 모공)
  {"GOLD", 255, 215, 0}    // 590nm equivalent (미백, 색소침착)
};

// State variables
String currentMode = "OFF";
unsigned long therapyDuration = 0;  // in milliseconds
unsigned long therapyStartTime = 0;
bool therapyActive = false;

// Function prototypes
void setupPins();
void setupBLE();
void processCommand(String cmd, bool isBLE);
void sendResponse(String response, bool isBLE);
void setLEDColor(int r, int g, int b);
void startTherapy(String mode, int durationMin);
void stopTherapy();
void updateTherapy();
void blinkStatusLED();

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 3000); // Wait for Serial (max 3s)

  Serial.println("MySkin LED Mask - Xiao BLE");
  Serial.println("Initializing...");

  setupPins();

  // LED 하드웨어 테스트
  Serial.println("Testing LEDs...");
  Serial.println("Red LED test (2 sec)");
  setLEDColor(255, 0, 0);
  delay(2000);

  Serial.println("Green LED test (2 sec)");
  setLEDColor(0, 255, 0);
  delay(2000);

  Serial.println("Blue LED test (2 sec)");
  setLEDColor(0, 0, 255);
  delay(2000);

  Serial.println("All OFF");
  setLEDColor(0, 0, 0);

  setupBLE();

  Serial.println("Ready!");
  Serial.println("Waiting for BLE connection...");
  Serial.println("Send 'TEST' to run LED test again");
}

void loop() {
  // Check for Serial commands (USB connection)
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    if (command.length() > 0) {
      Serial.print("Serial command received: ");
      Serial.println(command);
      processCommand(command, false);
    }
  }

  // Poll BLE central
  BLEDevice central = BLE.central();

  if (central) {
    Serial.print("Connected to central: ");
    Serial.println(central.address());
    digitalWrite(STATUS_LED, HIGH);

    while (central.connected()) {
      // Check for Serial commands even during BLE connection
      if (Serial.available() > 0) {
        String command = Serial.readStringUntil('\n');
        command.trim();
        if (command.length() > 0) {
          Serial.print("Serial command received: ");
          Serial.println(command);
          processCommand(command, false);
        }
      }

      // Check for incoming BLE command
      if (commandCharacteristic.written()) {
        String command = commandCharacteristic.value();
        Serial.print("Received BLE command: ");
        Serial.println(command);
        processCommand(command, true);
      }

      // Update therapy state
      updateTherapy();

      delay(100);
    }

    // Central disconnected
    Serial.print("Disconnected from central: ");
    Serial.println(central.address());
    digitalWrite(STATUS_LED, LOW);
    stopTherapy();
  } else {
    // No BLE connection - check serial and update therapy
    updateTherapy();
    blinkStatusLED();
    delay(100);
  }
}

void setupPins() {
  pinMode(LED_PIN_R, OUTPUT);
  pinMode(LED_PIN_G, OUTPUT);
  pinMode(LED_PIN_B, OUTPUT);
  pinMode(STATUS_LED, OUTPUT);

  // Turn off all LEDs initially
  setLEDColor(0, 0, 0);
  digitalWrite(STATUS_LED, LOW);
}

void setupBLE() {
  if (!BLE.begin()) {
    Serial.println("Starting BLE failed!");
    while (1) {
      digitalWrite(STATUS_LED, HIGH);
      delay(100);
      digitalWrite(STATUS_LED, LOW);
      delay(100);
    }
  }

  // Set device name
  BLE.setLocalName("MySkin_LED_Mask");
  BLE.setDeviceName("MySkin_LED_Mask");

  // Set advertised service
  BLE.setAdvertisedService(ledService);

  // Add characteristic to service
  ledService.addCharacteristic(commandCharacteristic);

  // Add service
  BLE.addService(ledService);

  // Set initial value
  commandCharacteristic.writeValue("READY");

  // Start advertising
  BLE.advertise();

  Serial.println("BLE LED Service started");
  Serial.println("Device name: MySkin_LED_Mask");
}

// Unified command processing function
void processCommand(String cmd, bool isBLE) {
  cmd.trim();
  cmd.toUpperCase();

  String response = "";

  // Command format: "START:MODE:DURATION"
  if (cmd.startsWith("START:")) {
    int firstColon = cmd.indexOf(':');
    int secondColon = cmd.indexOf(':', firstColon + 1);

    if (secondColon > 0) {
      String mode = cmd.substring(firstColon + 1, secondColon);
      int duration = cmd.substring(secondColon + 1).toInt();

      mode.trim();

      if (duration > 0 && duration <= 60) {  // Max 60 minutes
        startTherapy(mode, duration);
        response = "OK:STARTED:" + mode + ":" + String(duration);
      } else {
        response = "ERROR:INVALID_DURATION";
        Serial.println("Invalid duration (must be 1-60 minutes)");
      }
    } else {
      response = "ERROR:INVALID_FORMAT";
      Serial.println("Invalid command format");
    }
  }
  else if (cmd == "STOP") {
    stopTherapy();
    response = "OK:STOPPED";
  }
  else if (cmd == "STATUS") {
    if (therapyActive) {
      unsigned long elapsed = (millis() - therapyStartTime) / 1000;
      unsigned long remaining = (therapyDuration / 1000) - elapsed;
      response = "ACTIVE:" + currentMode + ":" + String(remaining);
    } else {
      response = "IDLE";
    }
  }
  else if (cmd == "TEST") {
    // LED 하드웨어 테스트
    Serial.println("Running LED test sequence...");
    setLEDColor(255, 0, 0);
    delay(1000);
    setLEDColor(0, 255, 0);
    delay(1000);
    setLEDColor(0, 0, 255);
    delay(1000);
    setLEDColor(255, 215, 0);
    delay(1000);
    setLEDColor(0, 0, 0);
    response = "OK:TEST_COMPLETED";
  }
  else {
    response = "ERROR:UNKNOWN_COMMAND";
    Serial.println("Unknown command: " + cmd);
  }

  // Send response
  sendResponse(response, isBLE);
}

// Send response via BLE or Serial
void sendResponse(String response, bool isBLE) {
  if (isBLE) {
    // Send via BLE
    commandCharacteristic.writeValue(response);
    Serial.println("BLE Response: " + response);
  } else {
    // Send via Serial
    Serial.println(response);
  }
}

void startTherapy(String mode, int durationMin) {
  Serial.print("Starting therapy: ");
  Serial.print(mode);
  Serial.print(" for ");
  Serial.print(durationMin);
  Serial.println(" minutes");

  mode.toUpperCase();
  bool modeFound = false;

  // Find matching mode
  for (int i = 0; i < 3; i++) {
    if (modes[i].name == mode) {
      setLEDColor(modes[i].r, modes[i].g, modes[i].b);
      currentMode = mode;
      therapyDuration = durationMin * 60000UL;  // Convert to milliseconds
      therapyStartTime = millis();
      therapyActive = true;
      modeFound = true;
      break;
    }
  }

  if (!modeFound) {
    Serial.println("Invalid mode: " + mode);
  }
}

void stopTherapy() {
  Serial.println("Stopping therapy");
  therapyActive = false;
  currentMode = "OFF";
  setLEDColor(0, 0, 0);
}

void updateTherapy() {
  if (!therapyActive) return;

  unsigned long elapsed = millis() - therapyStartTime;

  if (elapsed >= therapyDuration) {
    Serial.println("Therapy completed!");

    // Send completion notification via BLE if connected
    BLEDevice central = BLE.central();
    if (central && central.connected()) {
      commandCharacteristic.writeValue("COMPLETED");
    }

    stopTherapy();

    // Blink to indicate completion
    for (int i = 0; i < 3; i++) {
      digitalWrite(STATUS_LED, HIGH);
      delay(200);
      digitalWrite(STATUS_LED, LOW);
      delay(200);
    }
  }
}

void setLEDColor(int r, int g, int b) {
  // Seeed Xiao BLE Sense Plus는 공통 양극(Common Anode) RGB LED
  // PWM 값을 반전해야 함: 0 = 켜짐, 255 = 꺼짐
  analogWrite(LED_PIN_R, 255 - r);
  analogWrite(LED_PIN_G, 255 - g);
  analogWrite(LED_PIN_B, 255 - b);

  Serial.print("LED Color set to R:");
  Serial.print(r);
  Serial.print(" G:");
  Serial.print(g);
  Serial.print(" B:");
  Serial.println(b);
  Serial.print("(Inverted PWM: R:");
  Serial.print(255 - r);
  Serial.print(" G:");
  Serial.print(255 - g);
  Serial.print(" B:");
  Serial.print(255 - b);
  Serial.println(")");
}

void blinkStatusLED() {
  static unsigned long lastBlink = 0;
  static bool ledState = false;

  if (millis() - lastBlink > 1000) {
    ledState = !ledState;
    digitalWrite(STATUS_LED, ledState);
    lastBlink = millis();
  }
}
