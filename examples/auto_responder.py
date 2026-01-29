#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meshtastic Auto-Responder

What this does: Automatically responds to messages containing specific
keywords. Useful for status checks, away messages, or info bots.

Requirements:
- Python 3.8+
- meshtastic library 2.0+

Setup:
1. Install Python 3 if not already installed
2. Run: pip install "meshtastic>=2.0"
3. Connect your Meshtastic device via USB
4. Edit the RESPONSES dictionary below
5. Run: python3 auto_responder.py

Example: If someone sends "status", your node will reply with battery
and signal info. Add your own keywords and responses below.
"""

import meshtastic
import meshtastic.serial_interface
from pubsub import pub
from datetime import datetime
import signal
import sys
import time

# --- Configuration ---
# Add your trigger words and responses here
# Keywords are case-insensitive
RESPONSES = {
    "status": "AUTO-REPLY: Node is online and operational.",
    "help": "AUTO-REPLY: Available commands: status, help, info",
    "info": "AUTO-REPLY: This is an automated Meshtastic node.",
    "ping": "AUTO-REPLY: Pong!",
}

# Set to True to include battery info in status response
INCLUDE_BATTERY_IN_STATUS = True

# Cooldown per sender (seconds) - prevents response loops
RESPONSE_COOLDOWN = 60
# --------------------

interface = None
last_response_time = {}  # Track per-sender cooldowns


def get_battery_info(interface):
    """Get battery level if available."""
    try:
        if interface.localNode and interface.localNode.localConfig:
            # This varies by device - may not always be available
            return None  # Battery info from telemetry is more reliable
    except:
        pass
    return None


def on_receive(packet, interface):
    """Handle incoming packets and respond to keywords."""
    global last_response_time

    if 'decoded' not in packet:
        return

    portnum = packet['decoded'].get('portnum')

    if portnum == 'TEXT_MESSAGE_APP':
        # Extract message details
        sender_id = packet.get('fromId', 'unknown')
        message = packet['decoded'].get('payload', b'').decode('utf-8', errors='replace')
        message_lower = message.lower().strip()
        timestamp = datetime.now().strftime('%H:%M:%S')

        print(f"[{timestamp}] From {sender_id}: {message}")

        # Check cooldown for this sender
        current_time = time.time()
        last_time = last_response_time.get(sender_id, 0)

        if current_time - last_time < RESPONSE_COOLDOWN:
            print(f"  (Cooldown active for {sender_id}, not responding)")
            return

        # Check for trigger keywords
        for keyword, response in RESPONSES.items():
            if keyword.lower() in message_lower:
                # Special handling for status - add battery if configured
                if keyword.lower() == "status" and INCLUDE_BATTERY_IN_STATUS:
                    battery = get_battery_info(interface)
                    if battery:
                        response = f"{response} Battery: {battery}%"

                print(f"  >>> Responding to '{keyword}': {response}")
                interface.sendText(response, destinationId=sender_id)
                last_response_time[sender_id] = current_time
                break  # Only respond once per message


def shutdown(sig, frame):
    """Clean up on exit."""
    print("\nShutting down...")
    if interface:
        interface.close()
    sys.exit(0)


def main():
    global interface

    # Set up clean shutdown
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Subscribe to incoming messages
    pub.subscribe(on_receive, "meshtastic.receive")

    # Connect to device
    print("Connecting to Meshtastic device...")
    try:
        interface = meshtastic.serial_interface.SerialInterface()
    except Exception as e:
        print(f"Could not connect to Meshtastic device: {e}")
        print("Make sure your device is plugged in via USB")
        sys.exit(1)

    print("Connected! Auto-responder active.")
    print(f"Listening for keywords: {', '.join(RESPONSES.keys())}")
    print("Press Ctrl+C to stop\n")

    # Keep running
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
