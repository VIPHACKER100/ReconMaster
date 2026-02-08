#!/usr/bin/env python3
"""
ReconMaster WordPress Scanner Plugin
Version: 1.0.0
Author: VIPHACKER100

This plugin detects WordPress installations and enumerates plugins, themes, and users.
"""

import asyncio
import aiohttp
import re
from typing import Dict, List, Optional
from urllib.parse import urljoin

class WordPressPlugin:
    """WordPress vulnerability scanner plugin"""
    
    def __init__(self):
        self.name = "wordpress-scanner"
        self.version = "1.0.0"
        self.description = "WordPress detection and enumeration"
        self.author = "VIPHACKER100"
    
    @property
    def metadata(self) -> Dict:
        """Return plugin metadata"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "enabled": True
        }
    
    async def execute(self, target: str, **kwargs) -> Dict:
        """
        Execute WordPress scanning
        
        Args:
            target: Target URL to scan
            **kwargs: Additional arguments
        
        Returns:
            Dictionary containing scan results
        """
        results = {
            "target": target,
            "is_wordpress": False,
            "version": None,
            "plugins": [],
            "themes": [],
            "users": [],
            "vulnerabilities": []
        }
        
        # Detect WordPress
        is_wp, version = await self.detect_wordpress(target)
        results["is_wordpress"] = is_wp
        results["version"] = version
        
        if not is_wp:
            return results
        
        # Enumerate components
        results["plugins"] = await self.enumerate_plugins(target)
        results["themes"] = await self.enumerate_themes(target)
        results["users"] = await self.enumerate_users(target)
        
        # Check for vulnerabilities
        results["vulnerabilities"] = await self.check_vulnerabilities(
            version, results["plugins"], results["themes"]
        )
        
        return results
    
    async def detect_wordpress(self, target: str) -> tuple:
        """
        Detect if target is running WordPress
        
        Returns:
            Tuple of (is_wordpress: bool, version: str)
        """
        indicators = [
            "/wp-content/",
            "/wp-includes/",
            "/wp-admin/",
            "/wp-login.php"
        ]
        
        try:
            async with aiohttp.ClientSession() as session:
                # Check common WordPress paths
                for indicator in indicators:
                    url = urljoin(target, indicator)
                    async with session.get(url, timeout=10, allow_redirects=False) as response:
                        if response.status == 200 or response.status == 403:
                            # Try to get version
                            version = await self._get_version(session, target)
                            return True, version
                
                # Check meta generator tag
                async with session.get(target, timeout=10) as response:
                    if response.status == 200:
                        html = await response.text()
                        if 'wp-content' in html or 'WordPress' in html:
                            version = await self._get_version(session, target)
                            return True, version
        
        except Exception as e:
            print(f"Error detecting WordPress: {e}")
        
        return False, None
    
    async def _get_version(self, session: aiohttp.ClientSession, target: str) -> Optional[str]:
        """Extract WordPress version"""
        try:
            # Check readme.html
            readme_url = urljoin(target, "/readme.html")
            async with session.get(readme_url, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    match = re.search(r'Version (\d+\.\d+\.?\d*)', html)
                    if match:
                        return match.group(1)
            
            # Check meta generator
            async with session.get(target, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    match = re.search(r'<meta name="generator" content="WordPress (\d+\.\d+\.?\d*)"', html)
                    if match:
                        return match.group(1)
        
        except Exception:
            pass
        
        return "Unknown"
    
    async def enumerate_plugins(self, target: str) -> List[Dict]:
        """Enumerate WordPress plugins"""
        plugins = []
        common_plugins = [
            "akismet", "jetpack", "wordfence", "yoast-seo", "contact-form-7",
            "elementor", "woocommerce", "all-in-one-seo-pack", "google-analytics",
            "wp-super-cache", "wpforms-lite", "duplicate-post"
        ]
        
        try:
            async with aiohttp.ClientSession() as session:
                tasks = []
                for plugin in common_plugins:
                    url = urljoin(target, f"/wp-content/plugins/{plugin}/")
                    tasks.append(self._check_plugin(session, url, plugin))
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                plugins = [r for r in results if r and not isinstance(r, Exception)]
        
        except Exception as e:
            print(f"Error enumerating plugins: {e}")
        
        return plugins
    
    async def _check_plugin(self, session: aiohttp.ClientSession, url: str, name: str) -> Optional[Dict]:
        """Check if a plugin exists"""
        try:
            async with session.get(url, timeout=5, allow_redirects=False) as response:
                if response.status in [200, 403]:
                    # Try to get version from readme
                    readme_url = urljoin(url, "readme.txt")
                    version = await self._get_plugin_version(session, readme_url)
                    
                    return {
                        "name": name,
                        "url": url,
                        "version": version
                    }
        except Exception:
            pass
        
        return None
    
    async def _get_plugin_version(self, session: aiohttp.ClientSession, readme_url: str) -> str:
        """Extract plugin version from readme"""
        try:
            async with session.get(readme_url, timeout=5) as response:
                if response.status == 200:
                    text = await response.text()
                    match = re.search(r'Stable tag: (\d+\.\d+\.?\d*)', text)
                    if match:
                        return match.group(1)
        except Exception:
            pass
        
        return "Unknown"
    
    async def enumerate_themes(self, target: str) -> List[Dict]:
        """Enumerate WordPress themes"""
        themes = []
        common_themes = [
            "twentytwentythree", "twentytwentytwo", "twentytwentyone",
            "twentytwenty", "twentynineteen", "astra", "oceanwp", "generatepress"
        ]
        
        try:
            async with aiohttp.ClientSession() as session:
                tasks = []
                for theme in common_themes:
                    url = urljoin(target, f"/wp-content/themes/{theme}/")
                    tasks.append(self._check_theme(session, url, theme))
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                themes = [r for r in results if r and not isinstance(r, Exception)]
        
        except Exception as e:
            print(f"Error enumerating themes: {e}")
        
        return themes
    
    async def _check_theme(self, session: aiohttp.ClientSession, url: str, name: str) -> Optional[Dict]:
        """Check if a theme exists"""
        try:
            async with session.get(url, timeout=5, allow_redirects=False) as response:
                if response.status in [200, 403]:
                    return {
                        "name": name,
                        "url": url
                    }
        except Exception:
            pass
        
        return None
    
    async def enumerate_users(self, target: str) -> List[str]:
        """Enumerate WordPress users"""
        users = []
        
        try:
            async with aiohttp.ClientSession() as session:
                # Try REST API endpoint
                api_url = urljoin(target, "/wp-json/wp/v2/users")
                async with session.get(api_url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        users = [user.get('name', user.get('slug', 'unknown')) for user in data]
                        return users
                
                # Try author archive enumeration
                for user_id in range(1, 11):
                    url = urljoin(target, f"/?author={user_id}")
                    async with session.get(url, timeout=5, allow_redirects=True) as response:
                        if response.status == 200:
                            # Extract username from URL or content
                            final_url = str(response.url)
                            match = re.search(r'/author/([^/]+)', final_url)
                            if match:
                                username = match.group(1)
                                if username not in users:
                                    users.append(username)
        
        except Exception as e:
            print(f"Error enumerating users: {e}")
        
        return users
    
    async def check_vulnerabilities(self, version: str, plugins: List[Dict], themes: List[Dict]) -> List[Dict]:
        """
        Check for known vulnerabilities
        
        This is a placeholder - in production, you would query a vulnerability database
        """
        vulnerabilities = []
        
        # Example vulnerability checks
        if version and version != "Unknown":
            try:
                major_version = float(version.split('.')[0] + '.' + version.split('.')[1])
                if major_version < 6.0:
                    vulnerabilities.append({
                        "type": "outdated_version",
                        "severity": "high",
                        "component": f"WordPress {version}",
                        "description": "WordPress version is outdated and may contain vulnerabilities",
                        "recommendation": "Update to the latest WordPress version"
                    })
            except Exception:
                pass
        
        # Check for vulnerable plugins (example)
        for plugin in plugins:
            if plugin['version'] == "Unknown":
                vulnerabilities.append({
                    "type": "unknown_version",
                    "severity": "medium",
                    "component": f"Plugin: {plugin['name']}",
                    "description": "Plugin version could not be determined",
                    "recommendation": "Manually verify plugin version and update if necessary"
                })
        
        return vulnerabilities

# Plugin entry point
def get_plugin():
    """Return plugin instance"""
    return WordPressPlugin()

# For testing
if __name__ == "__main__":
    async def test():
        plugin = WordPressPlugin()
        results = await plugin.execute("https://example.com")
        print(results)
    
    asyncio.run(test())
