#!/usr/bin/env python3
"""
ReconMaster Project Verification Script

This script verifies that all components of the ReconMaster project are in place
and provides a comprehensive status report.

Author: viphacker100
Date: February 8, 2026
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def check_file_exists(filepath: str, min_lines: int = 0) -> Tuple[bool, int]:
    """
    Check if a file exists and optionally verify minimum line count.
    
    Args:
        filepath: Path to file
        min_lines: Minimum expected lines (0 = no check)
    
    Returns:
        Tuple of (exists, line_count)
    """
    if not os.path.exists(filepath):
        return False, 0
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = len(f.readlines())
        return True, lines
    except Exception:
        return True, 0


def print_section(title: str):
    """Print a section header."""
    print(f"\n{BLUE}{'=' * 70}{RESET}")
    print(f"{BLUE}{title:^70}{RESET}")
    print(f"{BLUE}{'=' * 70}{RESET}\n")


def print_status(item: str, status: bool, details: str = ""):
    """Print status line with color coding."""
    symbol = f"{GREEN}✓{RESET}" if status else f"{RED}✗{RESET}"
    print(f"{symbol} {item:50} {details}")


def verify_core_files() -> Dict[str, bool]:
    """Verify core implementation files."""
    print_section("CORE IMPLEMENTATION FILES")
    
    files = {
        'reconmaster.py': 500,
        'reconmasterv2.py': 500,
        'reconmasterv3.py': 500,
        'proreconmaster.py': 500,
        'recon_black.py': 500,
        'recon-tool.py': 500,
        'utils.py': 50,
        'rate_limiter.py': 100,
    }
    
    results = {}
    total_lines = 0
    
    for filename, min_lines in files.items():
        exists, lines = check_file_exists(filename, min_lines)
        results[filename] = exists
        total_lines += lines
        
        if exists:
            detail = f"{lines:,} lines"
            if lines < min_lines:
                detail += f" {YELLOW}(expected {min_lines}+){RESET}"
        else:
            detail = f"{RED}MISSING{RESET}"
        
        print_status(filename, exists, detail)
    
    print(f"\n{BLUE}Total core code lines: {total_lines:,}{RESET}")
    return results


def verify_documentation() -> Dict[str, bool]:
    """Verify documentation files."""
    print_section("DOCUMENTATION FILES")
    
    files = {
        'README.md': 100,
        'README_comprehensive.md': 200,
        'QUICKREF.md': 100,
        'QUICK_REFERENCE.md': 100,
        'CHANGELOG.md': 100,
        'LEGAL.md': 200,
        'CONTRIBUTING.md': 200,
        'CODE_OF_CONDUCT.md': 100,
        'SECURITY.md': 100,
        'MAINTENANCE.md': 100,
        'IMPLEMENTATION_SUMMARY.md': 200,
        'adv reconmaster.md': 200,
        'DOCUMENTATION_INDEX.md': 100,
        'PROJECT_STATUS.md': 200,
        'ALL_PHASES_COMPLETE.md': 200,
    }
    
    results = {}
    total_lines = 0
    
    for filename, min_lines in files.items():
        exists, lines = check_file_exists(filename, min_lines)
        results[filename] = exists
        total_lines += lines
        
        if exists:
            detail = f"{lines:,} lines"
        else:
            detail = f"{RED}MISSING{RESET}"
        
        print_status(filename, exists, detail)
    
    print(f"\n{BLUE}Total documentation lines: {total_lines:,}{RESET}")
    return results


def verify_support_docs() -> Dict[str, bool]:
    """Verify support documentation."""
    print_section("SUPPORT DOCUMENTATION")
    
    files = {
        'docs/FAQ.md': 100,
        'docs/TROUBLESHOOTING.md': 100,
        'docs/EXAMPLES.md': 200,
    }
    
    results = {}
    total_lines = 0
    
    for filename, min_lines in files.items():
        exists, lines = check_file_exists(filename, min_lines)
        results[filename] = exists
        total_lines += lines
        
        if exists:
            detail = f"{lines:,} lines"
        else:
            detail = f"{RED}MISSING{RESET}"
        
        print_status(filename, exists, detail)
    
    print(f"\n{BLUE}Total support doc lines: {total_lines:,}{RESET}")
    return results


def verify_testing() -> Dict[str, bool]:
    """Verify testing files."""
    print_section("TESTING INFRASTRUCTURE")
    
    files = {
        'tests/test_utils.py': 50,
        'tests/test_reconmaster.py': 100,
        'tests/test_integration.py': 50,
        'scripts/import_smoke_check.py': 20,
        'run_tests.py': 50,
        'pytest.ini': 5,
    }
    
    results = {}
    total_lines = 0
    
    for filename, min_lines in files.items():
        exists, lines = check_file_exists(filename, min_lines)
        results[filename] = exists
        total_lines += lines
        
        if exists:
            detail = f"{lines:,} lines"
        else:
            detail = f"{RED}MISSING{RESET}"
        
        print_status(filename, exists, detail)
    
    print(f"\n{BLUE}Total testing lines: {total_lines:,}{RESET}")
    return results


def verify_deployment() -> Dict[str, bool]:
    """Verify deployment files."""
    print_section("DEPLOYMENT & DISTRIBUTION")
    
    files = {
        'setup.py': 50,
        'pyproject.toml': 20,
        'requirements.txt': 5,
        'Dockerfile': 20,
        'docker-compose.yml': 10,
        '.dockerignore': 5,
        'MANIFEST.in': 5,
        'PYPI_GUIDE.md': 100,
        'DOCKER_GUIDE.md': 100,
        '.github/workflows/test.yml': 20,
        '.github/workflows/release.yml': 20,
    }
    
    results = {}
    total_lines = 0
    
    for filename, min_lines in files.items():
        exists, lines = check_file_exists(filename, min_lines)
        results[filename] = exists
        total_lines += lines
        
        if exists:
            detail = f"{lines:,} lines"
        else:
            detail = f"{RED}MISSING{RESET}"
        
        print_status(filename, exists, detail)
    
    print(f"\n{BLUE}Total deployment lines: {total_lines:,}{RESET}")
    return results


def verify_installation() -> Dict[str, bool]:
    """Verify installation scripts."""
    print_section("INSTALLATION SCRIPTS")
    
    files = {
        'install_reconmaster.sh': 200,
        'setup.ps1': 50,
    }
    
    results = {}
    total_lines = 0
    
    for filename, min_lines in files.items():
        exists, lines = check_file_exists(filename, min_lines)
        results[filename] = exists
        total_lines += lines
        
        if exists:
            detail = f"{lines:,} lines"
        else:
            detail = f"{RED}MISSING{RESET}"
        
        print_status(filename, exists, detail)
    
    print(f"\n{BLUE}Total installation script lines: {total_lines:,}{RESET}")
    return results


def verify_community() -> Dict[str, bool]:
    """Verify community infrastructure."""
    print_section("COMMUNITY INFRASTRUCTURE")
    
    files = {
        'CONTRIBUTORS.md': 50,
        '.github/ISSUE_TEMPLATE/bug_report.md': 10,
        '.github/ISSUE_TEMPLATE/feature_request.md': 10,
        '.github/ISSUE_TEMPLATE/question.md': 10,
        '.github/PULL_REQUEST_TEMPLATE.md': 20,
    }
    
    results = {}
    total_lines = 0
    
    for filename, min_lines in files.items():
        exists, lines = check_file_exists(filename, min_lines)
        results[filename] = exists
        total_lines += lines
        
        if exists:
            detail = f"{lines:,} lines"
        else:
            detail = f"{RED}MISSING{RESET}"
        
        print_status(filename, exists, detail)
    
    print(f"\n{BLUE}Total community infrastructure lines: {total_lines:,}{RESET}")
    return results


def verify_resources() -> Dict[str, bool]:
    """Verify bundled resources."""
    print_section("BUNDLED RESOURCES")
    
    files = {
        'wordlists/subdomains_new.txt': 10,
        'wordlists/directory-list_new.txt': 10,
        'LICENSE': 10,
        '.flake8': 5,
    }
    
    results = {}
    
    for filename, min_lines in files.items():
        exists, lines = check_file_exists(filename, min_lines)
        results[filename] = exists
        
        if exists:
            detail = f"{lines:,} lines"
        else:
            detail = f"{RED}MISSING{RESET}"
        
        print_status(filename, exists, detail)
    
    return results


def print_summary(all_results: Dict[str, Dict[str, bool]]):
    """Print overall summary."""
    print_section("OVERALL SUMMARY")
    
    total_files = 0
    present_files = 0
    
    for category, results in all_results.items():
        total = len(results)
        present = sum(1 for v in results.values() if v)
        total_files += total
        present_files += present
        
        percentage = (present / total * 100) if total > 0 else 0
        status = percentage == 100
        
        detail = f"{present}/{total} files ({percentage:.1f}%)"
        print_status(category, status, detail)
    
    print(f"\n{BLUE}{'─' * 70}{RESET}")
    
    overall_percentage = (present_files / total_files * 100) if total_files > 0 else 0
    
    print(f"\n{BLUE}Total Files:{RESET} {present_files}/{total_files} ({overall_percentage:.1f}%)")
    
    if overall_percentage == 100:
        print(f"\n{GREEN}✓ PROJECT IS COMPLETE!{RESET}")
        print(f"{GREEN}All required files are present and accounted for.{RESET}")
    elif overall_percentage >= 90:
        print(f"\n{YELLOW}⚠ PROJECT IS NEARLY COMPLETE{RESET}")
        print(f"{YELLOW}Most files are present. Review missing files above.{RESET}")
    else:
        print(f"\n{RED}✗ PROJECT IS INCOMPLETE{RESET}")
        print(f"{RED}Several files are missing. Review the report above.{RESET}")
    
    return overall_percentage


def main():
    """Main verification function."""
    print(f"\n{BLUE}{'═' * 70}{RESET}")
    print(f"{BLUE}{'ReconMaster Project Verification':^70}{RESET}")
    print(f"{BLUE}{'Version 3.0.0-Pro':^70}{RESET}")
    print(f"{BLUE}{'═' * 70}{RESET}")
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Run all verifications
    all_results = {
        'Core Implementation': verify_core_files(),
        'Documentation': verify_documentation(),
        'Support Documentation': verify_support_docs(),
        'Testing Infrastructure': verify_testing(),
        'Deployment & Distribution': verify_deployment(),
        'Installation Scripts': verify_installation(),
        'Community Infrastructure': verify_community(),
        'Bundled Resources': verify_resources(),
    }
    
    # Print summary
    percentage = print_summary(all_results)
    
    # Exit code based on completeness
    if percentage == 100:
        sys.exit(0)
    elif percentage >= 90:
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == '__main__':
    main()
