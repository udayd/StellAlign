from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox
from PyQt6.QtCore import Qt
from core.state import CollimationState, CircleState
from ui.styles import ROW_SPACING

class GuidedWizard(QWidget):
    def __init__(self, state: CollimationState, panel):
        super().__init__()
        self.state = state
        self.panel = panel
        self.current_step = 0
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(ROW_SPACING)
        
        # Step Setup / Scope Selector
        self.setup_layout = QHBoxLayout()
        self.setup_layout.addWidget(QLabel("Telescope Type:"))
        self.combo_scope = QComboBox()
        self.combo_scope.addItems(["Newtonian", "SCT / Mak"])
        self.setup_layout.addWidget(self.combo_scope)
        self.btn_start = QPushButton("Start Assistant")
        self.btn_start.clicked.connect(self.start_wizard)
        self.setup_layout.addWidget(self.btn_start)
        
        # Wizard Navigation
        self.nav_layout = QHBoxLayout()
        self.btn_back = QPushButton("< Back")
        self.btn_back.clicked.connect(self.prev_step)
        self.lbl_step = QLabel("Step 1/4")
        self.lbl_step.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_step.setStyleSheet("font-weight: bold; color: #4CAF50;")
        self.btn_next = QPushButton("Next >")
        self.btn_next.clicked.connect(self.next_step)
        
        self.nav_layout.addWidget(self.btn_back)
        self.nav_layout.addWidget(self.lbl_step)
        self.nav_layout.addWidget(self.btn_next)
        
        # Instruction Label
        self.lbl_instruction = QLabel("")
        self.lbl_instruction.setWordWrap(True)
        self.lbl_instruction.setStyleSheet("background-color: #1e1e1e; padding: 12px; border-radius: 6px; border: 1px solid #4CAF50;")
        self.lbl_instruction.setMinimumHeight(100)
        self.lbl_instruction.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.nav_container = QWidget()
        nav_vbox = QVBoxLayout(self.nav_container)
        nav_vbox.setContentsMargins(0, 0, 0, 0)
        nav_vbox.addLayout(self.nav_layout)
        nav_vbox.addWidget(self.lbl_instruction)
        
        layout.addLayout(self.setup_layout)
        layout.addWidget(self.nav_container)
        
        self.nav_container.hide()

    def start_wizard(self):
        scope = self.combo_scope.currentText()
        self.state.circles.clear()
        
        # Generate the exact circles needed for the specific scope
        self.state.circles.append(CircleState(name="Focuser", color="#00E5FF")) # Cyan
        self.state.circles.append(CircleState(name="Secondary", color="#FF007F")) # Magenta
        
        self.max_steps = 3
        if scope == "Newtonian":
            self.state.circles.append(CircleState(name="Primary", color="#FFFF00")) # Yellow
            self.max_steps = 4
            
        self.setup_layout.itemAt(0).widget().hide()
        self.combo_scope.hide()
        self.btn_start.hide()
        self.nav_container.show()
        
        self.current_step = 1
        self.apply_step()

    def stop_wizard(self):
        self.nav_container.hide()
        self.setup_layout.itemAt(0).widget().show()
        self.combo_scope.show()
        self.btn_start.show()
        
    def next_step(self):
        if self.current_step < self.max_steps:
            self.current_step += 1
            self.apply_step()
            
    def prev_step(self):
        if self.current_step > 1:
            self.current_step -= 1
            self.apply_step()

    def apply_step(self):
        self.lbl_step.setText(f"Step {self.current_step} of {self.max_steps}")
        scope = self.combo_scope.currentText()
        target_tab = 0
        
        # --- NEWTONIAN FLOW ---
        if scope == "Newtonian":
            c_focuser, c_secondary, c_primary = self.state.circles[0], self.state.circles[1], self.state.circles[2]
            
            if self.current_step == 1:
                self.lbl_instruction.setText("<b>1. Focuser Axis:</b> Adjust the Radius and Offsets of the Focuser circle below until it traces the inner edge of your focuser drawtube. This calibrates the optical axis.")
                self.state.crosshair_visible = False
                c_focuser.visible = True; c_focuser.mask_mode = "none"
                c_secondary.visible = False; c_primary.visible = False
                target_tab = 1
                
            elif self.current_step == 2:
                self.lbl_instruction.setText("<b>2. Secondary Placement:</b> The Focuser is anchored. Use your secondary mirror's center screw to move the mirror until it fits the Secondary circle below. The mask is hiding distracting reflections.")
                self.state.crosshair_offset_x = c_focuser.offset_x
                self.state.crosshair_offset_y = c_focuser.offset_y
                c_secondary.offset_x, c_secondary.offset_y = c_focuser.offset_x, c_focuser.offset_y
                c_secondary.visible = True; c_secondary.mask_mode = "inside"; c_secondary.mask_opacity = 85
                c_primary.visible = False
                target_tab = 2
                
            elif self.current_step == 3:
                self.lbl_instruction.setText("<b>3. Secondary Tilt:</b> Adjust the Primary circle to trace the primary mirror reflection. Turn your secondary tilt screws until the crosshair sits exactly inside the primary mirror's donut.")
                c_secondary.mask_mode = "none"
                c_primary.offset_x, c_primary.offset_y = c_focuser.offset_x, c_focuser.offset_y
                c_primary.visible = True; c_primary.mask_mode = "outside"; c_primary.mask_opacity = 80; c_primary.center_mark_visible = True
                target_tab = 3
                
            elif self.current_step == 4:
                self.lbl_instruction.setText("<b>4. Primary Tilt:</b> The Main Crosshair is active. Adjust your primary mirror knobs at the bottom of the telescope until the reflection of the camera lens sits exactly perfectly on the green crosshair.")
                self.state.crosshair_visible = True
                c_primary.mask_mode = "none"; c_primary.center_mark_visible = False
                c_secondary.visible = False; c_focuser.visible = False
                target_tab = 0
                
        # --- SCT / MAK FLOW ---
        elif scope == "SCT / Mak":
            # Example shell for Cassegrain logic
            if self.current_step == 1:
                self.lbl_instruction.setText("<b>1. Primary Baffle:</b> Adjust the circle to trace the outside edge of the primary baffle tube. This anchors the center.")
                target_tab = 1
            # (Steps 2 and 3 omitted for brevity, expands identically to Newtonian logic)
                
        # Sync the entire UI and force the tabs to show the controls for the current step
        self.panel.sync_ui_to_state()
        self.panel.tabs.setCurrentIndex(target_tab)