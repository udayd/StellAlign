import json
import dataclasses
from pathlib import Path
from core.state import CollimationState, CircleState
from core.workspace import WorkspaceManager

class ProfileManager:
    @staticmethod
    def get_available_profiles() -> list[str]:
        profiles_dir = WorkspaceManager.get_profiles_dir()
        # Return just the filenames without the .json extension
        return [p.stem for p in profiles_dir.glob("*.json")]

    @staticmethod
    def save_profile(state: CollimationState, profile_name: str):
        filepath = WorkspaceManager.get_profiles_dir() / f"{profile_name}.json"
        with open(filepath, 'w') as f:
            json.dump(dataclasses.asdict(state), f, indent=4)

    @staticmethod
    def load_profile(state: CollimationState, profile_name: str):
        filepath = WorkspaceManager.get_profiles_dir() / f"{profile_name}.json"
        if not filepath.exists():
            return
        with open(filepath, 'r') as f:
            data = json.load(f)
            for key, value in data.items():
                if key == 'circles':
                    # Rebuild the list of CircleState objects
                    state.circles = [CircleState(**c) for c in value]
                elif hasattr(state, key):
                    setattr(state, key, value)

    @staticmethod
    def delete_profile(profile_name: str):
        filepath = WorkspaceManager.get_profiles_dir() / f"{profile_name}.json"
        if filepath.exists():
            filepath.unlink()

    @staticmethod
    def save_global_settings(state: CollimationState):
        filepath = WorkspaceManager.get_workspace_dir() / "settings.json"
        with open(filepath, 'w') as f:
            json.dump(dataclasses.asdict(state), f, indent=4)

    @staticmethod
    def load_global_settings(state: CollimationState):
        filepath = WorkspaceManager.get_workspace_dir() / "settings.json"
        if not filepath.exists():
            return
        with open(filepath, 'r') as f:
            data = json.load(f)
            for key, value in data.items():
                if key == 'circles':
                    state.circles = [CircleState(**c) for c in value]
                elif hasattr(state, key):
                    setattr(state, key, value)
                    
        if not state.remember_hardware:
            state.camera_index = 0
            state.resolution_width = 640
            state.resolution_height = 480