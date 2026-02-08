# Security Policy

## Reporting Security Vulnerabilities

**Do not** open public issues for security vulnerabilities. Instead, please report security vulnerabilities responsibly through our private disclosure process.

### How to Report

1. **Email:** Send a detailed report to [security@example.com]
   * Include a clear description of the vulnerability
   * Provide steps to reproduce the issue
   * Include any relevant code samples or proof-of-concept
   * Suggest a fix if you have one

2. **Timing:** Please allow us 90 days to address the vulnerability before public disclosure

3. **Acknowledgment:** We will acknowledge receipt of your report within 24 hours

### What We'll Do

1. Confirm receipt of your security report
2. Assess the severity and impact
3. Develop and test a fix
4. Prepare a security advisory
5. Release a patched version
6. Acknowledge your responsible disclosure (if desired)

---

## Security Best Practices

When using ReconMaster, please follow these security best practices:

### Credentials & API Keys
* **Never** commit credentials to version control
* Use environment variables for sensitive configuration
* Rotate API keys regularly
* Use separate keys for different environments

### Target Authorization
* **Always** get written authorization before scanning any target
* Respect rate limits and backoff policies
* Use the built-in rate limiting features
* See [LEGAL.md](LEGAL.md) for jurisdictional restrictions

### Data Protection
* Sanitize and secure output files containing sensitive data
* Encrypt sensitive data at rest and in transit
* Use HTTPS for all network communications
* Be mindful of data retention policies

### Dependency Management
* Keep dependencies up to date
* Monitor for security advisories
* Use `pip check` and `safety` to identify vulnerabilities
* Review dependency changes in pull requests

---

## Supported Versions

| Version | Supported | Status |
|---------|-----------|--------|
| 3.0.x   | ✅ Yes    | Latest |
| 2.0.x   | ✅ Yes    | Maintenance |
| 1.0.x   | ❌ No     | EOL |

---

## Security Advisories

### Release Process

1. **Development:** New version in development branch
2. **Testing:** Comprehensive security testing
3. **Review:** Security audit and code review
4. **Preparation:** Security advisory drafted
5. **Release:** Version tagged and published
6. **Notification:** Users notified via release notes

### Notification

Security advisories are published:
* In release notes
* On GitHub Security Advisory
* Via email to security mailing list (opt-in)
* On project social media

---

## Python Version Support

ReconMaster supports Python 3.7 and later:
* 3.7 - Supported (security fixes only)
* 3.8 - Supported
* 3.9 - Supported
* 3.10 - Supported
* 3.11 - Supported
* 3.12 - Supported (latest)

---

## Dependencies

ReconMaster uses well-maintained, widely-trusted dependencies:
* requests - HTTP library
* dnspython - DNS resolution
* beautifulsoup4 - HTML parsing
* click - CLI framework

All dependencies are regularly updated and monitored for vulnerabilities.

---

## Container Security

### Docker Images

* Based on official Python images
* Minimal, lightweight base images
* Regular updates for security patches
* Scan images with vulnerability tools

### Dockerfile Security

```dockerfile
# Best practices followed:
- Non-root user (when possible)
- Minimal attack surface
- Health checks enabled
- Security headers configured
- Secrets not embedded in image
```

---

## Third-Party Tools

ReconMaster integrates with external security tools:
* subfinder, assetfinder, amass (subdomain discovery)
* httpx, ffuf (active scanning)
* nmap (port scanning)
* gowitness, katana, subzy, socialhunter (specialized tools)

**Important:** External tools may have their own security considerations. Always:
1. Keep tools updated
2. Review tool security advisories
3. Use tools responsibly
4. Respect rate limits and legal restrictions

---

## Compliance

### Legal Compliance
- Ensure proper authorization before any scanning
- Comply with local laws and regulations
- See [LEGAL.md](LEGAL.md) for jurisdictional information

### Responsible Disclosure
- Report vulnerabilities privately
- Allow time for remediation
- Don't publicly disclose until patched
- Respect embargoes on security information

---

## Security Checklist

Before using ReconMaster in production:

- [ ] Read [LEGAL.md](LEGAL.md) and understand jurisdictional restrictions
- [ ] Obtain written authorization for all targets
- [ ] Configure rate limiting appropriately
- [ ] Store output files securely
- [ ] Encrypt sensitive configuration
- [ ] Keep dependencies updated
- [ ] Review your scan scope carefully
- [ ] Monitor for security advisories
- [ ] Test in staging environment first
- [ ] Implement access controls on results

---

## Questions?

For security-related questions:
* **Vulnerabilities:** [security@example.com]
* **General Questions:** security@example.com or open an issue
* **Legal Concerns:** [contact@example.com]

---

## Attribution

This Security Policy follows best practices from:
* [OWASP](https://owasp.org/)
* [Python Security SIG](https://www.python.org/dev/sigs/security-sig/)
* Industry standards for responsible disclosure

---

**Last Updated:** February 8, 2026  
**Version:** 3.0.0-Pro
