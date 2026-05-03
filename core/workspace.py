from pathlib import Path

class WorkspaceManager:
    APP_NAME = "StellAlign"
    
    @classmethod
    def get_workspace_dir(cls) -> Path:
        # Resolves to C:\Users\Username\Documents\StellAlign on Windows
        return Path.home() / "Documents" / cls.APP_NAME
        
    @classmethod
    def get_profiles_dir(cls) -> Path:
        return cls.get_workspace_dir() / "profiles"
        
    @classmethod
    def get_screenshots_dir(cls) -> Path:
        return cls.get_workspace_dir() / "screenshots"
        
    @classmethod
    def init_workspace(cls):
        cls.get_profiles_dir().mkdir(parents=True, exist_ok=True)
        cls.get_screenshots_dir().mkdir(parents=True, exist_ok=True)