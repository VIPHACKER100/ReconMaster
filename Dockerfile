# ReconMaster - Automated Reconnaissance Framework
# Docker container for easy deployment and usage
# 
# Build:    docker build -t reconmaster:latest .
# Run:      docker run -it reconmaster:latest -d example.com
# Shell:    docker run -it reconmaster:latest bash

FROM python:3.12-slim

# Set metadata
LABEL maintainer="VIPHACKER100"
LABEL description="Advanced Asynchronous Reconnaissance Framework"
LABEL version="3.0.0-Pro"

# Set working directory
WORKDIR /opt/reconmaster

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build tools
    build-essential \
    git \
    wget \
    curl \
    \
    # Go installation for Go tools
    golang-go \
    \
    # Tools for reconnaissance
    nmap \
    whois \
    dig \
    dnsutils \
    net-tools \
    \
    # Utilities
    unzip \
    vim \
    less \
    && rm -rf /var/lib/apt/lists/*

# Set GOPATH
ENV GOPATH=/root/go
ENV PATH=$GOPATH/bin:/usr/local/go/bin:$PATH

# Install Go-based reconnaissance tools
RUN go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest && \
    go install -v github.com/tomnomnom/assetfinder@latest && \
    go install -v github.com/OWASP/Amass/v3/...@master && \
    go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest && \
    go install -v github.com/ffuf/ffuf@latest && \
    go install -v github.com/sensepost/gowitness@latest && \
    go install -v github.com/projectdiscovery/katana/cmd/katana@latest && \
    go install -v github.com/lc/subjs@latest && \
    go install -v github.com/PentestPad/subzy@latest && \
    go install -v github.com/daffainfo/socialhunter@latest && \
    go install -v github.com/tomnomnom/LinkFinder@latest && \
    go install -v github.com/s0md3v/Arjun@latest

# Copy ReconMaster application
COPY . /opt/reconmaster/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create results directory
RUN mkdir -p /opt/reconmaster/results

# Create wordlists directory if not exists
RUN mkdir -p /opt/reconmaster/wordlists && \
    if [ ! -f /opt/reconmaster/wordlists/subdomains.txt ]; then \
        echo "Creating default wordlist..."; \
        touch /opt/reconmaster/wordlists/subdomains.txt; \
    fi

# Install ReconMaster in development mode
RUN pip install -e .

# Set default command to show help
ENTRYPOINT ["python", "-m", "reconmaster"]
CMD ["--help"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import reconmaster; print('OK')" || exit 1

# Labels for container metadata
LABEL org.opencontainers.image.title="ReconMaster"
LABEL org.opencontainers.image.description="Automated Reconnaissance Framework for Security Testing"
LABEL org.opencontainers.image.url="https://github.com/VIPHACKER100/ReconMaster"
LABEL org.opencontainers.image.documentation="https://github.com/VIPHACKER100/ReconMaster/wiki"
LABEL org.opencontainers.image.source="https://github.com/VIPHACKER100/ReconMaster"
LABEL org.opencontainers.image.version="3.0.0-Pro"
LABEL org.opencontainers.image.licenses="MIT"
