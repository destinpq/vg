#!/bin/bash
# Script to add the provided SSH key to authorized_keys

# Create .ssh directory if it doesn't exist
mkdir -p ~/.ssh

# Set proper permissions
chmod 700 ~/.ssh

# Add the key to authorized_keys
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIdtceRKruYG8LcPzTL//3PSGq1OSV4dYqF24tzZew6f" >> ~/.ssh/authorized_keys

# Set proper permissions for authorized_keys
chmod 600 ~/.ssh/authorized_keys

echo "SSH key added successfully!"
echo "You can now connect to this server using:"
echo "ssh root@$(hostname -I | awk '{print $1}')" 