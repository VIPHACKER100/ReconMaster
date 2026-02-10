# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.1.0-Pro] - 2026-02-10 - Elite Intelligence & API Discovery (Current)

- **Elite Intelligence Integration**: Native support for **Censys**, **SecurityTrails**, and **VirusTotal** APIs to boost passive discovery yield.
- **AI Threat Profiler**: Heuristic intelligence engine for automated risk analysis and remediation advice.
- **Regression Recon Engine**: State-aware diffing to identify new subdomains and vulnerabilities across scans.
- **Hidden API Fuzzer**: Specialized module (`fuzz_api_endpoints`) using elite Pro wordlists to discover undocumented API routes.
- **Expanded Asset Intelligence**: Integrated `api_endpoints.txt`, `common.txt`, and `quickhits.txt` specialized wordlists.
- **Pro-Grade Discovery**: Enhanced `discover_sensitive_files` with high-velocity path scanning.
- **Elite Reports**: Enhanced Markdown summaries with AI-driven threat profiles and regression alerts.
- **Premium Branding**: New SVG-based animated logo and high-fidelity project assets.
- **Windows Power-Up Installer**: Refactored PowerShell script for the full Pro toolset.
- **Multi-Source Configuration**: Support for `RECON_TARGET`, `RECON_DOMAIN`, and `TARGET_DOMAIN` environment variables.
- **Unified Circuit Breaker**: Introduced a robust `CircuitBreaker` class with state management (CLOSED, OPEN, HALF_OPEN) and cooldown periods.
- **Sensitive Data Redaction**: Integrated `SensitiveFilter` to automatically redact API keys and tokens from all log files.
- **Advanced Security Scan Workflow**: New GitHub Actions workflow (`recon-security-scan.yml`) with parallel matrix scanning and authorization checks.
- **YAML Configuration Support**: Added `load_config()` to support `config.yaml` for persistent settings.
- **Progress Tracking**: Real-time progress indicators for passive discovery tasks.

### Fixed
- **Windows Performance**: Parallelized `active_subdomain_enum` using `asyncio.gather` for significantly faster brute-forcing on Windows consoles.
- **Path Sanitization**: Fixed `WinError 123` and `Errno 22` by stripping protocols and invalid characters from target-based output paths.
- **Windows Compatibility**: Automated UTF-8 encoding configuration and `colorama` initialization for reliable terminal output.
- **Tool Resolution**: Enhanced `verify_tools` to support custom `bin/` and `tools/` path injection for portable installations.
- **CI/CD Stabilization**: Removed legacy LinkFinder submodule/dependencies to resolve GitHub Actions checkout errors.
- **Async Logic**: Fixed SyntaxError in sensitive file discovery module.
- **Dependency Map**: Unified `requirements.txt` with infrastructure and optional power-up libraries.
- **Domain Validation**: Enhanced `validate_target` method with input sanitization and security blocks for internal infrastructure.
- **Command Injection Protection**: Implemented `_sanitize_header_value()` for shell metacharacter scrubbing.
- **Path Traversal Prevention**: Strict `_safe_path()` utility for sandboxed file operations.
- **Maintenance**: Ensured robust resource cleanup in active enumeration and HTTP modules.
- **Endpoint Analysis**: Improved JS endpoint filtering logic to reduce false positives.
- **Performance**: Optimized aiohttp sessions with better connection pooling and memory guards for JS analysis.

## [3.0.0-Pro] - 2026-02-08 - ReconMaster v3 Asynchronous Rewrite

