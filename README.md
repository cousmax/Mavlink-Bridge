# Mavlink Bridge Project

This project provides a WiFi-to-MAVLink bridge using ESP32 and MicroPython, with a modern OLED menu interface and OTA update support.

## Features
- WiFi UDP to MAVLink UART bridge
- OLED display with menu navigation (buttons)
- Live status screens: GPS, MAVLink heartbeat, WiFi RSSI
- Settings menu for UART baud rate and UDP port (persistent)
- Reboot/reset and WiFi credential reset
- OTA firmware update support (via espota.py)
- Visual feedback: icons, progress bars
- Captive portal for WiFi setup

## Getting Started
1. Flash MicroPython to your ESP32.
2. Upload scripts from `micropython/` to the device.
3. On first boot, connect to the ESP32 AP and set WiFi credentials via captive portal.
4. Use the OLED menu to monitor status, change settings, and perform OTA updates.

## OTA Update Instructions
- Select "OTA Update" in the menu.
- On your PC, run:
  ```
  python espota.py -i <ESP32_IP> -p 3232 --auth= -f <firmware.bin>
  ```
- See OLED for troubleshooting tips.

## Directory Overview
- `src/` - PlatformIO C++ source (if used)
- `micropython/` - MicroPython scripts and menu logic
- `lib/` - Project-specific libraries
- `include/` - Header files
- `test/` - Unit tests

## Requirements
- ESP32 board
- MicroPython firmware
- SSD1306 OLED display
- Buttons (GPIO 32, 33, 25)

## Credits
- MAVLink protocol: https://mavlink.io/
- PlatformIO: https://platformio.org/
- MicroPython: https://micropython.org/
