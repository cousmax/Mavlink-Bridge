
This folder contains a MicroPython script for ESP32 that listens for UDP packets and forwards them as raw MAVLink packets over UART.

## Usage
1. Flash MicroPython firmware to your ESP32.
2. Edit `main.py` to set your WiFi SSID, password, and UART pins.
3. Upload `main.py` to the ESP32 (e.g., using `ampy` or `rshell`).
4. Connect the ESP32 UART to your MAVLink device.

## Script Overview

## Requirements


# MicroPython ESP32 UDP to MAVLink Bridge

This folder contains MicroPython scripts for ESP32 that bridge WiFi UDP packets to MAVLink over UART, with a full-featured OLED menu and OTA update support.

## Features

- WiFi UDP to MAVLink UART bridge
- SSD1306 OLED menu with button navigation
- Live status: GPS, heartbeat, WiFi RSSI
- Settings menu for UART baud rate and UDP port (persistent)
- Captive portal for WiFi setup
- OTA firmware update (via espota.py)
- Visual feedback: icons, progress bars
- Reboot/reset and WiFi credential reset

## Usage

1. Flash MicroPython firmware to your ESP32.
2. Upload all scripts in this folder to the ESP32 (e.g., using `ampy`, `rshell`, or Thonny).
3. On first boot, connect to the ESP32 AP and set WiFi credentials via captive portal.
4. Use the OLED menu to monitor status, change settings, and perform OTA updates.

## OTA Update Instructions

- Select "OTA Update" in the menu.
- On your PC, run:

	```bash
	python espota.py -i <ESP32_IP> -p 3232 --auth= -f <firmware.bin>
	```

- See OLED for troubleshooting tips.

## Requirements

- ESP32 board
- MicroPython firmware
- SSD1306 OLED display
- Buttons (GPIO 32, 33, 25)
- MAVLink device (UART)

## Tips

- All settings are saved to `settings.json`.
- WiFi credentials are saved to `wifi.json`.
- For full OTA, use the official MicroPython `.bin` file.

## Credits

- MAVLink protocol: [https://mavlink.io/](https://mavlink.io/)
- PlatformIO: [https://platformio.org/](https://platformio.org/)
- MicroPython: [https://micropython.org/](https://micropython.org/)