### Added
- **Asynchronous Core**: Complete rewrite using `asyncio` for high-performance concurrent reconnaissance.
- **Nuclei Integration**: Native support for enterprise-grade vulnerability scanning (Critical-Low).
- **Katana Integration**: Advanced crawling and endpoint discovery module.
- **Cross-Platform Asynchronicity**: Fixed Windows timeout issues which were previously dependent on SIGALRM.
- **Professional Reporting**: Integrated executive summaries and JSON-based telemetry.
- **Improved Tech Detection**: Enhanced tech-stack mapping via optimized httpx logic.
- **Adaptive Concurrency**: Semaphore-based resource management to prevent network saturation.
- **Stealth & Evasion**: Integrated **User-Agent Rotation** for all HTTP-based tools.
- **JS Secrets Engine**: Specialized parallel module for extracting API keys and secrets from JS files.
- **WAF Awareness**: Implemented **Circuit Breaker** logic to auto-throttle/stop on 403/429 spikes.
- **Robustness**: Process-group timeout termination to prevent orphaned zombie processes.
- **Security**: Mandatory absolute path resolution for binaries to mitigate PATH injection risks.
- **CI/CD Infrastructure**: Native **GitHub Actions** support for scheduled daily recon.
- **Containerization**: Full **Docker** support with a self-contained environment.
- **Professional Exports**: Automated **Burp Suite** Site Map and **OWASP ZAP** Context generation.
- **Discord/Slack Webhooks**: Native real-time alerting system for scan events.
- **Scope Control**: Implemented `--include` and `--exclude` filters for surgical scanning.
- **Resume Capability**: Persistent artifact-based checkpointing for mission-critical scans.
- **Legal Safeguards**: Mandatory authorization flag and strict FQDN validation.
- **Fast Resolve**: Integrated `dnsx` pre-validation to accelerate live host discovery.
- **Optimized Scanning**: Parallelized sensitive file discovery and JS analysis.

### Changed
- Refactored core engine for async operations
- Improved memory management for large datasets
- Enhanced error handling with custom exceptions
- Updated documentation with API specifications
- Migration to asyncio from threading pools

### Deprecated
- Legacy ThreadPoolExecutor pattern (use asyncio)

### Fixed
- Memory leaks in long-running scans
- Race conditions in concurrent operations
- File encoding issues on non-UTF8 systems
- Path traversal vulnerabilities in output handling

### Security
- Added input validation for all CLI arguments
- Implemented rate limiting to prevent abuse
- Secure credential handling for cloud integrations
- Sanitized all file operations against path traversal

## [2.0.0] - 2025-12-15 - ReconMaster v2 (Enhanced)

### Added
- **Concurrent Execution**: ThreadPoolExecutor for parallel tool execution
- **Progress Indicators**: tqdm progress bars for all operations
- **Verbose/Quiet Modes**: `--verbose` and `--quiet` flags
- **Configuration Files**: YAML-based configuration support
- **Scan Resumption**: Resume interrupted scans from last checkpoint
- **Retry Logic**: Automatic retry with exponential backoff for failed tools
- **State Persistence**: ``.reconmaster_state.json`` for scan recovery
- **Performance Optimization**: Thread pool caching and connection pooling
- **Enhanced Logging**: Detailed debug logging with timestamps
- **Tool Version Detection**: Verify minimum tool versions
- **Custom Hooks**: Pre/post scan execution hooks
- **Report Customization**: Multiple output format options (JSON, CSV, HTML)

### Changed
- Improved subprocess execution with better error handling
- Enhanced wordlist handling with streaming support
- Better timeout management across all operations
- Improved output formatting and readability
- Command-line interface restructuring

### Fixed
- Fixed hanging processes in tool execution
- Corrected memory usage during large scans
- Fixed race conditions in output file writing
- Improved cross-platform path handling

### Performance
- ~3-5x faster execution vs v1 (with threading)
- Reduced memory footprint during wordlist processing
- Optimized file I/O operations

## [1.0.0] - 2025-10-01 - ReconMaster (Core)

### Added
- **Passive Subdomain Enumeration**: subfinder, assetfinder, amass integration
- **Active Subdomain Brute Forcing**: ffuf with customizable wordlists
- **Live Domain Verification**: httpx for responsive domain filtering
- **Screenshot Capture**: gowitness integration for visual documentation
- **Subdomain Takeover Detection**: subzy scanning
- **Web Content Discovery**: katana crawler with configurable depth
- **JavaScript Analysis**: subjs and LinkFinder for endpoint extraction
- **Directory Brute Forcing**: ffuf directory enumeration
- **Parameter Discovery**: Arjun parameter enumeration
- **Broken Link Detection**: socialhunter integration
- **Port Scanning**: nmap integration for service discovery
- **Comprehensive Reporting**: Markdown report generation
- **Cross-Platform Support**: Windows (WSL2), Linux, macOS
- **Bundled Wordlists**: Minimal wordlists for offline operation
- **Structured Output**: Organized directory hierarchy for results
- **Logging System**: File and console logging

