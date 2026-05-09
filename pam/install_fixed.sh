#!/bin/bash
# Install NOVA-SHIELD PAM integration

echo "[INSTALL] Installing NOVA-SHIELD PAM integration..."

# Backup existing PAM configuration
if [ -f "/etc/pam.d/common-auth" ]; then
    sudo cp /etc/pam.d/common-auth /etc/pam.d/common-auth.backup
    echo "[BACKUP] Created backup of common-auth"
fi

# Check if NOVA-SHIELD is already configured
if ! grep -q "pam_nova.so" /etc/pam.d/common-auth; then
    # Insert NOVA-SHIELD at the beginning of auth chain
    sudo sed -i '1i auth sufficient pam_nova.so' /etc/pam.d/common-auth
    echo "[PAM] Added NOVA-SHIELD to auth chain"
fi

# Create socket directory for IPC
sudo mkdir -p /run/nova-shield
sudo chmod 755 /run/nova-shield

# Check if service exists before enabling
if [ -f "/etc/systemd/system/nova-shield.service" ]; then
    sudo systemctl daemon-reload
    sudo systemctl enable nova-shield.service
    sudo systemctl start nova-shield.service
    echo "[SERVICE] NOVA-SHIELD service started"
else
    echo "[WARN] Service file not found. Run: sudo cp ~/nova-shield/systemd/nova-shield.service /etc/systemd/system/"
fi

echo "[OK] NOVA-SHIELD login integration installed"
echo "[INFO] Please reboot to test face authentication"
