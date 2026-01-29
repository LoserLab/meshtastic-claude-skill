# Meshtastic Script Generator for Claude Code

Generate ready-to-run Python scripts for your Meshtastic devices - no coding experience required.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

**Author:** [Heathen](https://x.com/heathenft)

**Built in [Mirra](https://getmirra.app)**

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/LoserLab/meshtastic-claude-skill.git
   ```

2. Copy the skill to your Claude Code skills folder:
   ```bash
   # For project-specific installation:
   mkdir -p /path/to/your/project/.claude/skills
   cp -r meshtastic-claude-skill /path/to/your/project/.claude/skills/meshtastic

   # Or for global installation:
   mkdir -p ~/.claude/skills
   cp -r meshtastic-claude-skill ~/.claude/skills/meshtastic
   ```

3. Restart Claude Code or open a new session

4. Use the skill by typing `/meshtastic` followed by what you want to create

## What Is This?

This is a Claude Code skill that helps you create automation scripts for your Meshtastic mesh network. Simply describe what you want in plain English, and Claude will generate complete, working code you can run on a Raspberry Pi, laptop, or any computer.

**You only need internet once** - to generate the script. After that, the script runs completely offline on your device, communicating over your mesh network.

## Compatibility

| Component | Version |
|-----------|---------|
| Python | 3.8+ |
| meshtastic (Python library) | 2.0+ |
| Meshtastic firmware | 2.x |

Install the correct version:
```bash
pip install "meshtastic>=2.0"
```

## Quick Start

1. Open Claude Code in this directory
2. Type: `/meshtastic` followed by what you want
3. Answer any clarifying questions
4. Copy the generated script to your device
5. Run it - done!

### Example

```
/meshtastic I want to get an alert when my cabin temperature drops below 40 degrees
```

Claude will generate a complete Python script that:
- Connects to your Meshtastic device
- Monitors temperature readings from the mesh
- Sends an alert message when it gets too cold
- Includes all setup instructions

## What Can It Do?

| Use Case | Description |
|----------|-------------|
| **Temperature alerts** | Get notified when temp goes above/below thresholds |
| **Message logging** | Save all mesh messages to a file |
| **Auto-responder** | Automatically reply to specific keywords |
| **Position tracking** | Log GPS coordinates from all nodes |
| **Scheduled messages** | Send check-ins at regular intervals |
| **Battery monitoring** | Alert when any node's battery is low |
| **Custom automation** | Describe any automation you need |

## Ready-to-Use Scripts

Don't want to generate a custom script? Grab one of these from the `examples/` folder:

| Script | What It Does |
|--------|--------------|
| `message_logger.py` | Saves all messages to `meshtastic_messages.log` |
| `temperature_alert.py` | Alerts when temp crosses your thresholds |
| `auto_responder.py` | Replies to "status", "help", "ping" keywords |
| `position_tracker.py` | Logs all GPS positions to `positions.csv` |
| `scheduled_broadcaster.py` | Sends a message every hour (configurable) |
| `battery_monitor.py` | Alerts when any node battery is low |

### Using an Example Script

1. Copy the script to your device (Raspberry Pi, laptop, etc.)
2. Install Python 3 if not already installed
3. Install the Meshtastic library:
   ```bash
   pip install meshtastic
   ```
4. Connect your Meshtastic device via USB
5. Run:
   ```bash
   python3 script_name.py
   ```

## Requirements

### Hardware
- A Meshtastic-compatible device (T-Beam, T-Echo, Heltec, RAK, etc.)
- USB cable (must support data, not just charging)
- A computer to run the script (Raspberry Pi recommended for always-on)

### Software
- Python 3
- Meshtastic library (`pip install meshtastic`)

## Common Questions

### Do I need to know Python?
No! The scripts are complete and ready to run. Just copy, paste, and go.

### Does the script need internet to work?
No. You only need internet once to generate the script with Claude. After that, it runs completely offline using your mesh network.

### What devices can run the scripts?
- Raspberry Pi (recommended for always-on)
- Windows, Mac, or Linux laptop/desktop
- Any computer with Python 3

### How do I make it run automatically on startup?
See the "Running on Boot" section below.

### My device isn't being detected
1. Check your USB cable supports data (not charge-only)
2. Try a different USB port
3. On Linux, you may need to add yourself to the dialout group:
   ```bash
   sudo usermod -a -G dialout $USER
   ```
   Then log out and back in.

### How do I know which port my device is on?
**Linux/Mac:**
```bash
ls /dev/tty* | grep -E "(USB|ACM)"
```

**Windows:**
Check Device Manager → Ports (COM & LPT)

## Running on Boot (Raspberry Pi)

To make your script start automatically when the Pi boots:

1. Save your script to `/home/pi/meshtastic_script.py`

2. Create a service file:
   ```bash
   sudo nano /etc/systemd/system/meshtastic.service
   ```

3. Paste this content:
   ```ini
   [Unit]
   Description=Meshtastic Script
   After=network.target

   [Service]
   ExecStart=/usr/bin/python3 /home/pi/meshtastic_script.py
   WorkingDirectory=/home/pi
   Restart=always
   User=pi

   [Install]
   WantedBy=multi-user.target
   ```

4. Save and exit (Ctrl+X, then Y, then Enter)

5. Enable and start:
   ```bash
   sudo systemctl enable meshtastic
   sudo systemctl start meshtastic
   ```

6. Check it's running:
   ```bash
   sudo systemctl status meshtastic
   ```

## Testing Your Setup

Before deploying, verify everything works:

1. **Check device is detected:**
   ```bash
   meshtastic --info
   ```
   Should show your device info.

2. **Check you can see other nodes:**
   ```bash
   meshtastic --nodes
   ```
   Should list other devices on your mesh.

3. **Test sending a message:**
   ```bash
   meshtastic --sendtext "Test message"
   ```
   Should appear on other devices.

## Hardware Quick Reference

### Devices WITH GPS
- LILYGO T-Beam
- LILYGO T-Echo
- Seeed SenseCAP T1000-E
- B&Q Nano G2 Ultra

### Devices WITHOUT GPS
- Heltec LoRa 32
- LILYGO T3-S3
- RAK WisBlock (GPS is optional add-on)

### Best for Battery Life
- T-Echo
- SenseCAP T1000-E
- RAK with nRF52 core

### WiFi Capable
- T-Beam
- T3-S3
- Heltec v3

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Could not find device" | Check USB cable, try different port |
| "Permission denied" (Linux) | Run: `sudo usermod -a -G dialout $USER` then log out/in |
| "No module named meshtastic" | Run: `pip install meshtastic` |
| Script runs but no messages | Check other nodes are in range, channels match |
| No telemetry data | Your device may not have sensors - check hardware specs |

## Getting Help

- **Meshtastic Discord**: https://discord.gg/meshtastic
- **Meshtastic Docs**: https://meshtastic.org/docs/
- **GitHub Issues**: https://github.com/meshtastic/Meshtastic-python

## Files in This Skill

```
meshtastic/
├── README.md          # This file
├── SKILL.md           # Main skill instructions for Claude
├── reference.md       # Technical reference (troubleshooting, hardware, APIs)
├── LICENSE            # MIT License
└── examples/
    ├── message_logger.py
    ├── temperature_alert.py
    ├── auto_responder.py
    ├── position_tracker.py
    ├── scheduled_broadcaster.py
    └── battery_monitor.py
```

## Contributing

Contributions welcome! Ideas for improvement:
- Additional example scripts
- Support for more use cases
- Bug fixes and improvements
- Documentation updates

## Acknowledgments

- [Meshtastic Project](https://meshtastic.org/) - The open-source mesh networking platform
- [Meshtastic Python Library](https://github.com/meshtastic/Meshtastic-python) - The Python API this skill generates code for
- Built with [Claude Code](https://claude.ai/code)

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

---

**Remember:** You only need internet to generate the script. Once you have it, your Meshtastic mesh runs completely off-grid!
