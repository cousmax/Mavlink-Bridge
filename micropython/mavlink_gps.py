# Minimal MAVLink GPS parser for GLOBAL_POSITION_INT
# Only extracts lat/lon/alt from raw MAVLink packets

def parse_gps_from_mavlink(packet):
    # MAVLink v1: GLOBAL_POSITION_INT msg id = 33, payload starts at byte 6
    # Packet: [STX][LEN][SEQ][SYS][COMP][MSGID][PAYLOAD...]
    if len(packet) >= 28 and packet[5] == 33:
        # Extract payload
        payload = packet[6:6+18]
        lat = int.from_bytes(payload[0:4], 'little', signed=True) / 1e7
        lon = int.from_bytes(payload[4:8], 'little', signed=True) / 1e7
        alt = int.from_bytes(payload[8:12], 'little', signed=True) / 1000
        return lat, lon, alt
    return None
