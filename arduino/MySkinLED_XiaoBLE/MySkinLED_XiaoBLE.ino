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

// Pin Definitions (adjust based on your hardware)
#define LED_PIN_R 2    // Red LED pin (D2)
#define LED_PIN_G 3    // Green LED pin (D3)
#define LED_PIN_B 4    // Blue LED pin (D4)
#define STATUS_LED LED_BUILTIN

// BLE Service and Characteristic
BLEService ledService("0000FFE0-0000-1000-8000-00805F9B34FB");
BLEStringCharacteristic commandCharacteristic("0000FFE1-0000-1000-8000-00805F9B34FB",
                                               BLEWrite | BLERead, 50);

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
void handleCommand(String cmd);
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
  setupBLE();

  Serial.println("Ready!");
  Serial.println("Waiting for BLE connection...");
}

void loop() {
  // Check for Serial commands (USB connection)
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    if (command.length() > 0) {
      Serial.print("Serial command received: ");
      Serial.println(command);
      handleSerialCommand(command);
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
          handleSerialCommand(command);
        }
      }

      // Check for incoming BLE command
      if (commandCharacteristic.written()) {
        String command = commandCharacteristic.value();
        Serial.print("Received BLE command: ");
        Serial.println(command);
        handleCommand(command);
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

void handleSerialCommand(String cmd) {
  cmd.trim();
  cmd.toUpperCase();

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
        Serial.println("OK:STARTED:" + mode + ":" + String(duration));
      } else {
        Serial.println("ERROR:INVALID_DURATION");
      }
    } else {
      Serial.println("ERROR:INVALID_FORMAT");
    }
  }
  else if (cmd == "STOP") {
    stopTherapy();
    Serial.println("OK:STOPPED");
  }
  else if (cmd == "STATUS") {
    if (therapyActive) {
      unsigned long elapsed = (millis() - therapyStartTime) / 1000;
      unsigned long remaining = (therapyDuration / 1000) - elapsed;
      String status = "ACTIVE:" + currentMode + ":" + String(remaining);
      Serial.println(status);
    } else {
      Serial.println("IDLE");
    }
  }
  else {
    Serial.println("ERROR:UNKNOWN_COMMAND");
  }
}

void handleCommand(String cmd) {
  cmd.trim();
  cmd.toUpperCase();

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
        commandCharacteristic.writeValue("OK:STARTED:" + mode + ":" + String(duration));
      } else {
        Serial.println("Invalid duration (must be 1-60 minutes)");
        commandCharacteristic.writeValue("ERROR:INVALID_DURATION");
      }
    } else {
      Serial.println("Invalid command format");
      commandCharacteristic.writeValue("ERROR:INVALID_FORMAT");
    }
  }
  else if (cmd == "STOP") {
    stopTherapy();
    commandCharacteristic.writeValue("OK:STOPPED");
  }
  else if (cmd == "STATUS") {
    if (therapyActive) {
      unsigned long elapsed = (millis() - therapyStartTime) / 1000;
      unsigned long remaining = (therapyDuration / 1000) - elapsed;
      String status = "ACTIVE:" + currentMode + ":" + String(remaining);
      commandCharacteristic.writeValue(status);
      Serial.println(status);
    } else {
      commandCharacteristic.writeValue("IDLE");
      Serial.println("Status: IDLE");
    }
  }
  else {
    Serial.println("Unknown command");
    commandCharacteristic.writeValue("ERROR:UNKNOWN_COMMAND");
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
    Serial.println("Invalid mode");
    commandCharacteristic.writeValue("ERROR:INVALID_MODE");
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
    stopTherapy();
    commandCharacteristic.writeValue("COMPLETED");

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
  analogWrite(LED_PIN_R, r);
  analogWrite(LED_PIN_G, g);
  analogWrite(LED_PIN_B, b);

  Serial.print("LED Color set to R:");
  Serial.print(r);
  Serial.print(" G:");
  Serial.print(g);
  Serial.print(" B:");
  Serial.println(b);
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
