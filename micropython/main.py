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

print("[MAIN] Starting MAVLink Bridge...")

# Load UART/UDP settings
def load_settings():
    try:
        with open('settings.json', 'r') as f:
            s = ujson.load(f)
            print("[MAIN] Loaded settings: UART={}, UDP={}".format(s.get('uart_baud', 57600), s.get('udp_port', 14550)))
            return s.get('uart_baud', 57600), s.get('udp_port', 14550)
    except Exception as e:
        print("[MAIN] No settings file, using defaults:", e)
        return 57600, 14550

uart_baud, udp_port = load_settings()


# UART settings
uart = machine.UART(1, baudrate=uart_baud, tx=17, rx=16)  # Adjust pins as needed
print("[MAIN] UART initialized: baud={}, tx=17, rx=16".format(uart_baud))

# OLED settings
i2c = machine.I2C(scl=machine.Pin(22), sda=machine.Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
print("[MAIN] OLED initialized on I2C pins 21/22")

def show_gps_on_oled(lat, lon, alt):
    print("[DISPLAY] Updating GPS on OLED: {:.6f}, {:.6f}, {:.1f}m".format(lat, lon, alt))
    oled.fill(0)
    oled.text('GPS Position:', 0, 0)
    oled.text('Lat: {:.5f}'.format(lat), 0, 16)
    oled.text('Lon: {:.5f}'.format(lon), 0, 28)
    oled.text('Alt: {:.1f}m'.format(alt), 0, 40)
    oled.show()

def run_udp_bridge(ssid, password):
    print("[BRIDGE] Starting UDP bridge with SSID:", ssid)
    # Connect to WiFi
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    print("[BRIDGE] Connecting to WiFi...")
    wlan.connect(ssid, password)
    
    timeout = 0
    while not wlan.isconnected() and timeout < 30:
        print("[BRIDGE] WiFi connection attempt {}...".format(timeout + 1))
        timeout += 1
        import time
        time.sleep(1)
    
    if wlan.isconnected():
        print('[BRIDGE] Connected to WiFi:', wlan.ifconfig())
        print('[BRIDGE] WiFi RSSI:', wlan.status('rssi'))
    else:
        print('[BRIDGE] WiFi connection failed after 30 seconds')
        return

    # Set up UDP socket
    UDP_IP = '0.0.0.0'
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, udp_port))
    print('[BRIDGE] Listening for UDP packets on port', udp_port)
    packet_count = 0
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            packet_count += 1
            print("[BRIDGE] Packet #{}: {} bytes from {}".format(packet_count, len(data), addr))
            uart.write(data)
            print("[BRIDGE] Forwarded to UART")
            
            gps = parse_gps_from_mavlink(data)
            if gps:
                lat, lon, alt = gps
                print("[GPS] Lat: {:.6f}, Lon: {:.6f}, Alt: {:.1f}m".format(lat, lon, alt))
                show_gps_on_oled(lat, lon, alt)
        except Exception as e:
            print("[BRIDGE] Error in UDP loop:", e)

def run_captive_portal():
    print("[MAIN] Starting captive portal for WiFi setup...")
    import captive_portal

def load_wifi_credentials():
    try:
        with open('wifi.json', 'r') as f:
            creds = ujson.load(f)
            print("[MAIN] WiFi credentials loaded")
            return creds.get('ssid'), creds.get('password')
    except Exception as e:
        print("[MAIN] No WiFi credentials found:", e)
        return None, None

print("[MAIN] Checking WiFi credentials...")
ssid, password = load_wifi_credentials()
if not ssid or not password:
    print('[MAIN] No WiFi credentials found. Starting captive portal...')
    run_captive_portal()
else:
    print("[MAIN] WiFi credentials found, starting bridge...")
    run_udp_bridge(ssid, password)
