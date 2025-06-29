#!/bin/bash
# Deployment script for AWS EC2

echo "🚀 Deploying GenAI CSV Enhancer to AWS EC2..."

# Update system
echo "📦 Updating system packages..."
sudo yum update -y

# Install Python 3 and pip
echo "🐍 Installing Python 3..."
sudo yum install -y python3 python3-pip git

# Install application dependencies
echo "📚 Installing Python dependencies..."
pip3 install -r requirements.txt

# Create systemd service for auto-start
echo "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/genai-csv-enhancer.service > /dev/null <<EOF
[Unit]
Description=GenAI CSV Enhancer Streamlit App
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/genai-csv-enhancer
ExecStart=/usr/local/bin/streamlit run main.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable genai-csv-enhancer
sudo systemctl start genai-csv-enhancer

echo "✅ Deployment complete!"
echo "🌐 Application should be accessible at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8501"
echo "📊 Check service status: sudo systemctl status genai-csv-enhancer"
echo "📝 View logs: sudo journalctl -u genai-csv-enhancer -f"
