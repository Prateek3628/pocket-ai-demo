# AWS EC2 Deployment Guide for Pocket AI

## Prerequisites
- AWS account with EC2 access
- OpenAI API key
- Basic knowledge of SSH and Linux commands

## Step 1: Launch EC2 Instance

1. **Go to AWS EC2 Dashboard** and click "Launch Instance"

2. **Configure Instance:**
   - **Name:** pocket-ai-demo
   - **AMI:** Ubuntu Server 22.04 LTS (Free tier eligible)
   - **Instance Type:** t2.small or t2.medium (recommended)
   - **Key Pair:** Create new or use existing (download .pem file)
   - **Network Settings:**
     - Allow SSH (port 22) from your IP
     - Allow HTTP (port 80) from anywhere (0.0.0.0/0)
     - Allow Custom TCP (port 8501) from anywhere (0.0.0.0/0)

3. **Launch the instance** and note the **Public IP address**

## Step 2: Connect to EC2 Instance

```bash
# Make your key file secure
chmod 400 your-key.pem

# Connect to EC2
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

## Step 3: Upload Your Application

### Option A: Using SCP (Secure Copy)
From your local machine:

```bash
# Navigate to your project directory
cd /Users/mac/Documents/pocket-ai/pocket-ai-demo

# Copy files to EC2
scp -i your-key.pem -r * ubuntu@your-ec2-public-ip:/home/ubuntu/pocket-ai-demo/
```

### Option B: Using Git
On EC2 instance:

```bash
cd /home/ubuntu
git clone https://github.com/Prateek3628/pocket-ai-demo.git
cd pocket-ai-demo
```

## Step 4: Run Deployment Script

```bash
cd /home/ubuntu/pocket-ai-demo
chmod +x deploy.sh
./deploy.sh
```

## Step 5: Configure Environment Variables

```bash
# Edit the .env file and add your OpenAI API key
nano .env
```

Add:
```
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

Save and exit (Ctrl+X, then Y, then Enter)

## Step 6: Set Up Systemd Service

```bash
# Copy service file to systemd
sudo cp streamlit.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable streamlit

# Start the service
sudo systemctl start streamlit

# Check status
sudo systemctl status streamlit
```

## Step 7: Configure Nginx (Optional but Recommended)

```bash
# Copy nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/pocket-ai

# Edit the configuration
sudo nano /etc/nginx/sites-available/pocket-ai
# Replace 'your-domain.com' with your actual domain or EC2 public IP

# Enable the site
sudo ln -s /etc/nginx/sites-available/pocket-ai /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

## Step 8: Access Your Application

### Without Nginx:
```
http://your-ec2-public-ip:8501
```

### With Nginx:
```
http://your-ec2-public-ip
```

## Useful Commands

### Check Application Status
```bash
sudo systemctl status streamlit
```

### View Application Logs
```bash
sudo journalctl -u streamlit -f
```

### Restart Application
```bash
sudo systemctl restart streamlit
```

### Stop Application
```bash
sudo systemctl stop streamlit
```

### Update Application
```bash
cd /home/ubuntu/pocket-ai-demo
git pull  # If using git
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart streamlit
```

## Optional: Set Up HTTPS with Let's Encrypt

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get SSL certificate (requires domain name)
sudo certbot --nginx -d your-domain.com

# Auto-renewal is set up automatically
```

## Troubleshooting

### Application won't start
```bash
# Check logs
sudo journalctl -u streamlit -n 50

# Check if port is in use
sudo lsof -i :8501

# Manually test the app
cd /home/ubuntu/pocket-ai-demo
source venv/bin/activate
streamlit run app.py
```

### Can't access the application
1. Check EC2 Security Group allows inbound traffic on port 8501 (or 80 if using nginx)
2. Check if service is running: `sudo systemctl status streamlit`
3. Check nginx status: `sudo systemctl status nginx`

### Environment variables not loading
```bash
# Verify .env file exists and has correct content
cat /home/ubuntu/pocket-ai-demo/.env

# Make sure python-dotenv is installed
source venv/bin/activate
pip install python-dotenv
```

## Security Best Practices

1. **Use Environment Variables:** Never commit .env file to git
2. **Restrict SSH Access:** Only allow SSH from your IP in Security Group
3. **Enable HTTPS:** Use Let's Encrypt for free SSL certificates
4. **Regular Updates:** Keep system and packages updated
5. **Firewall:** Configure UFW firewall
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

## Cost Optimization

- Use t2.micro for testing (free tier eligible)
- Stop instance when not in use
- Set up auto-stop using AWS Lambda or CloudWatch
- Consider using Elastic IP to maintain same IP address

## Monitoring

### Set up CloudWatch
- Enable detailed monitoring in EC2
- Create alarms for CPU, memory usage
- Monitor application logs

### Application Health Check
Create a simple health check endpoint or monitor logs regularly.

---

## Quick Start Summary

```bash
# 1. Connect to EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# 2. Upload and setup
cd /home/ubuntu/pocket-ai-demo
./deploy.sh

# 3. Configure
nano .env  # Add OpenAI API key

# 4. Start service
sudo cp streamlit.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable streamlit
sudo systemctl start streamlit

# 5. Access
# Open browser: http://your-ec2-ip:8501
```

## Support

For issues, check:
- Application logs: `sudo journalctl -u streamlit -f`
- Nginx logs: `sudo tail -f /var/log/nginx/error.log`
- System logs: `sudo dmesg`
