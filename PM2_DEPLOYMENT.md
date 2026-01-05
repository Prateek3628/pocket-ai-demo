# Deploy Pocket AI with PM2 on AWS EC2

## Why PM2?
- Easy process management
- Auto-restart on crashes
- Log management
- Memory monitoring
- Simple commands

## Prerequisites
- AWS EC2 instance (Ubuntu 22.04 LTS)
- Node.js and npm installed
- Your application files on EC2

## Step 1: Connect to EC2

```bash
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

## Step 2: Install Node.js and PM2

```bash
# Install Node.js (if not already installed)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version
npm --version

# Install PM2 globally
sudo npm install -g pm2
```

## Step 3: Set Up Application

```bash
# Navigate to app directory
cd /home/ubuntu/pocket-ai-demo

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create logs directory
mkdir -p logs

# Create .env file
nano .env
```

Add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

## Step 4: Start with PM2

### Option A: Using ecosystem.config.js (Recommended)

```bash
# Start the application
pm2 start ecosystem.config.js

# Save PM2 process list
pm2 save

# Set PM2 to start on system boot
pm2 startup
# Copy and run the command that PM2 outputs
```

### Option B: Direct Command

```bash
pm2 start "venv/bin/streamlit run app.py --server.port 5000 --server.address 0.0.0.0 --server.headless true" --name pocket-ai --interpreter venv/bin/python
pm2 save
pm2 startup
```

## Step 5: Configure Nginx (Optional)

```bash
# Install nginx
sudo apt-get install -y nginx

# Copy nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/pocket-ai

# Edit if needed
sudo nano /etc/nginx/sites-available/pocket-ai

# Enable the site
sudo ln -s /etc/nginx/sites-available/pocket-ai /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test and restart nginx
sudo nginx -t
sudo systemctl restart nginx
```

## PM2 Commands

### View Running Apps
```bash
pm2 list
pm2 status
```

### View Logs
```bash
# All logs
pm2 logs

# Specific app logs
pm2 logs pocket-ai

# Real-time logs
pm2 logs pocket-ai --lines 100
```

### Monitor
```bash
pm2 monit
```

### Restart Application
```bash
pm2 restart pocket-ai
```

### Stop Application
```bash
pm2 stop pocket-ai
```

### Delete Application
```bash
pm2 delete pocket-ai
```

### Reload (Zero Downtime)
```bash
pm2 reload pocket-ai
```

### View Details
```bash
pm2 show pocket-ai
```

### Update Application
```bash
cd /home/ubuntu/pocket-ai-demo
git pull  # or upload new files
source venv/bin/activate
pip install -r requirements.txt
pm2 restart pocket-ai
```

## Environment Variables with PM2

### Option 1: Using .env file
PM2 will automatically load `.env` file if you have python-dotenv installed.

### Option 2: Set via PM2
```bash
pm2 set pocket-ai:OPENAI_API_KEY "your-api-key"
pm2 restart pocket-ai
```

### Option 3: Use ecosystem.config.js
Edit `ecosystem.config.js` and add environment variables in the `env` section.

## Auto-start on Reboot

After starting your app with PM2:

```bash
# Save current process list
pm2 save

# Generate startup script
pm2 startup

# PM2 will output a command like:
# sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u ubuntu --hp /home/ubuntu

# Copy and run that command
```

## Monitoring & Logs

### View Resource Usage
```bash
pm2 monit
```

### Clear Logs
```bash
pm2 flush
```

### Rotate Logs (to prevent large log files)
```bash
pm2 install pm2-logrotate
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 7
```

## Troubleshooting

### App Not Starting
```bash
# Check logs
pm2 logs pocket-ai --err

# Check if port is available
sudo lsof -i :5000

# Manually test
source venv/bin/activate
streamlit run app.py --server.port 5000 --server.address 0.0.0.0
```

### PM2 Not Found After Reboot
```bash
# Reinstall startup script
pm2 startup
pm2 save
```

### High Memory Usage
```bash
# Check memory
pm2 monit

# Restart app
pm2 restart pocket-ai
```

### Update PM2
```bash
sudo npm install -g pm2@latest
pm2 update
```

## Security Best Practices

1. **Firewall Rules:**
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 5000/tcp
sudo ufw enable
```

2. **Keep System Updated:**
```bash
sudo apt-get update && sudo apt-get upgrade -y
```

3. **Secure .env File:**
```bash
chmod 600 .env
```

4. **Use HTTPS:** Configure Let's Encrypt with nginx

## Quick Reference

```bash
# Start
pm2 start ecosystem.config.js

# Monitor
pm2 monit

# Logs
pm2 logs pocket-ai

# Restart
pm2 restart pocket-ai

# Stop
pm2 stop pocket-ai

# Status
pm2 status

# Save configuration
pm2 save
```

## Access Your Application

- **With Nginx:** http://your-ec2-ip
- **Without Nginx:** http://your-ec2-ip:5000

## Advantages of PM2 over Systemd

✅ Easier log management
✅ Built-in monitoring dashboard
✅ Simple commands
✅ Works across platforms
✅ Great for Node.js developers
✅ Easy process management

---

**Need help?** Check logs with `pm2 logs pocket-ai`
