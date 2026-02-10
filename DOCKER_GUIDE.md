# Docker Usage Guide for ReconMaster

## Overview

ReconMaster can be deployed and run using Docker, providing:
- ✅ Isolated environment
- ✅ All dependencies pre-installed
- ✅ Cross-platform compatibility
- ✅ Easy scaling and deployment
- ✅ Integration with Kubernetes and container orchestration

---

## Building the Docker Image

### From Dockerfile

```bash
# Build the image
docker build -t reconmaster:latest .

# Build with custom tag
docker build -t reconmaster:3.1.0-Pro .

# Build without cache
docker build --no-cache -t reconmaster:latest .

# Build with build arguments
docker build --build-arg PYTHON_VERSION=3.10 -t reconmaster:latest .
```

### Using Docker Compose

```bash
# Build and start
docker-compose up --build

# Build only
docker-compose build

# Rebuild without cache
docker-compose build --no-cache
```

---

## Running ReconMaster in Docker

### Basic Usage

```bash
# Show help
docker run reconmaster:latest --help

# Scan a domain
docker run -it reconmaster:latest -d example.com

# Scan with custom output (in container)
docker run -it reconmaster:latest -d example.com -o /opt/reconmaster/results
```

### With Volume Mounting

```bash
# Mount results directory to host
docker run -it \
  -v ~/recon_results:/opt/reconmaster/results \
  reconmaster:latest \
  -d example.com

# Mount both input and output
docker run -it \
  -v ~/wordlists:/opt/reconmaster/wordlists:ro \
  -v ~/recon_results:/opt/reconmaster/results \
  reconmaster:latest \
  -d example.com -w /opt/reconmaster/wordlists/custom.txt

# Mount current directory
docker run -it \
  -v $(pwd)/results:/opt/reconmaster/results \
  reconmaster:latest \
  -d example.com

# Mount configuration file
docker run -it \
  -v $(pwd)/config.yaml:/opt/reconmaster/config.yaml:ro \
  -v $(pwd)/results:/opt/reconmaster/results \
  reconmaster:latest \
  -d example.com
```

### With Custom Parameters

```bash
# Custom rate limit
docker run -it reconmaster:latest \
  -d example.com \
  --rate-limit 5.0

# Custom threads
docker run -it reconmaster:latest \
  -d example.com \
  --threads 20

# Passive only
docker run -it reconmaster:latest \
  -d example.com \
  --passive-only

# All custom parameters
docker run -it \
  -v ~/results:/opt/reconmaster/results \
  reconmaster:latest \
  -d example.com \
  -o /opt/reconmaster/results \
  --rate-limit 10.0 \
  --threads 15 \
  --passive-only
```

### Interactive Shell

```bash
# Access container shell
docker run -it reconmaster:latest bash

# From shell, run commands
root@container:/opt/reconmaster# python reconmaster.py -d example.com
root@container:/opt/reconmaster# python -m pytest tests/
root@container:/opt/reconmaster# exit
```

### Running Tests

```bash
# Run all tests
docker run reconmaster:latest python -m pytest tests/

# Run specific test file
docker run reconmaster:latest python -m pytest tests/test_utils.py -v

# Run with coverage
docker run reconmaster:latest python -m pytest tests/ --cov=. --cov-report=term-missing
```

---

## Docker Compose Usage

### Basic Commands

```bash
# Start service
docker-compose up

# Start in background
docker-compose up -d

# Stop service
docker-compose down

# View logs
docker-compose logs -f

# Rebuild image
docker-compose build --no-cache
```

### Running Scans with Compose

```bash
# Run a scan
docker-compose run reconmaster -d example.com

# Run with custom parameters
docker-compose run reconmaster -d example.com --rate-limit 5.0

# Run interactive shell
docker-compose run reconmaster bash

# Run tests
docker-compose run reconmaster python -m pytest tests/
```

### Advanced Compose Usage

```bash
# Run with specific service
docker-compose run --service reconmaster -d example.com

# Run with environment variables
docker-compose run \
  -e RECONMASTER_RATE_LIMIT=5.0 \
  reconmaster -d example.com

# Run and remove container after
docker-compose run --rm reconmaster -d example.com

# Rebuild and run
docker-compose build && docker-compose run reconmaster -d example.com
```

---

## Environment Variables

### Available Variables

```bash
# Set rate limit
RECONMASTER_RATE_LIMIT=10.0

# Set thread count
RECONMASTER_THREADS=10

# Set output directory
RECONMASTER_OUTPUT_DIR=/opt/reconmaster/results

# Python settings
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
```

### Using Environment Variables

```bash
# Docker run
docker run \
  -e RECONMASTER_RATE_LIMIT=5.0 \
  -e RECONMASTER_THREADS=15 \
  reconmaster:latest -d example.com

# Docker compose
docker-compose run \
  -e RECONMASTER_RATE_LIMIT=5.0 \
  reconmaster -d example.com
```

---

## Volume Management

### Creating Volumes

```bash
# Create named volume
docker volume create reconmaster-results

# Use named volume
docker run -it \
  -v reconmaster-results:/opt/reconmaster/results \
  reconmaster:latest -d example.com

# List volumes
docker volume ls

# Inspect volume
docker volume inspect reconmaster-results

# Remove volume
docker volume rm reconmaster-results
```

### Accessing Results

```bash
# View results in volume
docker run -it \
  -v reconmaster-results:/opt/reconmaster/results \
  alpine ls -la /opt/reconmaster/results

# Copy results from volume
docker run --rm \
  -v reconmaster-results:/data \
  -v $(pwd):/output \
  alpine cp -r /data /output/results

# Mount and inspect
docker run -it \
  -v reconmaster-results:/results \
  alpine sh -c "cd /results && find . -type f"
```

