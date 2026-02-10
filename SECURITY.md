# Security Policy

## Responsible Use
**ReconMaster** is designed for **authorized security testing and ethical hacking only**. By using this tool, you agree to:
- Only scan infrastructure you own or have explicit, documented permission to test.
- Adhere to all local, state, and international laws regarding cybersecurity and data privacy.
- Avoid causing disruption or damage to any system or network.

The author assumes **no liability** for any misuse, damage, or illegal activities performed with this tool.

## Internal Security Features
ReconMaster v3.1.0-Pro implements several internal security controls:
- **Sensitive Data Redaction**: Log filters automatically redact API keys (**Censys, SecurityTrails, VirusTotal**, Google, AWS, GitHub, etc.) and passwords.
- **Circuit Breaker**: Protects against WAF blocking and rate limiting by auto-throttling requests.
- **Path Traversal Protection**: All file writes are sandboxed using strict path verification.
- **Command Injection Protection**: Defensive sanitization of dynamic inputs used in shell commands.
- **Internal Infrastructure Guard**: Built-in blocks prevent accidental scanning of localhost or private networks.

## Reporting a Vulnerability
If you discover a security issue in ReconMaster itself, please report it responsibly:
1. Open a private issue on GitHub (if available) or contact the author directly at [GitHub Profile](https://github.com/VIPHACKER100).
2. Provide a detailed description of the vulnerability and steps to reproduce it.
3. Allow reasonable time for the author to address the issue before public disclosure.

Thank you for helping keep ReconMaster secure!

**Last Updated:** February 10, 2026
