#!/bin/bash

# Simple Audio Service Installation Script

echo "🚀 Installing Simple Audio Service as systemd service..."

# Stop any existing service
sudo systemctl stop simple-audio-service 2>/dev/null || true

# Copy service file
sudo cp simple-audio-service.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable simple-audio-service

# Start service
sudo systemctl start simple-audio-service

# Check status
echo "📊 Service Status:"
sudo systemctl status simple-audio-service --no-pager

echo ""
echo "✅ Installation complete!"
echo ""
echo "📋 Useful commands:"
echo "  Start:   sudo systemctl start simple-audio-service"
echo "  Stop:    sudo systemctl stop simple-audio-service"
echo "  Restart: sudo systemctl restart simple-audio-service"
echo "  Status:  sudo systemctl status simple-audio-service"
echo "  Logs:    sudo journalctl -u simple-audio-service -f"
echo ""
echo "🌐 Service will be available at: http://localhost:8000"