---

## Networking

### Port Exposure

```bash
# Expose port (if ReconMaster had a web interface)
docker run -p 8080:8080 reconmaster:latest

# Multiple ports
docker run \
  -p 8080:8080 \
  -p 8081:8081 \
  reconmaster:latest
```

### Custom Networks

```bash
# Create network
docker network create reconmaster-net

# Run with custom network
docker run \
  --network reconmaster-net \
  --name reconmaster \
  reconmaster:latest -d example.com

# Connect another container
docker run \
  --network reconmaster-net \
  --link reconmaster \
  alpine ping reconmaster
```

---

## Resource Management

### Memory Limits

```bash
# Limit memory to 2GB
docker run \
  -m 2g \
  reconmaster:latest -d example.com

# Limit CPU
docker run \
  --cpus 2 \
  reconmaster:latest -d example.com

# Both limits
docker run \
  -m 2g \
  --cpus 2 \
  reconmaster:latest -d example.com
```

### With Docker Compose

```yaml
services:
  reconmaster:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

---

## Troubleshooting

### Container Issues

```bash
# View running containers
docker ps

# View all containers (including stopped)
docker ps -a

# View container logs
docker logs container_id

# Follow logs
docker logs -f container_id

# View detailed logs
docker logs --details container_id

# Get container info
docker inspect container_id
```

### Image Issues

```bash
# List images
docker images

# View image details
docker inspect image_id

# Remove image
docker rmi image_id

# Remove unused images
docker image prune

# Build with verbose output
docker build --progress=plain -t reconmaster:latest .
```

### Volume Issues

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect volume_name

# Prune unused volumes
docker volume prune

# Remove all volumes
docker volume rm $(docker volume ls -q)
```

### Network Issues

```bash
# List networks
docker network ls

# Inspect network
docker network inspect network_name

# Check DNS resolution
docker run --rm alpine nslookup reconmaster

# Test connectivity
docker run --rm alpine ping container_name
```

---

## Health Checks

The Dockerfile includes health checks:

```bash
# Check health status
docker ps --format "table {{.Names}}\t{{.Status}}"

# Run health check
docker run --health-cmd "python -c 'import reconmaster; print(\"OK\")'" \
  reconmaster:latest
```

---

## Kubernetes Deployment

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: reconmaster
spec:
  containers:
  - name: reconmaster
    image: reconmaster:latest
    imagePullPolicy: IfNotPresent
    args: ["-d", "example.com"]
    volumeMounts:
    - name: results
      mountPath: /opt/reconmaster/results
    resources:
      limits:
        memory: "2Gi"
        cpu: "2"
      requests:
        memory: "1Gi"
        cpu: "1"
    livenessProbe:
      exec:
        command:
        - python
        - -c
        - "import reconmaster; print('OK')"
      initialDelaySeconds: 10
      periodSeconds: 30
  volumes:
  - name: results
    emptyDir: {}
```

---

## Best Practices

### Security

```bash
# Run as non-root (in Dockerfile)
RUN useradd -m -u 1000 reconmaster
USER reconmaster

# Use read-only volumes
docker run -v ~/wordlists:/wordlists:ro reconmaster:latest

# Don't use latest tag in production
docker run reconmaster:1.0.0
```

### Performance

```bash
# Multi-stage Dockerfile for smaller images
# Use specific Python version (not latest)
# Cache layers efficiently
# Minimize layers

# Use docker-compose for orchestration
docker-compose up -d
```

### Logging

```bash
# Configure logging driver
docker run \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  reconmaster:latest -d example.com
```

---

## Examples

### Example 1: Quick Scan

```bash
# Simple one-liner for quick scan
docker run -it \
  -v $(pwd)/results:/opt/reconmaster/results \
  reconmaster:latest \
  -d example.com -o /opt/reconmaster/results
```

### Example 2: Stealth Mode

```bash
# Slow scanning to avoid detection
docker run -it \
  -v $(pwd)/results:/opt/reconmaster/results \
  reconmaster:latest \
  -d example.com \
  --rate-limit 2.0 \
  --passive-only
```

### Example 3: Heavy Scanning

```bash
# Aggressive scanning with high parallelism
docker run -it \
  -m 4g \
  --cpus 4 \
  -v $(pwd)/results:/opt/reconmaster/results \
  reconmaster:latest \
  -d example.com \
  --threads 50 \
  --rate-limit 50.0
```

### Example 4: Batch Processing

```bash
# Scan multiple domains
for domain in example.com test.com site.com; do
  docker run -it \
    -v $(pwd)/results/$domain:/opt/reconmaster/results \
    reconmaster:latest \
    -d $domain
done
```

### Example 5: With Docker Compose

```bash
# docker-compose.yml already configured
docker-compose run reconmaster -d example.com
docker-compose run reconmaster -d test.com --rate-limit 5.0
docker-compose down
```

---

## Support

- **Documentation:** See [PHASE_19_GUIDE.md](PHASE_19_GUIDE.md)
- **Docker Hub:** [reconmaster:latest](https://hub.docker.com/r/VIPHACKER100/reconmaster)
- **Issues:** [GitHub Issues](https://github.com/VIPHACKER100/ReconMaster/issues)

---

## Summary

ReconMaster Docker provides:
- ✅ Easy installation and deployment
- ✅ Isolated environment
- ✅ All dependencies included
- ✅ Cross-platform compatibility
- ✅ Kubernetes support
- ✅ Production-ready

Start using Docker: `docker run reconmaster:latest --help`

---

**Last Updated:** February 10, 2026  
**Version:** 3.1.0-Pro