### Changed
- Initial release

## Variant Releases

### ProReconMaster (Enterprise) - 2026-01-15

**Enterprise-Grade Reconnaissance Platform**

#### Added
- Team collaboration and account management
- Centralized PostgreSQL/MongoDB database
- Role-based access control (RBAC)
- Audit logging and compliance reporting
- Scheduled and recurring scans
- Email report delivery
- Compliance templates (PCI DSS, HIPAA, SOC2)
- Advanced filtering and asset management
- Integration with vulnerability databases
- SAML/OAuth2 authentication
- API key management
- Custom dashboard and reports
- Data export in multiple formats

#### Pricing
- Enterprise: Custom quotes
- Professional: Annual subscription model

### Recon Black (Stealth) - 2025-11-20

**Stealth-Focused Reconnaissance**

#### Added
- Request randomization engine
- User-agent rotation
- Proxy/Tor support with automatic rotation
- Rate limiting with jitter
- Request header randomization
- Time-based execution (scheduled windows)
- Traffic obfuscation techniques
- Stealth level configuration (1-5)
- Minimal logging for operations security
- Decoy requests to evade detection

#### Use Cases
- Avoiding WAF/IDS detection
- Testing security detection capabilities
- Red team operations

### Recon Tool (Minimal) - 2025-11-01

**Lightweight, Pure Python Implementation**

#### Features
- No external tool dependencies
- Standard library + requests only
- Basic subdomain brute forcing
- DNS resolution and verification
- HTTP probing
- Directory enumeration (limited)
- Minimal reporting
- Small resource footprint

#### Use Cases
- Restricted environments
- Quick baseline scans
- Air-gapped systems

---

## Version Comparison

| Feature | v1 | v2 | v3 | Pro | Black |
|---------|----|----|----|----|-------|
| Passive Enumeration | ✅ | ✅ | ✅ | ✅ | ✅ |
| Active Brute Force | ✅ | ✅ | ✅ | ✅ | ✅ |
| Threading | ❌ | ✅ | ✅ | ✅ | ✅ |
| Async Execution | ❌ | ❌ | ✅ | ✅ | ✅ |
| Configuration Files | ❌ | ✅ | ✅ | ✅ | ✅ |
| Scan Resume | ❌ | ✅ | ✅ | ✅ | ✅ |
| Plugins | ❌ | ❌ | ✅ | ✅ | ❌ |
| Cloud Export | ❌ | ❌ | ✅ | ✅ | ❌ |
| Team Collaboration | ❌ | ❌ | ❌ | ✅ | ❌ |
| Database Backend | ❌ | ❌ | ❌ | ✅ | ❌ |
| Stealth Features | ❌ | ❌ | ❌ | ❌ | ✅ |
| Minimal Footprint | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## Roadmap

### Planned for v3.1
- [ ] GraphQL endpoint detection
- [ ] SOAP API analysis
- [ ] Mobile app reconnaissance
- [ ] AWS/Azure asset discovery
- [ ] Kubernetes cluster scanning

### Planned for v4.0
- [ ] Visual dashboard UI
- [ ] Real-time collaboration
- [ ] Advanced ML-based vulnerability detection
- [ ] Integration with SIEM platforms
- [ ] Automated exploitation (with consent)

### Community Requests
- [ ] Github/GitLab API integration
- [ ] S3 bucket enumeration
- [ ] Subdomain wildcard detection
- [ ] CORS misconfiguration detection
- [ ] CSP header analysis

---

## Support

- **Latest Release**: v3.0.0
- **LTS Release**: v2.0.0 (support until 2027-02-01)
- **EOL Release**: v1.0.0 (support ended 2025-10-01)

For upgrade assistance, see [UPGRADING.md](docs/UPGRADING.md).

---

**Maintained by**: viphacker100  
**License**: MIT  
**Repository**: https://github.com/VIPHACKER100/ReconMaster
