import asyncio
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import os
import json
from reconmaster import ReconMaster

class TestReconExtensions(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.target = "example.com"
        self.output_dir = "./test_results"
        self.recon = ReconMaster(self.target, self.output_dir)
        self.recon._setup_dirs()

    def tearDown(self):
        import shutil
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

    @patch('reconmaster.ReconMaster._run_command', new_callable=AsyncMock)
    async def test_check_takeovers(self, mock_run):
        # Simulate live domain discovery
        self.recon.live_domains.add("sub.example.com")
        
        # Mock nuclei finding a takeover
        takeover_file = self.recon.files["takeovers"]
        with open(takeover_file, "w") as f:
            f.write("[takeover-template] http://sub.example.com\n")
        
        await self.recon.check_takeovers()
        
        self.assertTrue(any("Potential Subdomain Takeover" in v["info"]["name"] for v in self.recon.vulns))
        self.assertIn("[takeover-template] http://sub.example.com", self.recon.takeovers)

    @patch('aiohttp.ClientSession.head', new_callable=AsyncMock)
    async def test_check_broken_links(self, mock_head):
        # Mock a 404 response for a social link
        mock_resp = MagicMock()
        mock_resp.status = 404
        mock_head.return_value.__aenter__.return_value = mock_resp
        
        self.recon.urls.add("https://twitter.com/dead_account")
        
        await self.recon.check_broken_links()
        
        self.assertTrue(any("Broken Social Link Hijack" in v["info"]["name"] for v in self.recon.vulns))
        self.assertIn("https://twitter.com/dead_account", self.recon.broken_links)

if __name__ == "__main__":
    unittest.main()
