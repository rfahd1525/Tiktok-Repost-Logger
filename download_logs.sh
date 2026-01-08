#!/bin/bash
# Download logs from EC2 instance
# Usage: ./download_logs.sh <ssh-key-path> <ec2-ip>

set -e

# Check arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: ./download_logs.sh <ssh-key-path> <ec2-ip>"
    echo "Example: ./download_logs.sh ~/Downloads/my-key.pem 54.123.45.67"
    exit 1
fi

SSH_KEY="$1"
EC2_IP="$2"
EC2_USER="ubuntu"

echo "Downloading logs from EC2..."

# Create local logs directory
mkdir -p ec2_logs

# Download repost log
echo "Downloading reposts.log..."
scp -i "$SSH_KEY" -o StrictHostKeyChecking=no "${EC2_USER}@${EC2_IP}:~/TiktokRepostLogger/data/reposts.log" ec2_logs/ 2>/dev/null || echo "No repost log found yet"

# Download state file
echo "Downloading state file..."
scp -i "$SSH_KEY" -o StrictHostKeyChecking=no "${EC2_USER}@${EC2_IP}:~/TiktokRepostLogger/data/repost_state.json" ec2_logs/ 2>/dev/null || echo "No state file found yet"

echo ""
echo "Logs downloaded to ./ec2_logs/"
echo ""
echo "View reposts:"
echo "  cat ec2_logs/reposts.log"
echo ""
echo "View state:"
echo "  cat ec2_logs/repost_state.json"
