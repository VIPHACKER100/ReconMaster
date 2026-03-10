import os
import sys
import yaml
import logging
import re
from typing import Dict, Any

logger = logging.getLogger("ReconMaster.Config")

class Config:
    """Configuration parser and validator for ReconMaster."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self._data: Dict[str, Any] = {}
        self.load()

    def load(self):
        """Load and validate the YAML configuration."""
        if not os.path.exists(self.config_path):
            self._create_default_config()
            logger.info(f"Created default configuration at {self.config_path}")
            
        try:
            with open(self.config_path, 'r') as f:
                self._data = yaml.safe_load(f) or {}
            self._validate()
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse config.yaml: {e}")
            sys.exit(1)
        except ValueError as e:
            logger.error(f"Configuration Validation Error: {e}")
            sys.exit(1)

    def _validate(self):
        """Validate critical configuration parameters."""
        scan_cfg = self._data.get("scan", {})
        
        # Threads validation
        threads = scan_cfg.get("threads", 10)
        if not isinstance(threads, int) or not (1 <= threads <= 100):
            raise ValueError(f"scan.threads must be an integer between 1 and 100. Got: {threads}")
            
        # Timeout validation
        timeout = scan_cfg.get("timeout", 300)
        if not isinstance(timeout, int) or timeout <= 0:
            raise ValueError(f"scan.timeout must be a positive integer. Got: {timeout}")

        # API Key Validation (Format checks only, no hardcoded secrets)
        api_cfg = self._data.get("api_keys", {})
        censys_id = api_cfg.get("censys_id", "")
        if censys_id and not isinstance(censys_id, str):
             raise ValueError("API Keys must be strings.")

    def get(self, key_path: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation (e.g., 'scan.threads')."""
        keys = key_path.split('.')
        current = self._data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current

    def _create_default_config(self):
        """Generate a default configuration file."""
        default_config = '''# ReconMaster Configuration File

scan:
  threads: 10
  timeout: 300
  verify_ssl: true

api_keys:
  # Do not commit real keys to version control!
  censys_id: ""
  censys_secret: ""
  securitytrails: ""
  virustotal: ""
'''
        with open(self.config_path, 'w') as f:
            f.write(default_config)
