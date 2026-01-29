# Meshtastic Python Reference

## Troubleshooting Guide

### Connection Issues

#### "Could not find a connected Meshtastic device"
**Cause:** Device not detected on USB port

**Solutions:**
1. Check USB cable supports data (not charge-only)
2. Try different USB port
3. Unplug and replug the device
4. Check device is powered on

**Linux/Mac - find your device:**
```bash
ls /dev/tty* | grep -E "(USB|ACM)"
```

**Windows - find COM port:**
Check Device Manager → Ports (COM & LPT)

**Specify port manually:**
```python
interface = meshtastic.serial_interface.SerialInterface(devPath="/dev/ttyUSB0")
```

---

#### "Permission denied" on Linux
**Cause:** User not in dialout group

**Solution:**
```bash
sudo usermod -a -G dialout $USER
# Log out and back in for changes to take effect
```

---

#### "No module named 'meshtastic'"
**Cause:** Library not installed

**Solution:**
```bash
pip install meshtastic
# Or if using Python 3 specifically:
pip3 install meshtastic
```

---

#### "Multiple devices found"
**Cause:** More than one serial device connected

**Solution:** Specify the exact port:
```python
interface = meshtastic.serial_interface.SerialInterface(devPath="/dev/ttyACM0")
```

---

#### Bluetooth connection fails
**Cause:** Various pairing issues

**Solutions:**
1. Forget device in system Bluetooth settings
2. Re-pair the device
3. Ensure device is in pairing mode
4. Try serial/USB instead (more reliable)

---

#### TCP connection timeout
**Cause:** WiFi not configured or wrong hostname

**Solutions:**
1. Verify device WiFi is enabled and connected
2. Check hostname/IP is correct
3. Ensure device and computer on same network
4. Try IP address instead of hostname

---

### Message Issues

#### Messages not sending
**Possible causes:**
- No other nodes in range
- Mismatched channel settings
- Device in airplane mode

**Debug steps:**
```python
# Check if device is connected
print(interface.myInfo)

# List known nodes
for node in interface.nodes.values():
    print(node)
```

---

#### Not receiving messages
**Possible causes:**
- Callback not subscribed
- Wrong channel
- Other nodes out of range

**Verify subscription:**
```python
from pubsub import pub

def on_receive(packet, interface):
    print(f"Got packet: {packet}")

# Make sure this is called BEFORE the main loop
pub.subscribe(on_receive, "meshtastic.receive")
```

---

### Telemetry Issues

#### No telemetry data
**Cause:** Telemetry not enabled or no sensors attached

**Check device capabilities:**
```bash
meshtastic --info
```

**Note:** Not all devices have built-in sensors. Check hardware section below.

---

## Hardware Capabilities

### Devices WITH Built-in GPS
- LILYGO T-Beam (all versions)
- LILYGO T-Echo
- Seeed SenseCAP T1000-E
- B&Q Nano G2 Ultra
- Heltec Mesh Node T114 (some versions)
- RAK WisBlock (with GPS module added)

### Devices WITHOUT Built-in GPS
- Heltec LoRa 32 (all versions)
- LILYGO T3-S3
- RAK WisBlock base (GPS is optional add-on)

### Devices WITH Built-in Sensors
- RAK WisBlock (with sensor modules)
- Some T-Echo variants

### WiFi Capable (ESP32-based)
- LILYGO T-Beam
- LILYGO T3-S3
- Heltec LoRa 32 v3
- RAK WisBlock with ESP32-S3 core

### Low Power (nRF52-based) - Best for Solar/Battery
- LILYGO T-Echo
- RAK WisBlock with RAK4631 core
- Seeed SenseCAP T1000-E
- B&Q Nano G2 Ultra

### When to Use Serial vs TCP vs Bluetooth

| Connection | Best For | Reliability |
|------------|----------|-------------|
| **Serial/USB** | Raspberry Pi, always-on setups | Most reliable |
| **TCP/WiFi** | Remote access, no physical connection | Good (requires WiFi) |
| **Bluetooth** | Mobile, temporary connections | Less reliable |

**Recommendation:** Use Serial/USB for any automated scripts that need to run continuously.

---

## Testing Checklist

Before deploying your script, verify:

### 1. Device Connection
```bash
# Does the CLI see your device?
meshtastic --info
```
Expected: Shows device info, region, channels

### 2. Node Discovery
```bash
# Can you see other nodes?
meshtastic --nodes
```
Expected: Lists nearby nodes (may take a few minutes)

### 3. Manual Message Test
```bash
# Can you send a message?
meshtastic --sendtext "Test from CLI"
```
Expected: Message appears on other devices

### 4. Python Connection Test
```python
import meshtastic
import meshtastic.serial_interface

interface = meshtastic.serial_interface.SerialInterface()
print("Connected!")
print(f"My node ID: {interface.myInfo}")
interface.close()
```
Expected: Prints "Connected!" and node info

### 5. Receive Test
```python
from pubsub import pub
import meshtastic
import meshtastic.serial_interface

def on_receive(packet, interface):
    print(f"Received: {packet}")

pub.subscribe(on_receive, "meshtastic.receive")
interface = meshtastic.serial_interface.SerialInterface()

print("Listening... send a message from another device")
import time
time.sleep(60)  # Wait 1 minute for messages
interface.close()
```
Expected: Prints packets when messages arrive

---

## Mesh Network Best Practices

### Do's
- Keep hop count at 3 (default) unless you have a specific reason
- Use CLIENT role for most nodes
- Test configurations before remote deployment
- Use good quality antennas
- Position nodes with line of sight when possible

### Don'ts
- Don't spam the network with frequent messages
- Don't use ROUTER role unless strategically placed
- Don't power on without antenna attached (damages radio)
- Don't share primary channel widely (use secondary channels for groups)

### Rate Limiting
The network has limited bandwidth. Good practices:
- Telemetry updates: Every 15-30 minutes minimum
- Position updates: Every 5-15 minutes minimum
- Avoid sending messages more than once per minute in busy meshes

### Battery Considerations
- nRF52 devices last much longer than ESP32
- Disable WiFi if not needed
- Reduce screen timeout
- Use lower transmit power if nodes are close

---

## Common Python Patterns

### Async-Safe Connection
```python
import meshtastic
import meshtastic.serial_interface
from pubsub import pub
import time

interface = None

def on_connection(interface, topic=pub.AUTO_TOPIC):
    print("Connected to device")

def on_receive(packet, interface):
    # Handle incoming packets
    pass

pub.subscribe(on_connection, "meshtastic.connection.established")
pub.subscribe(on_receive, "meshtastic.receive")

interface = meshtastic.serial_interface.SerialInterface()

# Keep running
while True:
    time.sleep(1)
```

### Filtering Message Types
```python
def on_receive(packet, interface):
    if 'decoded' not in packet:
        return

    portnum = packet['decoded'].get('portnum')

    if portnum == 'TEXT_MESSAGE_APP':
        handle_text(packet)
    elif portnum == 'POSITION_APP':
        handle_position(packet)
    elif portnum == 'TELEMETRY_APP':
        handle_telemetry(packet)
    elif portnum == 'NODEINFO_APP':
        handle_nodeinfo(packet)
```

### Safe Shutdown
```python
import signal
import sys

def shutdown(sig, frame):
    print("\nShutting down gracefully...")
    if interface:
        interface.close()
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)
```

### Logging to File
```python
import logging

logging.basicConfig(
    filename='meshtastic.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

def on_receive(packet, interface):
    logging.info(f"Packet: {packet}")
```
