#!/bin/bash
# Deployment script for TikTok Repost Logger to AWS EC2
# Usage: ./deploy.sh <ssh-key-path> <ec2-ip>

set -e

# Check arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: ./deploy.sh <ssh-key-path> <ec2-ip>"
    echo "Example: ./deploy.sh ~/Downloads/my-key.pem 54.123.45.67"
    exit 1
fi

SSH_KEY="$1"
EC2_IP="$2"
EC2_USER="ubuntu"

echo "========================================="
echo "TikTok Repost Logger - AWS Deployment"
echo "========================================="
echo "EC2 IP: $EC2_IP"
echo "SSH Key: $SSH_KEY"
echo ""

# Check if SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    echo "Error: SSH key not found at $SSH_KEY"
    exit 1
fi

# Set correct permissions on SSH key
chmod 400 "$SSH_KEY"

echo "Step 1: Creating deployment package..."
# Create temporary directory
TEMP_DIR=$(mktemp -d)
cp config.py utils.py notifications.py repost_logger.py requirements.txt Dockerfile docker-compose.yml .env .dockerignore "$TEMP_DIR/"

echo "Step 2: Uploading files to EC2..."
scp -i "$SSH_KEY" -o StrictHostKeyChecking=no -r "$TEMP_DIR"/* "${EC2_USER}@${EC2_IP}:~/"

echo "Step 3: Creating EC2 setup script..."
cat > "$TEMP_DIR/ec2_setup.sh" << 'EOF'
#!/bin/bash
set -e

echo "========================================="
echo "Setting up TikTok Repost Logger on EC2"
echo "========================================="

# Update system
echo "Updating system packages..."
sudo apt-get update -qq

# Install Docker
echo "Installing Docker..."
sudo apt-get install -y docker.io docker-compose 2>&1 | grep -v "^Get:" || true

# Start Docker
echo "Starting Docker service..."
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
echo "Adding user to docker group..."
sudo usermod -aG docker ubuntu

# Create project directory
echo "Creating project directory..."
mkdir -p ~/TiktokRepostLogger
mv ~/config.py ~/utils.py ~/notifications.py ~/repost_logger.py ~/requirements.txt ~/Dockerfile ~/docker-compose.yml ~/.env ~/.dockerignore ~/TiktokRepostLogger/ 2>/dev/null || true

cd ~/TiktokRepostLogger

# Create data directory
mkdir -p data

# Make sure .env has HEADLESS=true
echo "Configuring for headless mode..."
sed -i 's/HEADLESS=false/HEADLESS=true/g' .env

echo ""
echo "========================================="
echo "Setup complete!"
echo "========================================="
echo ""
echo "To start the application:"
echo "  cd ~/TiktokRepostLogger"
echo "  docker-compose up -d"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "Note: You may need to log out and back in for docker permissions to take effect."
echo "After logging back in, run: cd ~/TiktokRepostLogger && docker-compose up -d"
EOF

chmod +x "$TEMP_DIR/ec2_setup.sh"

echo "Step 4: Uploading and running setup script..."
scp -i "$SSH_KEY" -o StrictHostKeyChecking=no "$TEMP_DIR/ec2_setup.sh" "${EC2_USER}@${EC2_IP}:~/"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "${EC2_USER}@${EC2_IP}" 'bash ~/ec2_setup.sh'

# Clean up
rm -rf "$TEMP_DIR"

echo ""
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "Your .env file has been deployed and configured for headless mode."
echo ""
echo "Next steps:"
echo "1. SSH into your instance:"
echo "   ssh -i $SSH_KEY ${EC2_USER}@${EC2_IP}"
echo ""
echo "2. Start the application:"
echo "   cd ~/TiktokRepostLogger"
echo "   docker-compose up -d"
echo ""
echo "3. View logs:"
echo "   docker-compose logs -f"
echo ""
echo "4. View reposts:"
echo "   tail -f data/reposts.log"
echo ""
echo "Note: If docker commands fail, log out and back in, then try again."
