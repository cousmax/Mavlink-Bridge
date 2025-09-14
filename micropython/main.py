wlan.active(True)
wlan.connect(SSID, PASSWORD)
sock.bind((UDP_IP, UDP_PORT))



import network
import socket
import machine
import ujson
import os
import ssd1306
from mavlink_gps import parse_gps_from_mavlink

# Load UART/UDP settings
def load_settings():
    try:
        with open('settings.json', 'r') as f:
            s = ujson.load(f)
            return s.get('uart_baud', 57600), s.get('udp_port', 14550)
    except:
        return 57600, 14550

uart_baud, udp_port = load_settings()


# UART settings
uart = machine.UART(1, baudrate=uart_baud, tx=17, rx=16)  # Adjust pins as needed

# OLED settings
i2c = machine.I2C(scl=machine.Pin(22), sda=machine.Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

def show_gps_on_oled(lat, lon, alt):
    oled.fill(0)
    oled.text('GPS Position:', 0, 0)
    oled.text('Lat: {:.5f}'.format(lat), 0, 16)
    oled.text('Lon: {:.5f}'.format(lon), 0, 28)
    oled.text('Alt: {:.1f}m'.format(alt), 0, 40)
    oled.show()

def run_udp_bridge(ssid, password):
    # Connect to WiFi
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        pass
    print('Connected to WiFi:', wlan.ifconfig())

    # Set up UDP socket
    UDP_IP = '0.0.0.0'
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, udp_port))
    print('Listening for UDP packets on port', udp_port)
    while True:
        data, addr = sock.recvfrom(1024)
        uart.write(data)
        gps = parse_gps_from_mavlink(data)
        if gps:
            lat, lon, alt = gps
            show_gps_on_oled(lat, lon, alt)

def run_captive_portal():
    import captive_portal

def load_wifi_credentials():
    try:
        with open('wifi.json', 'r') as f:
            creds = ujson.load(f)
            return creds.get('ssid'), creds.get('password')
    except:
        return None, None

ssid, password = load_wifi_credentials()
if not ssid or not password:
    print('No WiFi credentials found. Starting captive portal...')
    run_captive_portal()
else:
    run_udp_bridge(ssid, password)
