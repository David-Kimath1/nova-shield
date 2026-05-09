#!/bin/bash
# Run NOVA-SHIELD immediately (without systemd)

cd /home/dave/nova-shield
source venv/bin/activate

# Create necessary directories
mkdir -p storage/intruders storage/logs storage/encrypted
sudo mkdir -p /tmp/nova-shield
sudo chmod 777 /tmp/nova-shield

# Run the daemon
sudo -E python3 app/main.py
