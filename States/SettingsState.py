import os
import pygame
from States.State import State
from UI.Label import Label
from UI.Button import TextButton
from Utils.Draw import create_back_button


class SettingsState(State):
    """State for viewing and modifying game settings"""

    # Common resolution presets
    RESOLUTION_PRESETS = [
        (1280, 720),
        (1366, 768),
        (1600, 900),
        (1920, 1080),
        (2560, 1440),
    ]

    FPS_PRESETS = [30, 60, 120, 144, 240]

    def __init__(
        self,
        game,
        data=None,
        layer="foreground",
        bg_color=(40, 40, 50),
        previous_state=None,
    ):
        super().__init__(game, data, layer, bg_color, previous_state)

        # Copy current settings to work with
        self.temp_settings = {
            "SCREEN_W": game.settings.SCREEN_W,
            "SCREEN_H": game.settings.SCREEN_H,
            "FPS": game.settings.FPS,
            "LETTERBOX_COLOR": game.settings.LETTERBOX_COLOR,
            "MOUSE_VISIBLE": game.settings.MOUSE_VISIBLE,
        }

        # Find current resolution index
        current_res = (self.temp_settings["SCREEN_W"], self.temp_settings["SCREEN_H"])
        self.resolution_index = 0
        for i, res in enumerate(self.RESOLUTION_PRESETS):
            if res == current_res:
                self.resolution_index = i
                break

        # Find current FPS index
        self.fps_index = 0
        for i, fps in enumerate(self.FPS_PRESETS):
            if fps == self.temp_settings["FPS"]:
                self.fps_index = i
                break

        self._create_ui()

    def _create_ui(self):
        center_x = self.game.GAME_W * 0.5
        start_y = 120
        row_height = 80
        label_width = 300
        value_width = 250

        # Title
        self.title_label = Label(
            self.canvas,
            x=center_x - 150,
            y=30,
            width=300,
            text="Settings",
            fg_color=pygame.Color("white"),
            font=self.game.get_font("ant", 50),
        )

        # Back button
        self.go_back_btn = create_back_button(
            self.game,
            self.canvas,
            (self.game.GAME_W * 0.05, 30),
        )

        # --- Resolution ---
        row = 0
        self.resolution_label = Label(
            self.canvas,
            x=center_x - label_width - 20,
            y=start_y + row * row_height,
            width=label_width,
            text="Resolution:",
            fg_color=pygame.Color("white"),
            font=self.game.get_font("ant", 30),
        )

        self.resolution_btn = TextButton(
            self.canvas,
            x=center_x + 20,
            y=start_y + row * row_height,
            width=value_width,
            height=50,
            text=self._get_resolution_text(),
            fg_color=pygame.Color("white"),
            bg_color=(70, 70, 80),
            hover_color=(100, 100, 120),
            font=self.game.get_font("ant", 25),
            command=self._cycle_resolution,
        )

        # --- FPS ---
        row = 1
        self.fps_label = Label(
            self.canvas,
            x=center_x - label_width - 20,
            y=start_y + row * row_height,
            width=label_width,
            text="FPS:",
            fg_color=pygame.Color("white"),
            font=self.game.get_font("ant", 30),
        )

        self.fps_btn = TextButton(
            self.canvas,
            x=center_x + 20,
            y=start_y + row * row_height,
            width=value_width,
            height=50,
            text=str(self.temp_settings["FPS"]),
            fg_color=pygame.Color("white"),
            bg_color=(70, 70, 80),
            hover_color=(100, 100, 120),
            font=self.game.get_font("ant", 25),
            command=self._cycle_fps,
        )

        # --- Letterbox Color ---
        row = 2
        self.letterbox_label = Label(
            self.canvas,
            x=center_x - label_width - 20,
            y=start_y + row * row_height,
            width=label_width,
            text="Letterbox Color:",
            fg_color=pygame.Color("white"),
            font=self.game.get_font("ant", 30),
        )

        self.letterbox_btn = TextButton(
            self.canvas,
            x=center_x + 20,
            y=start_y + row * row_height,
            width=value_width,
            height=50,
            text=self._get_letterbox_text(),
            fg_color=pygame.Color("white"),
            bg_color=self.temp_settings["LETTERBOX_COLOR"],
            hover_color=self._lighten_color(self.temp_settings["LETTERBOX_COLOR"]),
            font=self.game.get_font("ant", 20),
            command=self._cycle_letterbox_color,
        )

        # --- Mouse Visible ---
        row = 3
        self.mouse_label = Label(
            self.canvas,
            x=center_x - label_width - 20,
            y=start_y + row * row_height,
            width=label_width,
            text="Show Mouse Cursor:",
            fg_color=pygame.Color("white"),
            font=self.game.get_font("ant", 30),
        )

        self.mouse_btn = TextButton(
            self.canvas,
            x=center_x + 20,
            y=start_y + row * row_height,
            width=value_width,
            height=50,
            text="ON" if self.temp_settings["MOUSE_VISIBLE"] else "OFF",
            fg_color=pygame.Color("white"),
            bg_color=(70, 130, 70) if self.temp_settings["MOUSE_VISIBLE"] else (130, 70, 70),
            hover_color=(90, 150, 90) if self.temp_settings["MOUSE_VISIBLE"] else (150, 90, 90),
            font=self.game.get_font("ant", 25),
            command=self._toggle_mouse_visible,
        )

        # --- Apply Button ---
        self.apply_btn = TextButton(
            self.canvas,
            center=(center_x, start_y + 5 * row_height),
            width=200,
            height=60,
            text="Apply & Save",
            fg_color=pygame.Color("white"),
            bg_color=(50, 120, 50),
            hover_color=(70, 160, 70),
            font=self.game.get_font("ant", 30),
            command=self._apply_settings,
        )

        # --- Reset Button ---
        self.reset_btn = TextButton(
            self.canvas,
            center=(center_x, start_y + 6 * row_height),
            width=150,
            height=45,
            text="Reset",
            fg_color=pygame.Color("white"),
            bg_color=(120, 80, 50),
            hover_color=(160, 100, 70),
            font=self.game.get_font("ant", 25),
            command=self._reset_settings,
        )

    def _get_resolution_text(self):
        w, h = self.temp_settings["SCREEN_W"], self.temp_settings["SCREEN_H"]
        return f"{w} x {h}"

    def _get_letterbox_text(self):
        color = self.temp_settings["LETTERBOX_COLOR"]
        return f"RGB({color[0]}, {color[1]}, {color[2]})"

    def _lighten_color(self, color):
        return tuple(min(255, c + 40) for c in color)

    def _cycle_resolution(self):
        self.resolution_index = (self.resolution_index + 1) % len(self.RESOLUTION_PRESETS)
        res = self.RESOLUTION_PRESETS[self.resolution_index]
        self.temp_settings["SCREEN_W"] = res[0]
        self.temp_settings["SCREEN_H"] = res[1]
        self.resolution_btn.text = self._get_resolution_text()

    def _cycle_fps(self):
        self.fps_index = (self.fps_index + 1) % len(self.FPS_PRESETS)
        self.temp_settings["FPS"] = self.FPS_PRESETS[self.fps_index]
        self.fps_btn.text = str(self.temp_settings["FPS"])

    def _cycle_letterbox_color(self):
        # Cycle through some preset colors
        presets = [
            (0, 0, 0),
            (30, 30, 30),
            (50, 50, 50),
            (70, 70, 70),
            (20, 20, 40),
            (40, 20, 20),
            (20, 40, 20),
        ]
        current = tuple(self.temp_settings["LETTERBOX_COLOR"])
        try:
            idx = presets.index(current)
            idx = (idx + 1) % len(presets)
        except ValueError:
            idx = 0
        self.temp_settings["LETTERBOX_COLOR"] = presets[idx]
        self.letterbox_btn.text = self._get_letterbox_text()
        self.letterbox_btn.bg_color = presets[idx]
        self.letterbox_btn.original_bg_color = presets[idx]
        self.letterbox_btn.hover_color = self._lighten_color(presets[idx])

    def _toggle_mouse_visible(self):
        self.temp_settings["MOUSE_VISIBLE"] = not self.temp_settings["MOUSE_VISIBLE"]
        visible = self.temp_settings["MOUSE_VISIBLE"]
        self.mouse_btn.text = "ON" if visible else "OFF"
        self.mouse_btn.bg_color = (70, 130, 70) if visible else (130, 70, 70)
        self.mouse_btn.original_bg_color = self.mouse_btn.bg_color
        self.mouse_btn.hover_color = (90, 150, 90) if visible else (150, 90, 90)

    def _apply_settings(self):
        # Apply settings to game
        self.game.settings.SCREEN_W = self.temp_settings["SCREEN_W"]
        self.game.settings.SCREEN_H = self.temp_settings["SCREEN_H"]
        self.game.settings.FPS = self.temp_settings["FPS"]
        self.game.settings.LETTERBOX_COLOR = self.temp_settings["LETTERBOX_COLOR"]
        self.game.settings.MOUSE_VISIBLE = self.temp_settings["MOUSE_VISIBLE"]

        # Update game state
        self.game.fps = self.temp_settings["FPS"]
        pygame.mouse.set_visible(self.temp_settings["MOUSE_VISIBLE"])

        # Resize window if resolution changed
        self.game.screen = pygame.display.set_mode(
            (self.game.settings.SCREEN_W, self.game.settings.SCREEN_H),
            pygame.RESIZABLE,
        )
        self.game._recompute_scaling()

        # Save to file
        settings_path = os.path.join(os.getcwd(), "settings.json")
        with open(settings_path, "w") as f:
            f.write(self.game.settings.to_json())

        print(f"Settings saved to {settings_path}")

    def _reset_settings(self):
        # Reset to current game settings
        self.temp_settings = {
            "SCREEN_W": self.game.settings.SCREEN_W,
            "SCREEN_H": self.game.settings.SCREEN_H,
            "FPS": self.game.settings.FPS,
            "LETTERBOX_COLOR": self.game.settings.LETTERBOX_COLOR,
            "MOUSE_VISIBLE": self.game.settings.MOUSE_VISIBLE,
        }

        # Update UI
        current_res = (self.temp_settings["SCREEN_W"], self.temp_settings["SCREEN_H"])
        self.resolution_index = 0
        for i, res in enumerate(self.RESOLUTION_PRESETS):
            if res == current_res:
                self.resolution_index = i
                break

        self.fps_index = 0
        for i, fps in enumerate(self.FPS_PRESETS):
            if fps == self.temp_settings["FPS"]:
                self.fps_index = i
                break

        self.resolution_btn.text = self._get_resolution_text()
        self.fps_btn.text = str(self.temp_settings["FPS"])
        self.letterbox_btn.text = self._get_letterbox_text()
        self.letterbox_btn.bg_color = self.temp_settings["LETTERBOX_COLOR"]
        self.letterbox_btn.original_bg_color = self.temp_settings["LETTERBOX_COLOR"]
        self.letterbox_btn.hover_color = self._lighten_color(self.temp_settings["LETTERBOX_COLOR"])

        visible = self.temp_settings["MOUSE_VISIBLE"]
        self.mouse_btn.text = "ON" if visible else "OFF"
        self.mouse_btn.bg_color = (70, 130, 70) if visible else (130, 70, 70)
        self.mouse_btn.original_bg_color = self.mouse_btn.bg_color
        self.mouse_btn.hover_color = (90, 150, 90) if visible else (150, 90, 90)

    def render(self, surface):
        super().render(surface)

    def update(self, delta):
        super().update(delta)
