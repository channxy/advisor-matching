# 🐳 Docker Deployment Guide

This guide shows you how to deploy AdvisorConnect GenAI v2 using Docker for true plug-and-play functionality.

## 🚀 Quick Start with Docker

### Prerequisites
- **Docker Desktop** installed (includes Docker Compose)
- **Git** for cloning the repository

### One-Command Deployment
```bash
# Clone and run with Docker
git clone <repository-url> && cd advisor-matching && ./docker-start.sh

# Or if already cloned, just run:
./docker-start.sh
```

### Manual Docker Commands
```bash
# Build and start all services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart
```

## 📁 Docker Files Structure

```
advisor-matching/
├── Dockerfile.backend          # FastAPI backend container
├── Dockerfile.frontend         # React frontend container
├── docker-compose.yml          # Development environment
├── docker-compose.prod.yml     # Production environment
├── docker-start.sh             # Docker startup script
├── nginx.conf                  # Nginx reverse proxy config
└── .dockerignore               # Files to exclude from builds
```

## 🔧 Docker Services

### Backend Service (`advisorconnect-backend`)
- **Image**: Python 3.11-slim
- **Port**: 8000
- **Features**:
  - FastAPI application
  - ML model training and inference
  - Excel data processing
  - SQLite database
  - Health checks

### Frontend Service (`advisorconnect-frontend`)
- **Image**: Node.js 18-alpine
- **Port**: 3000
- **Features**:
  - React application
  - Built and served with `serve`
  - Health checks
  - Production-optimized

### Nginx Service (Production)
- **Image**: nginx:alpine
- **Ports**: 80, 443
- **Features**:
  - Reverse proxy
  - Load balancing
  - SSL termination (when configured)

## 🌍 Environment Variables

### Required
- `OPENAI_API_KEY` (optional): For enhanced AI features

### Backend Environment
```bash
OPENAI_API_KEY=your-api-key-here
PYTHONPATH=/app
ENVIRONMENT=production  # for production
```

### Frontend Environment
```bash
REACT_APP_API_URL=http://localhost:8000
NODE_ENV=production  # for production
```

## 📊 Volumes and Data Persistence

### Backend Volumes
- `./backend/models:/app/models` - ML model persistence
- `./backend/transactions.xlsx:/app/transactions.xlsx` - Sample data
- `models-data:/app/models` - Production model storage

### Database
- SQLite database is stored in the backend container
- For production, consider using PostgreSQL with external volume

## 🚀 Production Deployment

### Using Production Compose File
```bash
# Start production environment
docker-compose -f docker-compose.prod.yml up --build -d

# View production logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Production Features
- **Resource Limits**: CPU and memory constraints
- **Health Checks**: Automatic service monitoring
- **Restart Policies**: Always restart on failure
- **Nginx Proxy**: Load balancing and SSL support
- **Volume Persistence**: Data survives container restarts

### SSL Configuration
1. Create SSL certificates in `./ssl/` directory
2. Update `nginx.conf` for HTTPS
3. Use `docker-compose.prod.yml`

## 🔍 Monitoring and Logs

### View Service Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Production logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Health Checks
```bash
# Check service health
docker-compose ps

# Manual health check
curl http://localhost:8000/
curl http://localhost:3000/
```

### Resource Usage
```bash
# View container resource usage
docker stats

# View disk usage
docker system df
```

## 🛠️ Development with Docker

### Development Workflow
```bash
# Start development environment
docker-compose up -d

# View logs in real-time
docker-compose logs -f

# Rebuild after code changes
docker-compose up --build -d

# Access container shell
docker-compose exec backend bash
docker-compose exec frontend sh
```

### Code Changes
- Backend changes: Rebuild with `docker-compose up --build -d`
- Frontend changes: Rebuild with `docker-compose up --build -d`
- Database changes: May require volume cleanup

## 🔧 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Check what's using the ports
lsof -i :8000
lsof -i :3000

# Stop conflicting services
docker-compose down
```

#### Build Failures
```bash
# Clean build cache
docker-compose build --no-cache

# Remove all containers and images
docker-compose down --rmi all --volumes --remove-orphans
```

#### Permission Issues
```bash
# Fix volume permissions
sudo chown -R $USER:$USER ./backend/models
```

#### Memory Issues
```bash
# Increase Docker memory limit in Docker Desktop
# Or use production compose file with resource limits
```

### Debug Commands
```bash
# Check container status
docker-compose ps

# View container details
docker-compose exec backend python -c "import app; print('Backend OK')"

# Check network connectivity
docker-compose exec backend curl -f http://localhost:8000/

# View container logs
docker-compose logs backend
```

## 📈 Scaling

### Horizontal Scaling
```bash
# Scale backend services
docker-compose up --scale backend=3 -d

# Scale with production config
docker-compose -f docker-compose.prod.yml up --scale backend=3 -d
```

### Load Balancing
- Nginx automatically load balances between multiple backend instances
- Frontend can be scaled behind a load balancer

## 🔒 Security Considerations

### Production Security
1. **Use HTTPS**: Configure SSL certificates
2. **Environment Variables**: Store secrets in `.env` files
3. **Network Security**: Use Docker networks for service isolation
4. **Resource Limits**: Prevent resource exhaustion attacks
5. **Regular Updates**: Keep base images updated

### Security Best Practices
```bash
# Use non-root users in containers
# Limit container capabilities
# Scan images for vulnerabilities
docker scan advisorconnect-backend
docker scan advisorconnect-frontend
```

## 📝 Docker Commands Reference

### Basic Commands
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f

# Build images
docker-compose build

# Pull latest images
docker-compose pull
```

### Advanced Commands
```bash
# Scale services
docker-compose up --scale backend=2 -d

# Execute commands in containers
docker-compose exec backend python manage.py migrate
docker-compose exec frontend npm install

# Copy files from/to containers
docker cp advisorconnect-backend:/app/models ./local-models
```

## 🎯 Performance Optimization

### Container Optimization
- Use multi-stage builds for smaller images
- Optimize layer caching
- Use `.dockerignore` to exclude unnecessary files
- Use Alpine Linux base images where possible

### Resource Optimization
```bash
# Monitor resource usage
docker stats

# Set resource limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 1G
      cpus: '0.5'
```

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] Docker and Docker Compose installed
- [ ] Repository cloned
- [ ] Environment variables set (optional)
- [ ] Ports 8000 and 3000 available

### Deployment
- [ ] Run `./docker-start.sh`
- [ ] Verify services are healthy
- [ ] Test application functionality
- [ ] Check logs for errors

### Post-Deployment
- [ ] Monitor resource usage
- [ ] Set up log rotation
- [ ] Configure backups
- [ ] Set up monitoring

## 📞 Support

For Docker-related issues:
1. Check the troubleshooting section
2. View container logs: `docker-compose logs -f`
3. Verify Docker installation: `docker --version`
4. Check system resources: `docker system df`

The Docker setup provides a complete, isolated environment for running AdvisorConnect GenAI v2 with minimal configuration required!
