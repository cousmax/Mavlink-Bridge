# MicroPython ESP32 UDP to MAVLink Bridge

This folder contains a MicroPython script for ESP32 that listens for UDP packets and forwards them as raw MAVLink packets over UART.

## Usage
1. Flash MicroPython firmware to your ESP32.
2. Edit `main.py` to set your WiFi SSID, password, and UART pins.
3. Upload `main.py` to the ESP32 (e.g., using `ampy` or `rshell`).
4. Connect the ESP32 UART to your MAVLink device.

## Script Overview
- Connects to WiFi
- Listens for UDP packets on port 14550
- Forwards received packets to UART

## Requirements
- ESP32 board
- MicroPython firmware
- UART connection to MAVLink device
