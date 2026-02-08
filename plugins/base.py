class ReconPlugin:
    """Base class for all ReconMaster plugins"""
    name = "BasePlugin"
    description = "A base plugin template"

    async def run(self, recon):
        """Main execution point for the plugin"""
        raise NotImplementedError
