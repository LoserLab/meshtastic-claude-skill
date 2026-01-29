#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meshtastic Battery Monitor

What this does: Monitors battery levels of all nodes on your mesh and
sends an alert when any node's battery drops below a threshold.
Also logs battery levels to a file for tracking over time.

Requirements:
- Python 3.8+
- meshtastic library 2.0+

Setup:
1. Install Python 3 if not already installed
2. Run: pip install "meshtastic>=2.0"
3. Connect your Meshtastic device via USB
4. Edit the configuration below
5. Run: python3 battery_monitor.py

Useful for monitoring solar nodes or remote installations.
"""

import meshtastic
import meshtastic.serial_interface
from pubsub import pub
from datetime import datetime
import signal
import sys
import time

# --- Configuration ---
# Alert when battery drops below this percentage
LOW_BATTERY_THRESHOLD = 20

# Log file for battery history
LOG_FILE = "battery_log.csv"

# How often to allow alerts per node (seconds)
ALERT_COOLDOWN = 3600  # 1 hour
# --------------------

interface = None
last_alert_time = {}  # Per-node cooldown tracking
node_batteries = {}   # Track last known battery levels


def get_node_name(interface, node_id):
    """Get the friendly name of a node, or return the ID if unknown."""
    if interface.nodes:
        node = interface.nodes.get(node_id)
        if node and 'user' in node:
            return node['user'].get('longName', node_id)
    return node_id


def ensure_log_header():
    """Create log file with header if it doesn't exist."""
    import os
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            f.write("timestamp,node_id,node_name,battery_percent,voltage\n")


def on_receive(packet, interface):
    """Handle incoming packets and monitor battery levels."""
    global last_alert_time, node_batteries

    if 'decoded' not in packet:
        return

    portnum = packet['decoded'].get('portnum')

    if portnum == 'TELEMETRY_APP':
        telemetry = packet['decoded'].get('telemetry', {})
        device_metrics = telemetry.get('deviceMetrics', {})

        battery_level = device_metrics.get('batteryLevel')
        voltage = device_metrics.get('voltage')

        if battery_level is None:
            return

        # Node info
        sender_id = packet.get('fromId', 'unknown')
        sender_name = get_node_name(interface, sender_id)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Print status
        voltage_str = f" ({voltage:.2f}V)" if voltage else ""
        print(f"[{timestamp}] {sender_name}: {battery_level}%{voltage_str}")

        # Log to file
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{timestamp},{sender_id},{sender_name},{battery_level},{voltage or ''}\n")

        # Track battery level
        previous_level = node_batteries.get(sender_id)
        node_batteries[sender_id] = battery_level

        # Check for low battery alert
        if battery_level <= LOW_BATTERY_THRESHOLD:
            current_time = time.time()
            last_time = last_alert_time.get(sender_id, 0)

            # Only alert if cooldown has passed and battery is newly low
            # (or dropped further since last alert)
            if current_time - last_time >= ALERT_COOLDOWN:
                alert_msg = f"LOW BATTERY: {sender_name} at {battery_level}%"
                print(f">>> ALERT: {alert_msg}")
                interface.sendText(alert_msg)
                last_alert_time[sender_id] = current_time


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

    # Ensure log file exists
    ensure_log_header()

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

    print(f"Connected! Monitoring battery levels")
    print(f"Alert threshold: {LOW_BATTERY_THRESHOLD}%")
    print(f"Logging to: {LOG_FILE}")
    print("Press Ctrl+C to stop\n")

    # Keep running
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
