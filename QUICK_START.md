# 🚀 QUICK START GUIDE - Docker Deployment

## ⚡ Super Quick Start

```powershell
# Start everything
docker-compose up -d

# View logs
docker-compose logs -f

# Stop everything
docker-compose down
```

## 🌐 Access URLs

| Service | URL | Login |
|---------|-----|-------|
| **Dashboard** | http://localhost:8000 | - |
| **Classify Text** | http://localhost:8000/classify | - |
| **Grafana** | http://localhost:3000 | admin/admin |
| **Prometheus** | http://localhost:9090 | - |

## 📊 Database Access

```powershell
# Quick stats
docker exec postgres psql -U admin -d bigdata_project -c "SELECT sentiment_classname, COUNT(*) FROM tweets GROUP BY sentiment_classname;"

# Connect to database
docker exec -it postgres psql -U admin -d bigdata_project

# View latest tweets
docker exec postgres psql -U admin -d bigdata_project -c "SELECT id, LEFT(tweet, 50), sentiment_classname FROM tweets ORDER BY id DESC LIMIT 10;"
```

## 🔍 Monitoring

```powershell
# View all logs
docker-compose logs -f

# Specific service logs
docker-compose logs -f django-dashboard
docker-compose logs -f pyspark-consumer
docker-compose logs -f kafka-producer

# Container status
docker ps
```

## 🛠️ Common Commands

```powershell
# Restart a service
docker-compose restart django-dashboard

# Rebuild a service
docker-compose up -d --build django-dashboard

# Stop all
docker-compose down

# Remove all data
docker-compose down -v

# Full restart
docker-compose down && docker-compose up -d
```

## 📈 Current Status

✅ **566+ tweets processed**  
✅ **All 10 containers running**  
✅ **Django on PostgreSQL**  
✅ **Real-time processing active**  

## 🎯 What's Running

- **Zookeeper** → Kafka coordination
- **Kafka** → Message streaming  
- **Producer** → Sending tweets every 3s
- **Consumer** → ML processing
- **PostgreSQL** → Data storage
- **Django** → Web dashboard
- **Prometheus** → Metrics
- **Grafana** → Visualization

## 💡 Tips

1. First time? It takes 30-60 seconds for all services to be ready
2. Check http://localhost:8000 after startup
3. Data persists even after `docker-compose down`
4. Use `docker-compose down -v` to clear all data

---

**Status:** 🟢 **OPERATIONAL**  
**Last Updated:** October 18, 2025
