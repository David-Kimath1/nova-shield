#!/bin/bash
# Install NOVA-SHIELD as login authentication

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

# Enable systemd service
sudo systemctl enable nova-shield.service
sudo systemctl start nova-shield.service

echo "[OK] NOVA-SHIELD login integration installed"
echo "[INFO] Please reboot to test face authentication"