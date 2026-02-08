#!/usr/bin/env python3
"""
ReconMaster Configuration Migration Script
Version: 3.1.0
Author: VIPHACKER100

This script migrates configuration and data from ReconMaster v1.x/v2.x to v3.x
"""

import json
import os
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime
import yaml

# Colors for output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_banner():
    """Display migration script banner"""
    print(f"{Colors.BLUE}")
    print("""
╦═╗╔═╗╔═╗╔═╗╔╗╔╔╦╗╔═╗╔═╗╔╦╗╔═╗╦═╗
╠╦╝║╣ ║  ║ ║║║║║║║╠═╣╚═╗ ║ ║╣ ╠╦╝
╩╚═╚═╝╚═╝╚═╝╝╚╝╩ ╩╩ ╩╚═╝ ╩ ╚═╝╩╚═
   Migration Script v1.x → v3.x
    """)
    print(f"{Colors.ENDC}")

def backup_old_config(old_path):
    """Create backup of old configuration"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{old_path}.backup_{timestamp}"
    
    try:
        if os.path.isfile(old_path):
            shutil.copy2(old_path, backup_path)
        elif os.path.isdir(old_path):
            shutil.copytree(old_path, backup_path)
        
        print(f"{Colors.GREEN}✓ Backup created: {backup_path}{Colors.ENDC}")
        return backup_path
    except Exception as e:
        print(f"{Colors.RED}✗ Failed to create backup: {e}{Colors.ENDC}")
        return None

def migrate_v1_config(old_config_path):
    """Migrate v1.x configuration to v3.x format"""
    print(f"{Colors.BLUE}[*] Migrating v1.x configuration...{Colors.ENDC}")
    
    # v1.x used simple JSON or no config file
    # Create new v3.x config with defaults
    new_config = {
        'targets': {
            'domains': [],
            'scope': [],
            'exclusions': []
        },
        'scan': {
            'passive_only': False,
            'aggressive': False,
            'rate_limit': 50,
            'timeout': 30,
            'retries': 3,
            'delay': 1
        },
        'modules': {
            'subdomain': {'enabled': True, 'sources': ['subfinder', 'assetfinder']},
            'dns': {'enabled': True, 'validate': True},
            'http': {'enabled': True, 'screenshot': False},
            'vuln': {'enabled': False},
            'endpoint': {'enabled': False}
        },
        'output': {
            'directory': './recon_results',
            'formats': ['json', 'md'],
            'verbose': True,
            'save_logs': True
        }
    }
    
    # Try to read old config if exists
    if os.path.exists(old_config_path):
        try:
            with open(old_config_path, 'r') as f:
                old_config = json.load(f)
            
            # Map old config to new format
            if 'target' in old_config:
                new_config['targets']['domains'] = [old_config['target']]
            
            if 'output_dir' in old_config:
                new_config['output']['directory'] = old_config['output_dir']
            
            print(f"{Colors.GREEN}✓ Old configuration parsed{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.YELLOW}⚠ Could not parse old config: {e}{Colors.ENDC}")
    
    return new_config

def migrate_v2_config(old_config_path):
    """Migrate v2.x configuration to v3.x format"""
    print(f"{Colors.BLUE}[*] Migrating v2.x configuration...{Colors.ENDC}")
    
    new_config = {
        'targets': {
            'domains': [],
            'scope': ['*'],
            'exclusions': []
        },
        'scan': {
            'passive_only': False,
            'aggressive': False,
            'rate_limit': 50,
            'timeout': 30,
            'retries': 3,
            'delay': 1,
            'max_concurrent': 50
        },
        'modules': {
            'subdomain': {
                'enabled': True,
                'sources': ['subfinder', 'assetfinder', 'amass'],
                'wordlist': None
            },
            'dns': {
                'enabled': True,
                'validate': True
            },
            'http': {
                'enabled': True,
                'screenshot': True,
                'tech_detect': True
            },
            'vuln': {
                'enabled': True,
                'severity': ['critical', 'high', 'medium']
            },
            'endpoint': {
                'enabled': True,
                'crawl_depth': 3
            }
        },
        'notifications': {
            'discord': {'enabled': False, 'webhook': ''},
            'slack': {'enabled': False, 'webhook': ''}
        },
        'output': {
            'directory': './recon_results',
            'formats': ['json', 'md', 'html'],
            'verbose': True,
            'save_logs': True
        },
        'advanced': {
            'circuit_breaker': {'enabled': True, 'threshold': 5, 'timeout': 300},
            'cache': {'enabled': True, 'ttl': 3600},
            'plugins': {'enabled': True, 'auto_load': True}
        }
    }
    
    # Try to read v2 config
    if os.path.exists(old_config_path):
        try:
            with open(old_config_path, 'r') as f:
                if old_config_path.endswith('.yaml') or old_config_path.endswith('.yml'):
                    old_config = yaml.safe_load(f)
                else:
                    old_config = json.load(f)
            
            # Merge old config with new structure
            if 'targets' in old_config:
                new_config['targets'].update(old_config['targets'])
            
            if 'scan' in old_config:
                new_config['scan'].update(old_config['scan'])
            
            if 'modules' in old_config:
                for module, settings in old_config['modules'].items():
                    if module in new_config['modules']:
                        new_config['modules'][module].update(settings)
            
            if 'output' in old_config:
                new_config['output'].update(old_config['output'])
            
            print(f"{Colors.GREEN}✓ v2.x configuration migrated{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.YELLOW}⚠ Could not parse v2 config: {e}{Colors.ENDC}")
    
    return new_config

def migrate_results(old_results_dir, new_results_dir):
    """Migrate old scan results to new structure"""
    print(f"{Colors.BLUE}[*] Migrating scan results...{Colors.ENDC}")
    
    if not os.path.exists(old_results_dir):
        print(f"{Colors.YELLOW}⚠ No old results found{Colors.ENDC}")
        return
    
    try:
        # Create new results directory
        os.makedirs(new_results_dir, exist_ok=True)
        
        # Copy old results
        for item in os.listdir(old_results_dir):
            old_path = os.path.join(old_results_dir, item)
            new_path = os.path.join(new_results_dir, item)
            
            if os.path.isdir(old_path):
                shutil.copytree(old_path, new_path, dirs_exist_ok=True)
            else:
                shutil.copy2(old_path, new_path)
        
        print(f"{Colors.GREEN}✓ Results migrated to {new_results_dir}{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.RED}✗ Failed to migrate results: {e}{Colors.ENDC}")

def save_new_config(config, output_path):
    """Save new configuration to YAML file"""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        print(f"{Colors.GREEN}✓ New configuration saved: {output_path}{Colors.ENDC}")
        return True
    except Exception as e:
        print(f"{Colors.RED}✗ Failed to save config: {e}{Colors.ENDC}")
        return False

def main():
    """Main migration function"""
    parser = argparse.ArgumentParser(
        description='Migrate ReconMaster configuration from v1.x/v2.x to v3.x'
    )
    parser.add_argument(
        '--version',
        choices=['v1', 'v2'],
        required=True,
        help='Source version to migrate from'
    )
    parser.add_argument(
        '--config',
        default='config.json',
        help='Path to old configuration file'
    )
    parser.add_argument(
        '--output',
        default='config/config.yaml',
        help='Path for new configuration file'
    )
    parser.add_argument(
        '--results',
        default='recon_results',
        help='Path to old results directory'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip creating backups'
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    print(f"{Colors.CYAN}Migration Settings:{Colors.ENDC}")
    print(f"  Source Version: {args.version}")
    print(f"  Old Config: {args.config}")
    print(f"  New Config: {args.output}")
    print(f"  Results Dir: {args.results}")
    print()
    
    # Create backups
    if not args.no_backup:
        if os.path.exists(args.config):
            backup_old_config(args.config)
        if os.path.exists(args.results):
            backup_old_config(args.results)
    
    # Migrate configuration
    if args.version == 'v1':
        new_config = migrate_v1_config(args.config)
    else:
        new_config = migrate_v2_config(args.config)
    
    # Save new configuration
    if save_new_config(new_config, args.output):
        print(f"\n{Colors.GREEN}✓ Migration completed successfully!{Colors.ENDC}")
        print(f"\n{Colors.CYAN}Next Steps:{Colors.ENDC}")
        print(f"1. Review the new configuration: {args.output}")
        print(f"2. Update your targets and settings as needed")
        print(f"3. Run ReconMaster with: python reconmaster.py --config {args.output}")
        print(f"\n{Colors.YELLOW}Note: Some features may require manual configuration{Colors.ENDC}")
    else:
        print(f"\n{Colors.RED}✗ Migration failed{Colors.ENDC}")
        sys.exit(1)

if __name__ == '__main__':
    main()
