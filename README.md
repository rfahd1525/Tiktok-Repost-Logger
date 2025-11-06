# TikTok Repost Logger

A Python-based application that monitors a TikTok user's reposts and logs new ones to a file.

## Features

- Monitors a TikTok user's reposts at configurable intervals (2-5 minutes recommended)
- Detects and logs new reposts with timestamps
- Browser automation with anti-detection measures
- Persistent state tracking to avoid duplicate logging
- Docker support for easy deployment
- Graceful shutdown handling
- Retry logic for reliability
- AWS-ready for 24/7 operation

## Requirements

- Python 3.9 or higher
- Docker and Docker Compose (optional, for containerized deployment)

## Installation

### Local Installation (macOS/Linux)

1. **Clone or download the repository**
   ```bash
   cd /path/to/TiktokRepostLogger
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers**
   ```bash
   playwright install chromium
   ```

5. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set your configuration:
   ```env
   TIKTOK_USERNAME=username_to_monitor
   CHECK_INTERVAL_MINUTES=3
   ```

6. **Run the application**
   ```bash
   python repost_logger.py
   ```

### Docker Installation

1. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your settings.

   **⚠️ IMPORTANT:** The `.env` file is required and must exist for Docker Compose to work.

2. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **View logs**
   ```bash
   docker-compose logs -f
   ```

4. **Stop the application**
   ```bash
   docker-compose down
   ```

## Configuration

All configuration is done via environment variables in the `.env` file:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TIKTOK_USERNAME` | Yes | - | TikTok username to monitor (without @) |
| `CHECK_INTERVAL_MINUTES` | No | 3 | How often to check for new reposts (minutes) |
| `LOG_FILE_PATH` | No | `reposts.log` | Path to the log file |
| `STATE_FILE_PATH` | No | `repost_state.json` | Path to state file |
| `TIKTOK_EMAIL` | No | - | TikTok account email (for login) |
| `TIKTOK_PASSWORD` | No | - | TikTok account password (for login) |
| `HEADLESS` | No | `true` | Run browser in headless mode |
| `BROWSER_TYPE` | No | `chromium` | Browser type (chromium/firefox/webkit) |
| `MAX_RETRIES` | No | 3 | Max retry attempts on failure |
| `RETRY_DELAY_SECONDS` | No | 5 | Delay between retries |

## Output

### Log File Format

New reposts are logged to `reposts.log` (or your configured path) in this format:

```
[2025-11-01 14:30:45] New repost detected: https://tiktok.com/@user/video/1234567890 (ID: 1234567890)
[2025-11-01 14:35:22] New repost detected: https://tiktok.com/@user/video/0987654321 (ID: 0987654321)
```

### State File

The application maintains a `repost_state.json` file to track:
- Previously seen repost IDs
- Last check timestamp
- Total reposts logged

This ensures duplicate reposts are not logged and allows the application to resume after restarts.

## AWS Deployment

### Option 1: EC2 Instance (Using deploy.sh Script)

The easiest way to deploy to EC2 is using the included deployment script:

1. **Configure your local `.env` file first**
   ```bash
   cp .env.example .env
   nano .env  # Set your production credentials
   ```

2. **Run the deployment script**
   ```bash
   ./deploy.sh ~/.ssh/your-key.pem your-ec2-ip-address
   ```

   The script will:
   - Copy all necessary files including `.env` to your EC2 instance
   - Set up Docker and Docker Compose
   - Configure the environment for headless mode
   - Create the project directory structure

3. **Start the application**
   ```bash
   ssh -i ~/.ssh/your-key.pem ubuntu@your-ec2-ip-address
   cd ~/TiktokRepostLogger
   docker-compose up -d
   ```

**⚠️ IMPORTANT:** Configure your local `.env` file with production credentials before running deploy.sh. The script will copy it to the server.

### Option 2: EC2 Instance (Manual)

1. **Launch an EC2 instance**
   - Amazon Linux 2 or Ubuntu
   - t2.micro or larger (t2.small recommended)
   - Configure security group (no inbound ports needed)

