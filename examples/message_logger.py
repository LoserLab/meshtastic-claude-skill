#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meshtastic Message Logger

What this does: Saves all messages from your mesh network to a text file
with timestamps. Useful for keeping a record of communications.

Requirements:
- Python 3.8+
- meshtastic library 2.0+

Setup:
1. Install Python 3 if not already installed
2. Run: pip install "meshtastic>=2.0"
3. Connect your Meshtastic device via USB
4. Run: python3 message_logger.py

Messages are saved to: meshtastic_messages.log
"""

import meshtastic
import meshtastic.serial_interface
from pubsub import pub
from datetime import datetime
import signal
import sys

# --- Configuration ---
LOG_FILE = "meshtastic_messages.log"
# --------------------

interface = None


def get_node_name(interface, node_id):
    """Get the friendly name of a node, or return the ID if unknown."""
    if interface.nodes:
        node = interface.nodes.get(node_id)
        if node and 'user' in node:
            return node['user'].get('longName', node_id)
    return node_id


def on_receive(packet, interface):
    """Handle incoming packets and log text messages."""
    if 'decoded' not in packet:
        return

    portnum = packet['decoded'].get('portnum')

    if portnum == 'TEXT_MESSAGE_APP':
        # Extract message details
        sender_id = packet.get('fromId', 'unknown')
        sender_name = get_node_name(interface, sender_id)
        message = packet['decoded'].get('payload', b'').decode('utf-8', errors='replace')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Format the log entry
        log_entry = f"[{timestamp}] {sender_name}: {message}"

        # Print to console
        print(log_entry)

        # Save to file
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')


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

    print(f"Connected! Logging messages to {LOG_FILE}")
    print("Press Ctrl+C to stop\n")

    # Keep running
    while True:
        import time
        time.sleep(1)


if __name__ == "__main__":
    main()
