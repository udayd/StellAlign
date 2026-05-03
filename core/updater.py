import json
import urllib.request
from PyQt6.QtCore import QThread, pyqtSignal

class UpdateChecker(QThread):
    update_available = pyqtSignal(str, str) # Emits (version_name, release_url)
    
    def __init__(self, current_version):
        super().__init__()
        self.current_version = current_version
        
    def run(self):
        try:
            url = "https://api.github.com/repos/udayd/StellAlign/releases/latest"
            # GitHub API requires a User-Agent header
            req = urllib.request.Request(url, headers={'User-Agent': 'StellAlign-App'})
            
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                latest_version = data.get("tag_name", "")
                release_url = data.get("html_url", "")
                
                if latest_version and latest_version != self.current_version:
                    self.update_available.emit(latest_version, release_url)
        except Exception:
            pass # If there is no internet connection or GitHub is down, fail silently