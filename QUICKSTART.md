# ReconMaster Quick Reference Guide
**Version:** 3.1.0  
**Last Updated:** February 9, 2026

## 🚀 Quick Start

### Installation (One Command)
```bash
# Clone and setup
git clone https://github.com/VIPHACKER100/ReconMaster.git
cd ReconMaster
chmod +x scripts/install_tools.sh && ./scripts/install_tools.sh
pip install -r requirements.txt
```

### First Scan
```bash
python reconmaster.py -d example.com --i-understand-this-requires-authorization
```

## 📋 Common Commands

### Basic Scans
```bash
# Standard scan
python reconmaster.py -d target.com --i-understand-this-requires-authorization

# Passive only (no active probing)
python reconmaster.py -d target.com --passive-only --i-understand-this-requires-authorization

# Aggressive mode
python reconmaster.py -d target.com --aggressive --i-understand-this-requires-authorization

# Quick scan
python reconmaster.py -d target.com --quick --i-understand-this-requires-authorization
```

### Advanced Scans
```bash
# Multiple domains
python reconmaster.py -d target.com -d api.target.com --i-understand-this-requires-authorization

# Custom wordlist
python reconmaster.py -d target.com --wordlist /path/to/wordlist.txt --i-understand-this-requires-authorization

# Custom output directory
python reconmaster.py -d target.com --output /custom/path --i-understand-this-requires-authorization

# Specific modules only
python reconmaster.py -d target.com --modules subdomain,dns,http --i-understand-this-requires-authorization

# Rate limiting
python reconmaster.py -d target.com --rate-limit 10 --i-understand-this-requires-authorization
```

### Automation
```bash
# Daily monitoring with notifications
python reconmaster.py -d target.com --daily --webhook https://discord.com/api/webhooks/YOUR_WEBHOOK --i-understand-this-requires-authorization

# Continuous mode with diff detection
python reconmaster.py -d target.com --continuous --diff-only --notify-on-new --i-understand-this-requires-authorization

# Scheduled scan (custom interval in minutes)
python reconmaster.py -d target.com --schedule 1440 --webhook https://slack.com/webhooks/YOUR_WEBHOOK --i-understand-this-requires-authorization
```

### Export & Integration
```bash
# Export to Burp Suite
python reconmaster.py -d target.com --export-burp --i-understand-this-requires-authorization

# Export to OWASP ZAP
python reconmaster.py -d target.com --export-zap --i-understand-this-requires-authorization

# Generate HTML/JSON/MD reports
python reconmaster.py -d target.com --report-format html,json,md --i-understand-this-requires-authorization
```

## ⚙️ Configuration

### Using Config File
```bash
# Create your config
cp config/config.yaml config/my-config.yaml

# Edit config
nano config/my-config.yaml

# Run with config
python reconmaster.py --config config/my-config.yaml
```

### Environment Variables
```bash
# Set environment variables
export RECON_DOMAIN="example.com"
export WEBHOOK_URL="https://discord.com/api/webhooks/YOUR_WEBHOOK"
export RECON_RATE_LIMIT="50"
export RECON_VERBOSE="2"

# Run scan
python reconmaster.py -d $RECON_DOMAIN --webhook $WEBHOOK_URL
```

## 🐳 Docker Usage

### Build Image
```bash
docker build -t reconmaster:latest .
```

### Run Scan
```bash
docker run --rm \
  -v $(pwd)/results:/app/recon_results \
  -e TARGET_DOMAIN=example.com \
  reconmaster:latest \
  -d example.com --i-understand-this-requires-authorization
```

### With Custom Config
```bash
docker run --rm \
  -v $(pwd)/config.yaml:/app/config.yaml \
  -v $(pwd)/results:/app/recon_results \
  reconmaster:latest \
  --config /app/config.yaml
```

### Docker Compose
```bash
# Edit docker-compose.yml with your settings
docker-compose up
```

## 🔧 Tool Management

### Install/Update Tools
```bash
# Install all tools
./scripts/install_tools.sh

# Update Nuclei templates
nuclei -update-templates

# Update Go tools
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
```

### Verify Installation
```bash
# Check tool versions
subfinder -version
httpx -version
nuclei -version
katana -version
dnsx -version
```

## 📊 Results & Reports

### View Results
```bash
# List recent scans
ls -lt recon_results/

# View summary
cat recon_results/target.com_*/summary.json | jq '.'

# View vulnerabilities
cat recon_results/target.com_*/vulns/nuclei_results.json | jq '.[] | select(.info.severity=="critical")'

# View subdomains
cat recon_results/target.com_*/subdomains/live_subdomains.txt
```

### Generate Reports
```bash
# HTML report (if not auto-generated)
python reconmaster.py -d target.com --report-format html --i-understand-this-requires-authorization

# Open HTML report
xdg-open recon_results/target.com_*/full_report.html  # Linux
open recon_results/target.com_*/full_report.html      # macOS
```

## 🔌 Plugin Management

### List Plugins
```bash
ls -l plugins/
```

### Enable/Disable Plugins
Edit `config/config.yaml`:
```yaml
advanced:
  plugins:
    enabled: true
    auto_load: true
    enabled_plugins:
      - wordpress_scanner
      # - cloud_scanner
```