2. **Connect to your instance and install Docker**
   ```bash
   # For Amazon Linux 2
   sudo yum update -y
   sudo yum install -y docker
   sudo service docker start
   sudo usermod -a -G docker ec2-user

   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

3. **Upload your project**
   ```bash
   # From your local machine
   scp -r TiktokRepostLogger ec2-user@your-instance-ip:~/
   ```

4. **Configure and run**
   ```bash
   cd ~/TiktokRepostLogger
   cp .env.example .env
   nano .env  # Edit configuration with your credentials
   docker-compose up -d
   ```

5. **Set up auto-start on reboot**
   ```bash
   # Add to crontab
   crontab -e
   # Add this line:
   @reboot cd /home/ec2-user/TiktokRepostLogger && /usr/local/bin/docker-compose up -d
   ```

### Option 3: AWS ECS (Fargate)

1. **Build and push Docker image to ECR**
   ```bash
   # Create ECR repository
   aws ecr create-repository --repository-name tiktok-repost-logger

   # Login to ECR
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

   # Build and push
   docker build -t tiktok-repost-logger .
   docker tag tiktok-repost-logger:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/tiktok-repost-logger:latest
   docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/tiktok-repost-logger:latest
   ```

2. **Create ECS task definition**
   - Use Fargate launch type
   - 1 vCPU, 2 GB memory
   - Set environment variables (configure each variable manually in ECS, do NOT use .env file)
   - Mount EFS volume for persistent logs (optional)

3. **Create ECS service**
   - Desired count: 1
   - Launch type: Fargate
   - No load balancer needed

**⚠️ NOTE:** For ECS/Fargate, configure environment variables directly in the task definition, not via `.env` file.

## Accessing Logs on AWS

### Docker on EC2
```bash
# SSH into instance
ssh ec2-user@your-instance-ip

# View application logs
docker-compose logs -f

# View repost log file
cat data/reposts.log

# Download logs to local machine
scp ec2-user@your-instance-ip:~/TiktokRepostLogger/data/reposts.log ./
```

### ECS with CloudWatch
Logs are automatically sent to CloudWatch Logs. View them in the AWS Console or:
```bash
aws logs tail /ecs/tiktok-repost-logger --follow
```

## Troubleshooting

### Common Issues

**1. "Could not find Reposts tab"**
- The user may have no reposts
- TikTok's UI may have changed
- Login might be required (set `TIKTOK_EMAIL` and `TIKTOK_PASSWORD`)

**2. Rate limiting / IP blocking**
- Increase `CHECK_INTERVAL_MINUTES` to 5 or higher
- Consider using a proxy (requires code modification)
- Reduce `MAX_RETRIES` to avoid aggressive retrying

**3. Browser crashes in Docker**
- Increase shared memory: `shm_size: '2gb'` in docker-compose.yml
- Increase container memory limits

**4. Login fails**
- TikTok may require CAPTCHA solving
- Run in non-headless mode to solve CAPTCHA manually: `HEADLESS=false`
- Consider using cookies from a logged-in session (requires code modification)

### Debug Mode

Run in non-headless mode to see what's happening:
```bash
HEADLESS=false python repost_logger.py
```

## Legal Notice

This tool is for educational and personal use only. Web scraping may violate TikTok's Terms of Service. Use responsibly and at your own risk. I am not responsible for any misuse or consequences.

## Important Notes

- **Rate Limiting**: TikTok has aggressive anti-bot measures. Keep check intervals at 2-5 minutes minimum.
- **Detection Risk**: Despite anti-detection measures, prolonged use may result in IP bans or account restrictions.
- **Maintenance**: TikTok frequently updates their website. The selectors may need updates.
- **Login**: Some reposts may only be visible when logged in. Provide credentials if needed.

## Project Structure

```
TiktokRepostLogger/
├── config.py              # Configuration management
├── utils.py               # Utility functions (state, logging)
├── repost_logger.py       # Main application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker image definition
├── docker-compose.yml    # Docker Compose configuration
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## Support

For issues, questions, or contributions, please check the TikTok profile structure and update selectors as needed.

## License

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
