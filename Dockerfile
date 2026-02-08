FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/root/go/bin:${PATH}"

RUN apt update && apt install -y \
    git curl wget unzip nmap jq build-essential chromium \
    && rm -rf /var/lib/apt/lists/*

# Install Go
RUN curl -fsSL https://go.dev/dl/go1.22.0.linux-amd64.tar.gz | tar -C /usr/local -xz
ENV PATH="/usr/local/go/bin:${PATH}"

# Install Recon tools
RUN go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest && \
    go install github.com/projectdiscovery/httpx/cmd/httpx@latest && \
    go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest && \
    go install github.com/projectdiscovery/dnsx/cmd/dnsx@latest && \
    go install github.com/projectdiscovery/katana/cmd/katana@latest && \
    go install github.com/ffuf/ffuf@latest && \
    go install github.com/sensepost/gowitness@latest && \
    go install github.com/tomnomnom/assetfinder@latest && \
    go install github.com/owasp-amass/amass/v4/...@latest

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python3", "reconmaster.py"]
