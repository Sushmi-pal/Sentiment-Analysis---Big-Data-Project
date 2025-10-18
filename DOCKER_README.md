# Running the Project with Docker

This guide explains how to run the entire Big Data Sentiment Analysis project using Docker.

## Prerequisites

- Docker Desktop installed and running
- At least 8GB of RAM available for Docker
- Docker Compose v2.x or higher

## Architecture

The Docker setup includes the following services:

1. **Zookeeper** - Kafka coordination service
2. **Kafka** - Message broker for streaming tweets
3. **PostgreSQL** - Database for storing processed tweets
4. **Kafka Producer** - Python service that reads tweets from CSV and sends to Kafka
5. **PySpark Consumer** - Processes tweets from Kafka using ML model and stores in PostgreSQL
6. **Django Dashboard** - Web interface to visualize sentiment analysis results
7. **Prometheus** - Monitoring and metrics collection
8. **Grafana** - Visualization dashboard for metrics
9. **Exporters** - Kafka and PostgreSQL exporters for Prometheus

## Quick Start

### 1. Build and Start All Services

```powershell
docker-compose up --build
```

This command will:
- Build all Docker images
- Start all containers
- Create Kafka topics automatically
- Initialize the PostgreSQL database
- Start the producer, consumer, and Django dashboard

### 2. Access the Services

Once all services are running, you can access:

- **Django Dashboard**: http://localhost:8000
  - View real-time sentiment analysis
  - Classify your own text at http://localhost:8000/classify

- **Grafana**: http://localhost:3000
  - Username: `admin`
  - Password: `admin`

- **Prometheus**: http://localhost:9090
  - View metrics and monitoring data

- **PostgreSQL**: localhost:5432
  - Database: `bigdata_project`
  - Username: `admin`
  - Password: `admin`

### 3. Run in Detached Mode (Background)

To run all services in the background:

```powershell
docker-compose up -d --build
```

### 4. View Logs

To view logs of all services:
```powershell
docker-compose logs -f
```

To view logs of a specific service:
```powershell
docker-compose logs -f django-dashboard
docker-compose logs -f pyspark-consumer
docker-compose logs -f kafka-producer
```

### 5. Stop All Services

```powershell
docker-compose down
```

To stop and remove all data (including volumes):
```powershell
docker-compose down -v
```

## Service Details

### Kafka Producer
- Reads tweets from `twitter_validation.csv`
- Sends tweets to Kafka topic `numtest` every 3 seconds
- Automatically restarts on failure

### PySpark Consumer
- Consumes tweets from Kafka topic `numtest`
- Processes tweets using the trained ML model
- Classifies sentiment: Positive, Negative, Neutral, or Irrelevant
- Stores results in PostgreSQL

### Django Dashboard
- Displays real-time sentiment analysis results
- Reads data from PostgreSQL
- Provides interactive visualizations and statistics

## Troubleshooting

### Container fails to start

Check logs:
```powershell
docker-compose logs [service-name]
```

### Kafka connection issues

Wait for Kafka to fully initialize (may take 30-60 seconds). Check Kafka status:
```powershell
docker-compose logs kafka1
```

### PostgreSQL connection issues

Ensure PostgreSQL is healthy:
```powershell
docker ps
```

Look for "healthy" status next to the postgres container.

### Rebuild specific service

```powershell
docker-compose up -d --build [service-name]
```

Example:
```powershell
docker-compose up -d --build django-dashboard
```

### Clear all Docker resources and restart

```powershell
docker-compose down -v
docker system prune -a
docker-compose up --build
```

## Development

### Modify Python Code

After modifying Python code, rebuild the affected service:

```powershell
# For producer changes
docker-compose up -d --build kafka-producer

# For consumer changes
docker-compose up -d --build pyspark-consumer

# For Django changes
docker-compose up -d --build django-dashboard
```

### Access Container Shell

To debug inside a container:

```powershell
docker exec -it [container-name] /bin/bash
```

Examples:
```powershell
docker exec -it django-dashboard /bin/bash
docker exec -it pyspark-consumer /bin/bash
docker exec -it kafka1 /bin/bash
```

## Monitoring

### View Kafka Topics

```powershell
docker exec kafka1 kafka-topics --list --bootstrap-server localhost:9092
```

### View PostgreSQL Data

Connect to PostgreSQL:
```powershell
docker exec -it postgres psql -U admin -d bigdata_project
```

Then run SQL queries:
```sql
SELECT COUNT(*) FROM tweets;
SELECT sentiment_classname, COUNT(*) FROM tweets GROUP BY sentiment_classname;
SELECT * FROM tweets ORDER BY id DESC LIMIT 10;
```

## Notes

- The first run will take longer as Docker downloads all images
- The ML model (`logistic_regression_model.pkl`) must exist in `ML PySpark Model/` directory
- Kafka may take 30-60 seconds to fully initialize
- The producer sends tweets every 3 seconds by default
- All data persists in Docker volumes even after stopping containers

## Port Usage

- 2181: Zookeeper
- 9092: Kafka
- 5432: PostgreSQL
- 8000: Django Dashboard
- 3000: Grafana
- 9090: Prometheus
- 9187: PostgreSQL Exporter
- 9308: Kafka Exporter
