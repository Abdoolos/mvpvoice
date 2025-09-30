# 🚀 Docker Quick Start Guide - AI Callcenter Agent

**Designer: Abdullah Alawiss**

## 🎯 Quick Setup (< 5 minutes)

### **Prerequisites:**
- Docker Desktop installed
- Docker Compose available
- Git (for cloning)

### **1. Clone & Setup:**
```bash
git clone https://github.com/yourusername/ai-callcenter-agent.git
cd ai-callcenter-agent

# Make startup script executable (Linux/Mac)
chmod +x start.sh
```

### **2. One-Command Start:**
```bash
# Easy start with automated setup
./start.sh

# OR manual start
cp .env.example .env
docker-compose up -d
```

### **3. Access Services:**
- 🌐 **Frontend**: http://localhost:3000
- 🔧 **API**: http://localhost:8000/docs
- 🌸 **Monitoring**: http://localhost:5555

## 🐳 Docker Commands Reference

### **Basic Operations:**
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart backend
```

### **Development Mode:**
```bash
# Start with dev settings (hot reload)
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d

# View backend logs
docker-compose logs -f backend

# View celery worker logs
docker-compose logs -f celery-worker
```

### **Production Mode:**
```bash
# Start with Nginx reverse proxy
docker-compose --profile production up -d

# Access via http://localhost (port 80)
```

## 🔧 Troubleshooting

### **Common Issues:**

#### **Port Conflicts:**
```bash
# Check what's using ports
netstat -tulpn | grep :3000
netstat -tulpn | grep :8000

# Change ports in docker-compose.yml if needed
```

#### **Docker Build Issues:**
```bash
# Clean rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### **Database Issues:**
```bash
# Reset database
docker-compose down -v
docker-compose up -d

# View database logs
docker-compose logs postgres
```

#### **Permission Issues (Linux):**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod +x start.sh
```

## 📊 Health Checks

### **Service Status:**
```bash
# Check all containers
docker-compose ps

# Test backend health
curl http://localhost:8000/health

# Test frontend
curl http://localhost:3000

# Test database
docker-compose exec postgres pg_isready -U postgres
```

### **Performance Monitoring:**
```bash
# View resource usage
docker stats

# Monitor Celery tasks
# Open http://localhost:5555 in browser
```

## 🔄 Updates & Maintenance

### **Update Code:**
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

### **Clean Up:**
```bash
# Remove all containers and volumes
docker-compose down -v

# Remove unused images
docker image prune -a

# Reset everything
docker system prune -a --volumes
```

## ⚙️ Configuration

### **Environment Variables:**
Edit `.env` file for customization:
```bash
# Database
DATABASE_URL=postgresql://user:pass@postgres:5432/db

# API Keys (optional)
OPENAI_API_KEY=your_key_here
HUGGINGFACE_API_KEY=your_key_here

# App Settings
DEBUG=false
LOG_LEVEL=info
```

### **Port Configuration:**
Edit `docker-compose.yml` to change ports:
```yaml
services:
  frontend:
    ports:
      - "3001:3000"  # Change to port 3001
  backend:
    ports:
      - "8001:8000"  # Change to port 8001
```

## 🔐 Security (Production)

### **Basic Security:**
```bash
# Use strong passwords in .env
POSTGRES_PASSWORD=strong_random_password_here
SECRET_KEY=your_secret_key_here

# Enable HTTPS in nginx config
# Add SSL certificates
```

### **Firewall (if needed):**
```bash
# Allow only necessary ports
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw enable
```

## 📋 Testing

### **Quick Tests:**
```bash
# Test file upload
curl -X POST "http://localhost:8000/api/v1/upload/" \
  -F "file=@data/sample_calls/norwegian_telecom_call_sample.txt"

# Get all calls
curl http://localhost:8000/api/v1/calls/

# Test Norwegian compliance analysis
curl http://localhost:8000/api/v1/analysis/violations
```

## 🆘 Getting Help

### **Logs for Debugging:**
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres
docker-compose logs redis
docker-compose logs celery-worker
```

### **Contact:**
- **Issues**: Create GitHub issue
- **Email**: abdullah.alawiss@example.com
- **Documentation**: See `/docs` folder

---

### 🎉 Success!
If you see services running on the URLs above, your AI Callcenter Agent is ready for Norwegian telecom compliance analysis!

**Happy analyzing! 🇳🇴📞🤖**
