from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QInputDialog, QMessageBox
from PyQt6.QtCore import pyqtSignal, QUrl
from PyQt6.QtGui import QIcon, QDesktopServices
from core.workspace import WorkspaceManager
from core.profiles import ProfileManager
from ui.styles import ROW_SPACING, SECTION_MARGINS

class WorkspaceWidget(QGroupBox):
    screenshot_requested = pyqtSignal()
    
    def __init__(self, panel, state):
        super().__init__("Workspace")
        self.panel = panel
        self.state = state
        
        workspace_layout = QVBoxLayout()
        workspace_layout.setSpacing(ROW_SPACING)
        workspace_layout.setContentsMargins(*SECTION_MARGINS)
        
        profile_row = QHBoxLayout()
        profile_row.setContentsMargins(0, 0, 0, 0)
        
        self.combo_profiles = QComboBox()
        self.combo_profiles.currentIndexChanged.connect(self.on_profile_selected)
        profile_row.addWidget(self.combo_profiles)
        
        self.btn_open_folder = QPushButton()
        self.btn_open_folder.setIcon(QIcon('assets/icons/folder.svg'))
        self.btn_open_folder.setToolTip("Open Screenshots Folder")
        self.btn_open_folder.setFixedSize(28, 28)
        self.btn_open_folder.clicked.connect(self.on_open_folder)
        profile_row.addWidget(self.btn_open_folder)
        
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        
        self.btn_save = QPushButton()
        self.btn_save.setIcon(QIcon('assets/icons/plus.svg'))
        self.btn_save.setToolTip("Save Current Settings as New Profile")
        self.btn_save.clicked.connect(self.on_save_profile)
        
        self.btn_update = QPushButton()
        self.btn_update.setIcon(QIcon('assets/icons/save.svg'))
        self.btn_update.setToolTip("Update Selected Profile")
        self.btn_update.clicked.connect(self.on_update_profile)
        
        self.btn_delete = QPushButton()
        self.btn_delete.setIcon(QIcon('assets/icons/trash.svg'))
        self.btn_delete.setToolTip("Delete Selected Profile")
        self.btn_delete.clicked.connect(self.on_delete_profile)
        
        self.btn_screenshot = QPushButton()
        self.btn_screenshot.setIcon(QIcon('assets/icons/camera.svg'))
        self.btn_screenshot.setToolTip("Take Screenshot")
        self.btn_screenshot.clicked.connect(self.screenshot_requested.emit)
        
        self.refresh_profiles()
        
        toolbar_layout.addWidget(self.btn_save)
        toolbar_layout.addWidget(self.btn_update)
        toolbar_layout.addWidget(self.btn_delete)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.btn_screenshot)
        
        workspace_layout.addLayout(profile_row)
        workspace_layout.addLayout(toolbar_layout)
        self.setLayout(workspace_layout)

    def refresh_profiles(self):
        self.combo_profiles.blockSignals(True)
        self.combo_profiles.clear()
        self.combo_profiles.addItem("-- Select Profile --")
        self.combo_profiles.addItems(ProfileManager.get_available_profiles())
        self.combo_profiles.blockSignals(False)
        self.btn_update.setEnabled(False); self.btn_update.setIcon(QIcon('assets/icons/save-disabled.svg'))
        self.btn_delete.setEnabled(False); self.btn_delete.setIcon(QIcon('assets/icons/trash-disabled.svg'))

    def on_save_profile(self):
        name, ok = QInputDialog.getText(self, "Save Profile", "Enter profile name (e.g., 8-inch Dob):")
        if ok and name:
            ProfileManager.save_profile(self.state, name.strip())
            self.refresh_profiles()
            index = self.combo_profiles.findText(name.strip())
            if index >= 0: self.combo_profiles.setCurrentIndex(index)
            self.panel.show_notification(f"Profile '{name.strip()}' saved.")

    def on_open_folder(self):
        path = str(WorkspaceManager.get_screenshots_dir())
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def on_profile_selected(self, index):
        if index > 0:
            profile_name = self.combo_profiles.currentText()
            ProfileManager.load_profile(self.state, profile_name)
            self.panel.sync_ui_to_state()
            self.btn_update.setEnabled(True); self.btn_update.setIcon(QIcon('assets/icons/save.svg'))
            self.btn_delete.setEnabled(True); self.btn_delete.setIcon(QIcon('assets/icons/trash.svg'))
        else:
            self.btn_update.setEnabled(False); self.btn_update.setIcon(QIcon('assets/icons/save-disabled.svg'))
            self.btn_delete.setEnabled(False); self.btn_delete.setIcon(QIcon('assets/icons/trash-disabled.svg'))

    def on_update_profile(self):
        if self.combo_profiles.currentIndex() > 0:
            profile_name = self.combo_profiles.currentText()
            ProfileManager.save_profile(self.state, profile_name)
            self.panel.show_notification(f"Profile '{profile_name}' updated.")

    def on_delete_profile(self):
        if self.combo_profiles.currentIndex() > 0:
            profile_name = self.combo_profiles.currentText()
            reply = QMessageBox.question(self, 'Delete Profile', f"Are you sure you want to delete '{profile_name}'?", 
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                ProfileManager.delete_profile(profile_name)
                self.refresh_profiles()