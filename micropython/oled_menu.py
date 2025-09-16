
# SSD1306 OLED menu for ESP32 (MicroPython)
# Uses I2C defaults: SDA=21, SCL=22
import machine
import ssd1306
import network
import time
import ujson

# Button pins
PIN_UP = 32
PIN_DOWN = 33
PIN_SELECT = 25
btn_up = machine.Pin(PIN_UP, machine.Pin.IN, machine.Pin.PULL_UP)
btn_down = machine.Pin(PIN_DOWN, machine.Pin.IN, machine.Pin.PULL_UP)
btn_select = machine.Pin(PIN_SELECT, machine.Pin.IN, machine.Pin.PULL_UP)

# Initialize I2C and OLED
i2c = machine.I2C(scl=machine.Pin(22), sda=machine.Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
print("[MENU] OLED initialized")


# Expanded menu options
MENU = [
    'WiFi Status',
    'GPS Data',
    'MAVLink Heartbeat',
    'Signal Strength',
    'Start Captive Portal',
    'Bridge Status',
    'Reboot/Reset',
    'Settings',
    'OTA Update'
]

selected = 0


# Placeholder for GPS, heartbeat, RSSI
gps_data = {'lat': None, 'lon': None, 'alt': None}
heartbeat = False
rssi = None
heartbeat_last = 0

def draw_heartbeat_icon(x, y, status):
    # Simple heart icon, filled if status OK
    heart = [
        (1,0),(2,0),(0,1),(3,1),(0,2),(3,2),(1,3),(2,3)
    ]
    for px, py in heart:
        oled.pixel(x+px, y+py, 1 if status else 0)


def show_menu():
    oled.fill(0)
    oled.text('MAVLink Bridge', 0, 0)
    for i, item in enumerate(MENU):
        prefix = '>' if i == selected else ' '
        oled.text(prefix + item, 0, 16 + i*8)
    oled.show()

def draw_wifi_icon(x, y, connected):
    # Simple WiFi icon
    for i in range(4):
        oled.line(x-i*2, y+i*3, x+i*2, y+i*3, 1 if connected else 0)
    oled.pixel(x, y+13, 1 if connected else 0)

def show_wifi_status():
    print("[MENU] Displaying WiFi status")
    wlan = network.WLAN(network.STA_IF)
    oled.fill(0)
    oled.text('WiFi Status:', 0, 0)
    draw_wifi_icon(110, 0, wlan.isconnected())
    if wlan.isconnected():
        ip = wlan.ifconfig()[0]
        rssi = wlan.status('rssi')
        print("[MENU] WiFi connected: IP={}, RSSI={}".format(ip, rssi))
        oled.text('Connected', 0, 16)
        oled.text(ip, 0, 28)
    else:
        print("[MENU] WiFi not connected")
        oled.text('Not connected', 0, 16)
    oled.show()

def draw_gps_icon(x, y, has_fix):
    # Simple GPS satellite icon
    oled.circle(x, y+8, 6, 1 if has_fix else 0)
    oled.pixel(x, y+8, 1 if has_fix else 0)

def show_gps_data():
    oled.fill(0)
    oled.text('GPS Data:', 0, 0)
    draw_gps_icon(110, 0, gps_data['lat'] is not None)
    if gps_data['lat']:
        oled.text('Lat: {:.5f}'.format(gps_data['lat']), 0, 16)
        oled.text('Lon: {:.5f}'.format(gps_data['lon']), 0, 28)
        oled.text('Alt: {:.1f}m'.format(gps_data['alt']), 0, 40)
    else:
        oled.text('No GPS', 0, 16)
    oled.show()


def show_heartbeat():
    oled.fill(0)
    oled.text('MAVLink Heartbeat:', 0, 0)
    status = 'OK' if heartbeat else 'None'
    oled.text('Status: ' + status, 0, 16)
    draw_heartbeat_icon(100, 16, heartbeat)
    oled.show()


def show_signal_strength():
    print("[MENU] Displaying WiFi signal strength")
    wlan = network.WLAN(network.STA_IF)
    oled.fill(0)
    oled.text('WiFi Signal:', 0, 0)
    if wlan.isconnected():
        try:
            rssi_val = wlan.status('rssi')
            print("[MENU] WiFi RSSI: {}".format(rssi_val))
            oled.text('RSSI: {}'.format(rssi_val), 0, 16)
        except Exception as e:
            print("[MENU] Error getting RSSI:", e)
            oled.text('RSSI N/A', 0, 16)
    else:
        print("[MENU] WiFi not connected for RSSI check")
        oled.text('Not connected', 0, 16)
    oled.show()

def start_captive_portal():
    print("[MENU] Starting captive portal from menu")
    oled.fill(0)
    oled.text('Starting portal...', 0, 0)
    oled.show()
    import captive_portal

def show_bridge_status():
    print("[MENU] Displaying bridge status")
    oled.fill(0)
    oled.text('Bridge running', 0, 0)
    oled.show()

def draw_progress_bar(x, y, w, h, percent):
    oled.rect(x, y, w, h, 1)
    fill_w = int(w * percent)
    if fill_w > 0:
        oled.fill_rect(x+1, y+1, fill_w-2, h-2, 1)

import os

def reboot_reset():
    # Prompt for WiFi reset
    oled.fill(0)
    oled.text('Reboot/Reset:', 0, 0)
    oled.text('Press SELECT to', 0, 16)
    oled.text('reset WiFi', 0, 28)
    oled.text('Press UP/DOWN to', 0, 40)
    oled.text('just reboot', 0, 52)
    oled.show()
    confirmed = False
    while True:
        if not btn_select.value():
            # Confirm WiFi reset
            oled.fill(0)
            oled.text('Resetting WiFi...', 0, 0)
            oled.show()
            try:
                os.remove('wifi.json')
            except:
                pass
            time.sleep(1)
            machine.reset()
        if not btn_up.value() or not btn_down.value():
            # Just reboot
            oled.fill(0)
            oled.text('Rebooting...', 0, 0)
            for i in range(11):
                draw_progress_bar(10, 20, 100, 10, i/10)
                oled.show()
                time.sleep(0.1)
            machine.reset()


# Load settings from file
def load_settings():
    try:
        with open('settings.json', 'r') as f:
            s = ujson.load(f)
            return s.get('uart_baud', 57600), s.get('udp_port', 14550)
    except:
        return 57600, 14550

def save_settings(uart_baud, udp_port):
    print("[MENU] Saving settings: UART={}, UDP={}".format(uart_baud, udp_port))
    with open('settings.json', 'w') as f:
        ujson.dump({'uart_baud': uart_baud, 'udp_port': udp_port}, f)

uart_baud, udp_port = load_settings()
print("[MENU] Settings loaded: UART={}, UDP={}".format(uart_baud, udp_port))


def show_settings():
    global uart_baud, udp_port
    setting_selected = 0
    settings_menu = ['UART Baud', 'UDP Port', 'Exit']
    while True:
        oled.fill(0)
        oled.text('Settings:', 0, 0)
        for i, item in enumerate(settings_menu):
            prefix = '>' if i == setting_selected else ' '
            if i == 0:
                val = str(uart_baud)
            elif i == 1:
                val = str(udp_port)
            else:
                val = ''
            oled.text(prefix + item + ' ' + val, 0, 16 + i*12)
        oled.show()
        # Button handling for settings
        if not btn_up.value():
            setting_selected = (setting_selected - 1) % len(settings_menu)
            wait_for_release(btn_up)
        if not btn_down.value():
            setting_selected = (setting_selected + 1) % len(settings_menu)
            wait_for_release(btn_down)
        if not btn_select.value():
            if setting_selected == 0:
                uart_baud = next_baud(uart_baud)
                save_settings(uart_baud, udp_port)
            elif setting_selected == 1:
                udp_port = next_port(udp_port)
                save_settings(uart_baud, udp_port)
            elif setting_selected == 2:
                break
            wait_for_release(btn_select)

def next_baud(current):
    bauds = [57600, 115200, 230400, 460800]
    idx = bauds.index(current) if current in bauds else 0
    return bauds[(idx + 1) % len(bauds)]

def next_port(current):
    ports = [14550, 14551, 14552, 14553]
    idx = ports.index(current) if current in ports else 0
    return ports[(idx + 1) % len(ports)]

def show_ota_update():
    print("[MENU] OTA update selected")
    ip = network.WLAN(network.STA_IF).ifconfig()[0]
    print("[MENU] Device IP for OTA: {}".format(ip))
    oled.fill(0)
    oled.text('OTA Update Mode', 0, 0)
    oled.text('1. On your PC:', 0, 12)
    oled.text('2. Run:', 0, 22)
    oled.text('espota.py -i {}'.format(ip), 0, 32)
    oled.text('-p 3232 -f bin'.format(ip), 0, 42)
    oled.text('3. Wait for finish', 0, 52)
    oled.show()
    time.sleep(4)
    oled.fill(0)
    oled.text('Troubleshooting:', 0, 0)
    oled.text('- PC & ESP32 same WiFi', 0, 12)
    oled.text('- Firewall allows 3232', 0, 22)
    oled.text('- Use correct bin file', 0, 32)
    oled.text('- Reboot if fails', 0, 42)
    oled.show()
    time.sleep(4)
    oled.fill(0)
    oled.text('Rebooting for OTA...', 0, 24)
    oled.show()
    time.sleep(2)
    print("[MENU] Rebooting for OTA mode...")
    machine.reset()

def handle_select():
    print("[MENU] Menu item {} selected".format(selected))
    if selected == 0:
        show_wifi_status()
    elif selected == 1:
        show_gps_data()
    elif selected == 2:
        show_heartbeat()
    elif selected == 3:
        show_signal_strength()
    elif selected == 4:
        start_captive_portal()
    elif selected == 5:
        show_bridge_status()
    elif selected == 6:
        reboot_reset()
    elif selected == 7:
        show_settings()
    elif selected == 8:
        show_ota_update()
    time.sleep(2)
    show_menu()



# Main loop for button navigation and dynamic status
show_menu()
last_update = time.ticks_ms()
dynamic_state = 0  # 0: heartbeat, 1: WiFi RSSI

# Button debounce helper
def wait_for_release(pin, timeout=500):
    start = time.ticks_ms()
    while not pin.value():
        if time.ticks_diff(time.ticks_ms(), start) > timeout:
            break
        time.sleep_ms(10)

while True:
    # Button handling with debounce
    if not btn_up.value():
        selected = (selected - 1) % len(MENU)
        show_menu()
        wait_for_release(btn_up)
    if not btn_down.value():
        selected = (selected + 1) % len(MENU)
        show_menu()
        wait_for_release(btn_down)
    if not btn_select.value():
        handle_select()
        wait_for_release(btn_select)
    # Dynamic status update every 2 seconds
    if time.ticks_diff(time.ticks_ms(), last_update) > 2000:
        if dynamic_state == 0:
            show_heartbeat()
            dynamic_state = 1
        elif dynamic_state == 1:
            show_signal_strength()
            dynamic_state = 2
        else:
            show_gps_data()
            dynamic_state = 0
        last_update = time.ticks_ms()
