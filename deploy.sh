#!/bin/bash
# MOL Playground — Azure VM Deploy Script
# Deploys MOL playground to the VM directly with Python + systemd

set -e

echo "=== MOL Playground Deployment ==="

# Install dependencies
echo "[1/4] Installing dependencies..."
pip3 install --user --break-system-packages lark fastapi uvicorn 2>/dev/null || \
pip3 install --user lark fastapi uvicorn

# Create app directory
echo "[2/4] Setting up application..."
sudo mkdir -p /opt/mol-playground
sudo cp -r ~/mol-deploy/* /opt/mol-playground/
sudo chown -R azureuser:azureuser /opt/mol-playground

# Create systemd service
echo "[3/4] Creating systemd service..."
sudo tee /etc/systemd/system/mol-playground.service > /dev/null << 'SVCEOF'
[Unit]
Description=MOL Playground — Online Compiler
After=network.target

[Service]
Type=simple
User=azureuser
WorkingDirectory=/opt/mol-playground
Environment=PATH=/home/azureuser/.local/bin:/usr/bin:/bin
ExecStart=/home/azureuser/.local/bin/uvicorn playground.server:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SVCEOF

# Start the service
echo "[4/4] Starting MOL Playground..."
sudo systemctl daemon-reload
sudo systemctl enable mol-playground
sudo systemctl restart mol-playground
sleep 2
sudo systemctl status mol-playground --no-pager

echo ""
echo "=== MOL Playground deployed! ==="
echo "  URL: http://$(curl -s ifconfig.me):8000"
echo ""