### Create Custom Plugin
```python
# plugins/my_scanner.py
class MyScanner:
    def __init__(self):
        self.name = "my-scanner"
        self.version = "1.0.0"
    
    @property
    def metadata(self):
        return {"name": self.name, "version": self.version}
    
    async def execute(self, target, **kwargs):
        # Your scanning logic
        return {"results": []}

def get_plugin():
    return MyScanner()
```

## 🔍 Debugging

### Verbose Mode
```bash
# Level 1 (INFO)
python reconmaster.py -d target.com --verbose 1

# Level 2 (DEBUG)
python reconmaster.py -d target.com --verbose 2

# Level 3 (TRACE)
python reconmaster.py -d target.com --verbose 3
```

### Debug Mode
```bash
python reconmaster.py -d target.com --debug --save-logs
```

### View Logs
```bash
# Real-time monitoring
tail -f recon_results/target.com_*/logs/scan.log

# View errors only
cat recon_results/target.com_*/logs/errors.log

# View debug info
cat recon_results/target.com_*/logs/debug.log
```

## 🚨 Troubleshooting

### Tool Not Found
```bash
# Reinstall tools
./scripts/install_tools.sh

# Add to PATH
export PATH=$PATH:$HOME/go/bin
echo 'export PATH=$PATH:$HOME/go/bin' >> ~/.bashrc
```

### Rate Limiting / WAF
```bash
# Reduce rate limit
python reconmaster.py -d target.com --rate-limit 5

# Add delays
python reconmaster.py -d target.com --delay 2

# Use passive mode
python reconmaster.py -d target.com --passive-only
```

### Memory Issues
```bash
# Limit concurrent tasks
python reconmaster.py -d target.com --max-concurrent 10

# Disable heavy modules
python reconmaster.py -d target.com --modules subdomain,dns,http
```

### Docker Issues
```bash
# Rebuild image
docker build --no-cache -t reconmaster .

# Check logs
docker logs <container_id>

# Run with verbose output
docker run -e RECON_VERBOSE=3 reconmaster ...
```

## 🔄 Migration

### From v1.x/v2.x to v3.x
```bash
# Migrate configuration
python scripts/migrate_v1_to_v3.py --version v2 --config old_config.json

# Review new config
cat config/config.yaml

# Run with new config
python reconmaster.py --config config/config.yaml
```

## 🤖 CI/CD Setup

### GitHub Actions
```bash
# Copy example workflow
cp .github/workflows/reconmaster.yml.example .github/workflows/reconmaster.yml

# Configure secrets in GitHub Settings:
# - RECON_DOMAIN
# - WEBHOOK_URL

# Push and enable workflow
git add .github/workflows/reconmaster.yml
git commit -m "Add CI/CD workflow"
git push
```

### GitLab CI
```bash
# .gitlab-ci.yml is already in place

# Configure CI/CD variables in GitLab:
# - RECON_DOMAIN
# - DISCORD_WEBHOOK

# Create schedule in GitLab CI/CD > Schedules
```

### Jenkins
```bash
# Jenkinsfile is already in place

# Configure credentials in Jenkins:
# - recon-domain (Secret text)
# - discord-webhook (Secret text)

# Create new Pipeline job pointing to Jenkinsfile
```

## 📚 Useful Aliases

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# ReconMaster aliases
alias recon='python /path/to/ReconMaster/reconmaster.py'
alias recon-quick='recon --quick --i-understand-this-requires-authorization'
alias recon-passive='recon --passive-only --i-understand-this-requires-authorization'
alias recon-results='ls -lt /path/to/ReconMaster/recon_results/'
alias recon-update='cd /path/to/ReconMaster && ./scripts/install_tools.sh && nuclei -update-templates'
```

Usage:
```bash
recon -d example.com
recon-quick -d example.com
recon-passive -d example.com
recon-results
recon-update
```

## 🔗 Quick Links

- **Documentation:** [README.md](README.md)
- **Configuration:** [config/config.yaml](config/config.yaml)
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)
- **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)
- **Issues:** https://github.com/VIPHACKER100/ReconMaster/issues
- **Wiki:** https://github.com/VIPHACKER100/ReconMaster/wiki

## 💡 Pro Tips

1. **Use config files** for complex scans instead of long command lines
2. **Enable caching** to speed up repeated scans
3. **Set up daily automation** for continuous monitoring
4. **Use webhooks** for real-time notifications
5. **Export to Burp/ZAP** for manual testing
6. **Review logs** when scans fail
7. **Update tools regularly** for latest features
8. **Use Docker** for consistent environments
9. **Enable circuit breaker** to avoid WAF detection
10. **Always get authorization** before scanning

## ⚖️ Legal Reminder

**ALWAYS obtain written authorization before scanning any target!**

Use the `--i-understand-this-requires-authorization` flag to acknowledge this requirement.

---

**Need Help?**
- Check [Troubleshooting](#-troubleshooting) section
- Search [GitHub Issues](https://github.com/VIPHACKER100/ReconMaster/issues)
- Join [Discord Community](https://discord.gg/reconmaster)
- Read [Full Documentation](README.md)
