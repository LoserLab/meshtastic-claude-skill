#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meshtastic Temperature Alert

What this does: Monitors temperature from mesh nodes and sends an alert
message when temperature drops below (or rises above) a threshold.

Requirements:
- Python 3.8+
- meshtastic library 2.0+

Setup:
1. Install Python 3 if not already installed
2. Run: pip install "meshtastic>=2.0"
3. Connect your Meshtastic device via USB
4. Edit the configuration below
5. Run: python3 temperature_alert.py

Note: Requires a node with temperature sensor (RAK with environment module,
or external sensor). The alert is sent over the mesh network.
"""

import meshtastic
import meshtastic.serial_interface
from pubsub import pub
from datetime import datetime
import signal
import sys
import time

# --- Configuration ---
# Temperature threshold (Fahrenheit)
LOW_TEMP_THRESHOLD = 40.0   # Alert if temp drops below this
HIGH_TEMP_THRESHOLD = 90.0  # Alert if temp rises above this

# How often to allow alerts (seconds) - prevents spam
ALERT_COOLDOWN = 1800  # 30 minutes

# Set to True to use Celsius instead of Fahrenheit
USE_CELSIUS = False
# --------------------

interface = None
last_alert_time = 0


def celsius_to_fahrenheit(celsius):
    """Convert Celsius to Fahrenheit."""
    return (celsius * 9/5) + 32


def on_receive(packet, interface):
    """Handle incoming packets and check for temperature alerts."""
    global last_alert_time

    if 'decoded' not in packet:
        return

    portnum = packet['decoded'].get('portnum')

    if portnum == 'TELEMETRY_APP':
        telemetry = packet['decoded'].get('telemetry', {})
        env_metrics = telemetry.get('environmentMetrics', {})

        if 'temperature' in env_metrics:
            temp_celsius = env_metrics['temperature']

            # Convert if needed
            if USE_CELSIUS:
                temp = temp_celsius
                unit = "C"
            else:
                temp = celsius_to_fahrenheit(temp_celsius)
                unit = "F"

            # Get sender info
            sender_id = packet.get('fromId', 'unknown')
            timestamp = datetime.now().strftime('%H:%M:%S')

            print(f"[{timestamp}] Temperature from {sender_id}: {temp:.1f}°{unit}")

            # Check thresholds
            current_time = time.time()
            time_since_alert = current_time - last_alert_time

            if time_since_alert >= ALERT_COOLDOWN:
                alert_message = None

                if not USE_CELSIUS:
                    low_threshold = LOW_TEMP_THRESHOLD
                    high_threshold = HIGH_TEMP_THRESHOLD
                else:
                    # Convert thresholds to Celsius for comparison
                    low_threshold = (LOW_TEMP_THRESHOLD - 32) * 5/9
                    high_threshold = (HIGH_TEMP_THRESHOLD - 32) * 5/9

                if temp < low_threshold:
                    alert_message = f"LOW TEMP ALERT: {temp:.1f}°{unit} (below {low_threshold:.0f}°{unit})"
                elif temp > high_threshold:
                    alert_message = f"HIGH TEMP ALERT: {temp:.1f}°{unit} (above {high_threshold:.0f}°{unit})"

                if alert_message:
                    print(f">>> SENDING ALERT: {alert_message}")
                    interface.sendText(alert_message)
                    last_alert_time = current_time


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

    unit = "C" if USE_CELSIUS else "F"
    print(f"Connected! Monitoring for temperature outside {LOW_TEMP_THRESHOLD}°{unit} - {HIGH_TEMP_THRESHOLD}°{unit}")
    print("Press Ctrl+C to stop\n")

    # Keep running
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
