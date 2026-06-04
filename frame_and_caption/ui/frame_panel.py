import re
from tkinter import colorchooser

import customtkinter as ctk


GRADIENT_DIRECTIONS = ["horizontal", "vertical", "diagonal", "anti-diagonal", "radial"]

_HEX_PATTERN = re.compile(r"^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$")


def _normalise_hex(raw: str) -> str:
    """Return full 6-digit hex from short or long form, or empty string if invalid."""
    raw = raw.strip()
    m = _HEX_PATTERN.match(raw)
    if not m:
        return ""
    digits = m.group(1)
    if len(digits) == 3:
        digits = "".join(c * 2 for c in digits)
    return "#" + digits.lower()


class FramePanel(ctk.CTkFrame):
    def __init__(self, master, on_settings_changed, **kwargs):
        super().__init__(master, **kwargs)
        self.on_settings_changed = on_settings_changed
        self._current_color = "#1a1a2e"
        self._current_color2 = "#e94560"
        self._gradient_enabled = False
        self._gradient_vars = {}

        self._header = ctk.CTkLabel(self, text="Frame Settings", font=ctk.CTkFont(size=14, weight="bold"))
        self._header.pack(anchor="w", padx=8, pady=(8, 4))

        self._gradient_toggle = ctk.CTkCheckBox(
            self, text="Enable Gradient",
            command=self._on_gradient_toggle,
        )
        self._gradient_toggle.pack(anchor="w", padx=8, pady=(0, 4))

        self._solid_color_row = ctk.CTkFrame(self, fg_color="transparent")
        self._solid_color_row.pack(fill="x", padx=8, pady=(0, 4))
        self._color_swatch = ctk.CTkLabel(
            self._solid_color_row, text="    ", fg_color=self._current_color,
            width=30, height=24, corner_radius=4
        )
        self._color_swatch.pack(side="left")
        self._color_btn = ctk.CTkButton(
            self._solid_color_row, text="Frame Color", command=self._pick_color,
            height=28, width=100
        )
        self._color_btn.pack(side="left", padx=(8, 0))
        self._color_entry = ctk.CTkEntry(self._solid_color_row, width=70, placeholder_text="#rrggbb")
        self._color_entry.insert(0, self._current_color)
        self._color_entry.bind("<<Paste>>", lambda e: self._on_paste("color"))
        self._color_entry.bind("<KeyRelease>", lambda e: self._on_hex_entry("color"))
        self._color_entry.bind("<FocusOut>", lambda e: self._on_hex_entry("color"))
        self._color_entry.pack(side="left", padx=8)

        self._gradient_row = ctk.CTkFrame(self, fg_color="transparent")

        self._color2_swatch = ctk.CTkLabel(
            self._gradient_row, text="    ", fg_color=self._current_color2,
            width=30, height=24, corner_radius=4
        )
        self._color2_swatch.pack(side="left")
        self._color2_btn = ctk.CTkButton(
            self._gradient_row, text="Color 2", command=self._pick_color2,
            height=28, width=100
        )
        self._color2_btn.pack(side="left", padx=(8, 0))
        self._color2_entry = ctk.CTkEntry(self._gradient_row, width=70, placeholder_text="#rrggbb")
        self._color2_entry.insert(0, self._current_color2)
        self._color2_entry.bind("<<Paste>>", lambda e: self._on_paste("color2"))
        self._color2_entry.bind("<KeyRelease>", lambda e: self._on_hex_entry("color2"))
        self._color2_entry.bind("<FocusOut>", lambda e: self._on_hex_entry("color2"))
        self._color2_entry.pack(side="left", padx=8)

        self._direction_label = ctk.CTkLabel(self, text="Gradient Direction:", font=ctk.CTkFont(size=11))
        self._direction_menu = ctk.CTkOptionMenu(
            self, values=GRADIENT_DIRECTIONS, command=self._on_direction_changed,
            height=28,
        )
        self._direction_menu.set("horizontal")

        self._thickness_label = ctk.CTkLabel(self, text="Thickness (px):", font=ctk.CTkFont(size=11))
        self._thickness_label.pack(anchor="w", padx=8)
        self._thickness_entry = ctk.CTkEntry(self, placeholder_text="80")
        self._thickness_entry.pack(fill="x", padx=8, pady=(0, 4))
        self._thickness_entry.insert(0, "80")
        self._thickness_entry.bind("<KeyRelease>", lambda e: self._notify())

        self._headline_label = ctk.CTkLabel(self, text="Headline:", font=ctk.CTkFont(size=11))
        self._headline_label.pack(anchor="w", padx=8)
        self._headline_entry = ctk.CTkEntry(self, placeholder_text="e.g. Class of 2026!")
        self._headline_entry.pack(fill="x", padx=8, pady=(0, 4))
        self._headline_entry.bind("<KeyRelease>", lambda e: self._notify())

        self._font_size_label = ctk.CTkLabel(self, text="Headline Font Size:", font=ctk.CTkFont(size=11))
        self._font_size_label.pack(anchor="w", padx=8)
        self._font_size_entry = ctk.CTkEntry(self, placeholder_text="36")
        self._font_size_entry.pack(fill="x", padx=8, pady=(0, 4))
        self._font_size_entry.insert(0, "36")
        self._font_size_entry.bind("<KeyRelease>", lambda e: self._notify())

        self._caption_font_size_label = ctk.CTkLabel(self, text="Caption Font Size:", font=ctk.CTkFont(size=11))
        self._caption_font_size_label.pack(anchor="w", padx=8)
        self._caption_font_size_entry = ctk.CTkEntry(self, placeholder_text="32")
        self._caption_font_size_entry.pack(fill="x", padx=8, pady=(0, 8))
        self._caption_font_size_entry.insert(0, "32")
        self._caption_font_size_entry.bind("<KeyRelease>", lambda e: self._notify())

    def _on_gradient_toggle(self):
        self._gradient_enabled = self._gradient_toggle.get() == 1
        if self._gradient_enabled:
            self._gradient_row.pack(fill="x", padx=8, pady=(0, 4), after=self._solid_color_row)
            self._direction_label.pack(anchor="w", padx=8, before=self._thickness_label)
            self._direction_menu.pack(fill="x", padx=8, pady=(0, 4), before=self._thickness_label)
        else:
            self._gradient_row.pack_forget()
            self._direction_label.pack_forget()
            self._direction_menu.pack_forget()
        self._notify()

    def _on_direction_changed(self, _value):
        self._notify()

    def _pick_color(self):
        result = colorchooser.askcolor(color=self._current_color, title="Choose Frame Color")
        if result and result[1]:
            self._current_color = result[1]
            self._color_swatch.configure(fg_color=self._current_color)
            self._color_entry.delete(0, "end")
            self._color_entry.insert(0, self._current_color)
            self._notify()

    def _pick_color2(self):
        result = colorchooser.askcolor(color=self._current_color2, title="Choose Gradient Color 2")
        if result and result[1]:
            self._current_color2 = result[1]
            self._color2_swatch.configure(fg_color=self._current_color2)
            self._color2_entry.delete(0, "end")
            self._color2_entry.insert(0, self._current_color2)
            self._notify()

    def _on_paste(self, which):
        entry = self._color_entry if which == "color" else self._color2_entry
        entry.delete(0, "end")
        entry.after_idle(lambda: self._on_hex_entry(which))

    def _on_hex_entry(self, which):
        entry = self._color_entry if which == "color" else self._color2_entry
        swatch = self._color_swatch if which == "color" else self._color2_swatch
        attr = "_current_color" if which == "color" else "_current_color2"

        raw = entry.get().strip()
        if raw == "":
            return

        normalised = _normalise_hex(raw)
        if normalised:
            setattr(self, attr, normalised)
            swatch.configure(fg_color=normalised)
            if entry.get() != normalised:
                entry.delete(0, "end")
                entry.insert(0, normalised)
            self._notify()

    def _notify(self):
        if self.on_settings_changed:
            self.on_settings_changed()

    def get_values(self):
        try:
            thickness = int(self._thickness_entry.get().strip())
        except ValueError:
            thickness = 80
        try:
            font_size = int(self._font_size_entry.get().strip())
        except ValueError:
            font_size = 36
        try:
            caption_font_size = int(self._caption_font_size_entry.get().strip())
        except ValueError:
            caption_font_size = 32
        return {
            "color": self._current_color,
            "thickness": thickness,
            "headline": self._headline_entry.get().strip(),
            "font_size": font_size,
            "caption_font_size": caption_font_size,
            "gradient_enabled": self._gradient_enabled,
            "gradient_color2": self._current_color2,
            "gradient_direction": self._direction_menu.get(),
        }

    def set_values(self, color, thickness, headline, font_size,
                   caption_font_size=32,
                   gradient_enabled=False, gradient_color2="#e94560",
                   gradient_direction="horizontal"):
        self._current_color = color
        self._color_swatch.configure(fg_color=color)
        self._color_entry.delete(0, "end")
        self._color_entry.insert(0, color)
        self._thickness_entry.delete(0, "end")
        self._thickness_entry.insert(0, str(thickness))
        self._headline_entry.delete(0, "end")
        self._headline_entry.insert(0, headline)
        self._font_size_entry.delete(0, "end")
        self._font_size_entry.insert(0, str(font_size))
        self._caption_font_size_entry.delete(0, "end")
        self._caption_font_size_entry.insert(0, str(caption_font_size))

        self._current_color2 = gradient_color2
        self._color2_swatch.configure(fg_color=gradient_color2)
        self._color2_entry.delete(0, "end")
        self._color2_entry.insert(0, gradient_color2)
        self._direction_menu.set(gradient_direction)

        self._gradient_enabled = gradient_enabled
        if self._gradient_toggle.get() != (1 if gradient_enabled else 0):
            self._gradient_toggle.select() if gradient_enabled else self._gradient_toggle.deselect()
        if gradient_enabled:
            self._gradient_row.pack(fill="x", padx=8, pady=(0, 4), after=self._solid_color_row)
            self._direction_label.pack(anchor="w", padx=8, before=self._thickness_label)
            self._direction_menu.pack(fill="x", padx=8, pady=(0, 4), before=self._thickness_label)
        else:
            self._gradient_row.pack_forget()
            self._direction_label.pack_forget()
            self._direction_menu.pack_forget()
