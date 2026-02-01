# ReconMaster Quick Reference Guide

**Version:** 1.0.0  
**Status:** Production Ready ✅  
**Last Updated:** February 1, 2026

---

## 🚀 Installation (Choose One)

### PyPI (Recommended for End Users)
```bash
pip install reconmaster
```

### Docker (Recommended for DevOps)
```bash
docker build -t reconmaster:latest .
docker run reconmaster:latest -d example.com
```

### Source (Recommended for Developers)
```bash
git clone https://github.com/yourusername/ReconMaster.git
cd ReconMaster
pip install -e .
```

---

## 📖 Documentation Quick Links

| Document | Purpose | Read Time |
|----------|---------|-----------|
| [README.md](README.md) | Project overview | 5 min |
| [PHASE_19_GUIDE.md](PHASE_19_GUIDE.md) | Deployment guide | 15 min |
| [PHASE_19_COMPLETION.md](PHASE_19_COMPLETION.md) | Completion summary | 10 min |
| [PYPI_GUIDE.md](PYPI_GUIDE.md) | PyPI installation | 10 min |
| [DOCKER_GUIDE.md](DOCKER_GUIDE.md) | Docker deployment | 15 min |
| [PHASE_18_GUIDE.md](PHASE_18_GUIDE.md) | Security features | 10 min |
| [LEGAL.md](LEGAL.md) | Legal compliance | 5 min |

---

## ⚡ Usage Examples

### Quick Scan
```bash
reconmaster -d example.com
```

### With Output File
```bash
reconmaster -d example.com -o results.json
```

### Custom Parameters
```bash
reconmaster -d example.com \
  --rate-limit 5.0 \
  --threads 15 \
  --passive-only
```

### Docker Scan
```bash
docker run -it \
  -v $(pwd)/results:/opt/reconmaster/results \
  reconmaster:latest \
  -d example.com
```

### Python API
```python
from reconmaster import ReconMaster

scanner = ReconMaster(domain="example.com")
results = scanner.run_full_scan()
```

---

## 🔧 Command-Line Options

```bash
reconmaster --help

Options:
  -d, --domain TEXT           Target domain [required]
  -o, --output TEXT           Output file path
  -w, --wordlist TEXT         Custom wordlist
  --rate-limit FLOAT          Rate limit (requests/sec)
  --threads INTEGER           Thread count
  --passive-only              Only passive scanning
  -h, --help                  Show help
```

---

## 🐳 Docker Quick Reference

### Build
```bash
docker build -t reconmaster:latest .
```

### Run
```bash
docker run reconmaster:latest -d example.com
```

### With Volume
```bash
docker run -v $(pwd)/results:/opt/reconmaster/results \
  reconmaster:latest -d example.com
```

### Docker Compose
```bash
docker-compose run reconmaster -d example.com
```

### View Logs
```bash
docker logs container_id
docker-compose logs -f
```

---

## 📦 PyPI Quick Reference

### Install
```bash
pip install reconmaster
```

### Upgrade
```bash
pip install --upgrade reconmaster
```

### Check Installation
```bash
pip show reconmaster
reconmaster --help
```

### Uninstall
```bash
pip uninstall reconmaster
```

---

## 🧪 Testing

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test
```bash
pytest tests/test_utils.py -v
```

### With Coverage
```bash
pytest tests/ --cov=. --cov-report=term-missing
```

### Docker Tests
```bash
docker-compose run reconmaster pytest tests/
```

---

## 🔐 Security & Compliance

### Rate Limiting
```bash
# Slow down to avoid detection
reconmaster -d example.com --rate-limit 2.0
```

### Legal Compliance
See [LEGAL.md](LEGAL.md) for jurisdictional restrictions

### Safe Mode
```bash
# Only passive scanning
reconmaster -d example.com --passive-only
```

---

## 🌐 Supported Environments

| OS | Support | Recommended Setup |
|---|---------|---|
| Linux | ✅ Full | Native installation |
| macOS | ✅ Full | Native installation |
| Windows | ✅ Full | Docker or WSL2 |

---

## 🆘 Troubleshooting

### Command Not Found (PyPI)
```bash
# Check installation
pip show reconmaster

# Use Python module
python -m reconmaster --help

# Install for current user
pip install --user reconmaster
```

### Docker Issues
```bash
# Check images
docker images

# View logs
docker logs container_id

# Rebuild
docker build --no-cache -t reconmaster:latest .
```

### Import Errors
```bash
# Reinstall
pip install --force-reinstall reconmaster

# Check dependencies
pip check

# Verify Python version
python --version  # 3.7+
```

---

## 📊 File Structure

