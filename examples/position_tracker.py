#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meshtastic Position Tracker

What this does: Logs GPS positions from all nodes on your mesh to a CSV
file. Useful for tracking movement, creating maps, or reviewing routes.

Requirements:
- Python 3.8+
- meshtastic library 2.0+

Setup:
1. Install Python 3 if not already installed
2. Run: pip install "meshtastic>=2.0"
3. Connect your Meshtastic device via USB
4. Run: python3 position_tracker.py

Positions are saved to: positions.csv
You can open this file in Excel, Google Sheets, or mapping software.
"""

import meshtastic
import meshtastic.serial_interface
from pubsub import pub
from datetime import datetime
import signal
import sys
import os

# --- Configuration ---
CSV_FILE = "positions.csv"
# --------------------

interface = None


def get_node_name(interface, node_id):
    """Get the friendly name of a node, or return the ID if unknown."""
    if interface.nodes:
        node = interface.nodes.get(node_id)
        if node and 'user' in node:
            return node['user'].get('longName', node_id)
    return node_id


def ensure_csv_header():
    """Create CSV file with header if it doesn't exist."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', encoding='utf-8') as f:
            f.write("timestamp,node_id,node_name,latitude,longitude,altitude,speed,heading\n")


def on_receive(packet, interface):
    """Handle incoming packets and log position data."""
    if 'decoded' not in packet:
        return

    portnum = packet['decoded'].get('portnum')

    if portnum == 'POSITION_APP':
        position = packet['decoded'].get('position', {})

        # Extract position data
        lat = position.get('latitude') or position.get('latitudeI')
        lon = position.get('longitude') or position.get('longitudeI')

        # Skip if no valid position
        if lat is None or lon is None:
            return

        # Convert from integer format if needed (latitudeI is lat * 1e7)
        if isinstance(lat, int) and abs(lat) > 180:
            lat = lat / 1e7
        if isinstance(lon, int) and abs(lon) > 180:
            lon = lon / 1e7

        # Get other data
        altitude = position.get('altitude', '')
        speed = position.get('groundSpeed', '')  # m/s
        heading = position.get('groundTrack', '')  # degrees

        # Node info
        sender_id = packet.get('fromId', 'unknown')
        sender_name = get_node_name(interface, sender_id)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Print to console
        print(f"[{timestamp}] {sender_name}: {lat:.6f}, {lon:.6f}", end="")
        if altitude:
            print(f" alt:{altitude}m", end="")
        if speed:
            print(f" speed:{speed}m/s", end="")
        print()

        # Save to CSV
        with open(CSV_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{timestamp},{sender_id},{sender_name},{lat},{lon},{altitude},{speed},{heading}\n")


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

    # Ensure CSV has header
    ensure_csv_header()

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

    print(f"Connected! Logging positions to {CSV_FILE}")
    print("Press Ctrl+C to stop\n")

    # Keep running
    while True:
        import time
        time.sleep(1)


if __name__ == "__main__":
    main()
