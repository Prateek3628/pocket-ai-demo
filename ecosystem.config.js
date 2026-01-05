module.exports = {
  apps: [{
    name: 'pocket-ai',
    script: 'streamlit',
    args: 'run app.py --server.port 5000 --server.address 0.0.0.0 --server.headless true',
    interpreter: '/home/ubuntu/pocket-ai-demo/venv/bin/python',
    cwd: '/home/ubuntu/pocket-ai-demo',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production',
      OPENAI_API_KEY: process.env.OPENAI_API_KEY
    },
    error_file: '/home/ubuntu/pocket-ai-demo/logs/pm2-error.log',
    out_file: '/home/ubuntu/pocket-ai-demo/logs/pm2-out.log',
    log_file: '/home/ubuntu/pocket-ai-demo/logs/pm2-combined.log',
    time: true
  }]
};
