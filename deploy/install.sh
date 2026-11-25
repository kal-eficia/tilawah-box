#!/usr/bin/env bash
# Set up Tilawah Box on Raspberry Pi OS (Lite is fine). Run from the repo folder: ./deploy/install.sh
set -euo pipefail
cd "$(dirname "$0")/.."
sudo apt-get update -q
sudo apt-get install -y -q mpv python3-venv python3-gpiozero python3-lgpio
python3 -m venv --system-site-packages .venv
.venv/bin/pip install -q -e .
if grep -q '"cards"' config.json 2>/dev/null; then .venv/bin/pip install -q mfrc522 spidev || true; fi
[ -f config.json ] || cp config.example.json config.json
echo "Downloading the short surahs and the daily ones for offline play (safe to stop and re-run)..."
.venv/bin/python -m tilawah --config config.json sync --surahs 1,18,36,67,78-114 --reciter alafasy || true
sudo sed "s#/home/pi#$HOME#g; s#User=pi#User=$USER#" deploy/tilawah.service | sudo tee /etc/systemd/system/tilawah.service >/dev/null
sudo systemctl daemon-reload
sudo systemctl enable --now tilawah
echo "Tilawah Box is running. Logs: journalctl -u tilawah -f"
