#!/bin/bash
# Build script for NOVA-SHIELD PAM module

echo "[BUILD] Compiling PAM module..."

# Compile the PAM module
gcc -fPIC -fno-stack-protector -c pam_nova.c

# Link shared library
gcc -shared -Wl,-soname, pam_nova.so -o pam_nova.so pam_nova.o -lpam

# Install to PAM directory
if [ -d "/lib/x86_64-linux-gnu/security/" ]; then
    sudo cp pam_nova.so /lib/x86_64-linux-gnu/security/
elif [ -d "/lib/security/" ]; then
    sudo cp pam_nova.so /lib/security/
else
    echo "[WARN] Could not find PAM directory"
fi

echo "[OK] PAM module built and installed"