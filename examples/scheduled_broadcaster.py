#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meshtastic Scheduled Broadcaster

What this does: Sends a message to the mesh at regular intervals.
Useful for check-ins, status updates, or heartbeat signals.

Requirements:
- Python 3.8+
- meshtastic library 2.0+

Setup:
1. Install Python 3 if not already installed
2. Run: pip install "meshtastic>=2.0"
3. Connect your Meshtastic device via USB
4. Edit the configuration below
5. Run: python3 scheduled_broadcaster.py

Messages are broadcast to all nodes on your primary channel.
"""

import meshtastic
import meshtastic.serial_interface
from datetime import datetime
import signal
import sys
import time

# --- Configuration ---
# How often to send (in minutes)
INTERVAL_MINUTES = 60

# Message to send (you can include {time} to insert current time)
MESSAGE = "Automated check-in at {time}"

# Channel to broadcast on (0 = primary channel)
CHANNEL_INDEX = 0
# --------------------

interface = None
running = True


def send_scheduled_message():
    """Send the scheduled message."""
    current_time = datetime.now().strftime('%H:%M')
    message = MESSAGE.format(time=current_time)

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] Sending: {message}")

    try:
        interface.sendText(message, channelIndex=CHANNEL_INDEX)
        print("  Message sent successfully")
    except Exception as e:
        print(f"  Error sending message: {e}")


def shutdown(sig, frame):
    """Clean up on exit."""
    global running
    print("\nShutting down...")
    running = False
    if interface:
        interface.close()
    sys.exit(0)


def main():
    global interface, running

    # Set up clean shutdown
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Connect to device
    print("Connecting to Meshtastic device...")
    try:
        interface = meshtastic.serial_interface.SerialInterface()
    except Exception as e:
        print(f"Could not connect to Meshtastic device: {e}")
        print("Make sure your device is plugged in via USB")
        sys.exit(1)

    print(f"Connected! Will broadcast every {INTERVAL_MINUTES} minutes")
    print(f"Message template: {MESSAGE}")
    print("Press Ctrl+C to stop\n")

    # Send first message immediately
    send_scheduled_message()

    # Calculate interval in seconds
    interval_seconds = INTERVAL_MINUTES * 60

    # Main loop
    last_send = time.time()
    while running:
        time.sleep(1)

        # Check if it's time to send
        if time.time() - last_send >= interval_seconds:
            send_scheduled_message()
            last_send = time.time()


if __name__ == "__main__":
    main()
