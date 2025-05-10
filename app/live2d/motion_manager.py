import os
import json
import random
from PyQt5.QtCore import QObject, QTimer


class MotionManager(QObject):
    """Manager for Live2D model motions and expressions"""

    def __init__(self, model_manager):
        super().__init__()
        self.model_manager = model_manager
        self.motions = {}
        self.expressions = {}
        self.current_motion = None
        self.current_expression = None

        # Idle motion timer
        self.idle_timer = QTimer(self)
        self.idle_timer.timeout.connect(self.play_idle_motion)
        self.idle_timer.setInterval(10000)  # 10 seconds
        self.idle_timer.start()

    def load_motions(self, model_path):
        """Load motions from model directory"""
        self.motions = {}
        self.expressions = {}

        model_json_path = None
        if os.path.exists(os.path.join(model_path, "model3.json")):
            model_json_path = os.path.join(model_path, "model3.json")
        elif os.path.exists(os.path.join(model_path, "model.json")):
            model_json_path = os.path.join(model_path, "model.json")

        if not model_json_path:
            print(f"No model definition found in {model_path}")
            return

        try:
            with open(model_json_path, "r", encoding="utf-8") as f:
                model_data = json.load(f)

            if "motions" in model_data:
                for group_name, motions in model_data["motions"].items():
                    self.motions[group_name] = []
                    for motion in motions:
                        file_path = os.path.join(model_path, motion.get("file", ""))
                        if os.path.exists(file_path):
                            self.motions[group_name].append({
                                "file": file_path,
                                "fade_in": motion.get("fade_in", 0),
                                "fade_out": motion.get("fade_out", 0)
                            })

            if "expressions" in model_data:
                for expression in model_data["expressions"]:
                    name = expression.get("name", "")
                    file_path = os.path.join(model_path, expression.get("file", ""))
                    if name and os.path.exists(file_path):
                        self.expressions[name] = file_path

        except Exception as e:
            print(f"Failed to load motions: {e}")

    def play_motion(self, group, index=None):
        """Play a specific motion"""
        if group in self.motions and self.motions[group]:
            if index is None or index >= len(self.motions[group]):
                index = random.randint(0, len(self.motions[group]) - 1)

            motion_data = self.motions[group][index]
            self.current_motion = motion_data

            print(f"Playing motion: {group} {index}")
            self.idle_timer.start()
            return True
        return False

    def play_expression(self, name):
        """Play a specific expression"""
        if name in self.expressions:
            self.current_expression = name
            print(f"Playing expression: {name}")
            return True
        return False

    def play_idle_motion(self):
        """Play a random idle motion"""
        if "idle" in self.motions and self.motions["idle"]:
            self.play_motion("idle")
        elif self.motions:
            group = list(self.motions.keys())[0]
            self.play_motion(group)

    def on_tap(self, x, y):
        """Handle tap interaction"""
        if "tap" in self.motions and self.motions["tap"]:
            self.play_motion("tap")

        if self.expressions:
            expression = random.choice(list(self.expressions.keys()))
            self.play_expression(expression)

    def update(self):
        """Update motion and expression state"""
        pass