```
ReconMaster/
├── reconmaster.py         # Main framework
├── rate_limiter.py        # Rate limiting
├── utils.py               # Utilities
├── setup.py               # PyPI config
├── Dockerfile             # Docker image
├── docker-compose.yml     # Local testing
├── pyproject.toml         # Packaging config
├── requirements.txt       # Dependencies
├── tests/                 # Unit tests
├── wordlists/             # Built-in lists
└── docs/                  # Documentation
```

---

## 🎯 Key Features

| Feature | Status | Notes |
|---------|--------|-------|
| Subdomain Enumeration | ✅ | Multiple tools |
| Rate Limiting | ✅ | Configurable |
| Legal Compliance | ✅ | Built-in warnings |
| Docker Support | ✅ | Full image |
| PyPI Distribution | ✅ | `pip install` |
| Unit Tests | ✅ | 35+ tests |
| CI/CD Automation | ✅ | GitHub Actions |

---

## 📈 Statistics

- **Lines of Code:** 11,320+
- **Documentation:** 3,050+ lines
- **Unit Tests:** 35+
- **CI/CD Matrix:** 15 combinations
- **Python Versions:** 3.7-3.11
- **Platforms:** Linux, macOS, Windows
- **Code Coverage:** 80%+

---

## 🔄 Update Instructions

### PyPI Version
```bash
pip install --upgrade reconmaster
```

### Docker Image
```bash
docker pull reconmaster:latest
```

### Source Version
```bash
cd ReconMaster
git pull
pip install -e .
```

---

## 💡 Pro Tips

1. **Use Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install reconmaster
   ```

2. **Save Configuration**
   ```bash
   export RECONMASTER_RATE_LIMIT=5.0
   export RECONMASTER_THREADS=10
   ```

3. **Batch Processing**
   ```bash
   for domain in domains.txt; do
     reconmaster -d "$domain" -o "results/$domain.json"
   done
   ```

4. **Docker with Compose**
   ```bash
   docker-compose up -d
   docker-compose run reconmaster -d example.com
   ```

---

## ❓ FAQ

**Q: Which installation method should I use?**  
A: PyPI for end-users, Docker for DevOps, Source for developers.

**Q: How do I avoid detection?**  
A: Use `--rate-limit 2.0` and `--passive-only` flags.

**Q: Can I use this on Windows?**  
A: Yes, via Docker or WSL2. Docker is recommended.

**Q: How do I report issues?**  
A: Use GitHub Issues: [issues](https://github.com/yourusername/ReconMaster/issues)

**Q: Is there a commercial version?**  
A: Not yet. See Phase 11 for potential premium variants.

---

## 📞 Support Resources

| Resource | Link | Purpose |
|----------|------|---------|
| Documentation | [PHASE_19_GUIDE.md](PHASE_19_GUIDE.md) | Full deployment guide |
| PyPI Guide | [PYPI_GUIDE.md](PYPI_GUIDE.md) | Installation help |
| Docker Guide | [DOCKER_GUIDE.md](DOCKER_GUIDE.md) | Docker deployment |
| Issues | GitHub Issues | Bug reports |
| Legal | [LEGAL.md](LEGAL.md) | Compliance info |

---

## 🎓 Learning Path

1. **Beginner:** Read [README.md](README.md) (5 min)
2. **User:** Follow [PYPI_GUIDE.md](PYPI_GUIDE.md) (10 min)
3. **DevOps:** Read [DOCKER_GUIDE.md](DOCKER_GUIDE.md) (15 min)
4. **Developer:** See [PHASE_19_GUIDE.md](PHASE_19_GUIDE.md) (15 min)
5. **Advanced:** Check Phase 18+ guides (30 min)

---

## ✅ Checklist for First Use

- [ ] Install ReconMaster (pip/docker/source)
- [ ] Verify installation works
- [ ] Read [LEGAL.md](LEGAL.md) (legal requirements)
- [ ] Scan test domain: `reconmaster -d example.com`
- [ ] Review results in output file
- [ ] Configure rate limiting if needed
- [ ] Check [DOCKER_GUIDE.md](DOCKER_GUIDE.md) for deployment options

---

## 🚀 Next Steps

1. **Install:** Choose installation method above
2. **Verify:** Run `reconmaster --help`
3. **Scan:** Try test scan `reconmaster -d example.com`
4. **Learn:** Read relevant documentation guide
5. **Deploy:** Use PyPI/Docker for production
6. **Contribute:** Submit improvements via GitHub

---

## 📄 Legal Notice

ReconMaster is for authorized security testing only. Always obtain permission before scanning. See [LEGAL.md](LEGAL.md) for important legal information.

---

**Quick Access:** [Installation Guide](PYPI_GUIDE.md) | [Docker Guide](DOCKER_GUIDE.md) | [Deployment Guide](PHASE_19_GUIDE.md) | [Full Documentation](README.md)

---

**Version:** 1.0.0  
**Status:** Production Ready ✅  
**Last Updated:** February 1, 2026
