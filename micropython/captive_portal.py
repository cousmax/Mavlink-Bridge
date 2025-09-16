import network
import socket
import ure
import ujson

AP_SSID = 'MAVLinkBridge-Setup'
AP_PASSWORD = ''  # Open network for simplicity

print("[PORTAL] Starting captive portal...")
# Start Access Point
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=AP_SSID, password=AP_PASSWORD)
print("[PORTAL] Access Point started: SSID={}".format(AP_SSID))

# Simple HTML form for WiFi credentials
HTML = """
<!DOCTYPE html>
<html>
<head><title>WiFi Setup</title></head>
<body>
<h2>Enter WiFi Credentials</h2>
<form action="/" method="post">
SSID: <input name="ssid" type="text" /><br>
Password: <input name="password" type="password" /><br>
<input type="submit" value="Connect" />
</form>
</body>
</html>
"""

# Save credentials to file
def save_credentials(ssid, password):
    print("[PORTAL] Saving credentials: SSID={}".format(ssid))
    with open('wifi.json', 'w') as f:
        ujson.dump({'ssid': ssid, 'password': password}, f)
    print("[PORTAL] Credentials saved successfully")

# Simple web server
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print('[PORTAL] Captive portal running. Connect to WiFi:', AP_SSID)

while True:
    cl, addr = s.accept()
    print('[PORTAL] Client connected from:', addr)
    req = cl.recv(1024)
    req = req.decode('utf-8')
    print('[PORTAL] Request received:', req[:100])  # First 100 chars
    if 'POST' in req:
        match = ure.search('ssid=([^&]*)&password=([^&]*)', req)
        if match:
            ssid = match.group(1)
            password = match.group(2)
            print('[PORTAL] Credentials received via POST')
            save_credentials(ssid, password)
            response = '<h2>Saved! Reboot device.</h2>'
        else:
            print('[PORTAL] Invalid POST data')
            response = '<h2>Error: Invalid input.</h2>'
    else:
        print('[PORTAL] Serving setup page')
        response = HTML
    cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    cl.send(response)
    cl.close()
