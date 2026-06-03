import tkinter as tk
from tkinter import filedialog
from pathlib import Path

import customtkinter as ctk
from tkinterdnd2 import DND_FILES


class DropZone(tk.Frame):
    def __init__(self, master, on_image_selected, **kwargs):
        super().__init__(master, **kwargs)
        self.on_image_selected = on_image_selected
        self._image_path = None

        bg = "#2b2b2b" if ctk.get_appearance_mode() == "Dark" else "#d9d9d9"
        self._inner = tk.Label(
            self,
            text="Drop image here\nor click Browse",
            bg=bg,
            fg="gray60",
            font=("", 12),
            cursor="hand2",
            relief="groove",
            bd=2,
            anchor="center",
        )
        self._inner.pack(fill="both", expand=True, padx=4, pady=4)
        self._inner.bind("<Button-1>", self._browse)
        self._inner.drop_target_register(DND_FILES)
        self._inner.dnd_bind("<<Drop>>", self._on_drop)

        self._browse_btn = ctk.CTkButton(
            self, text="Browse...", command=self._browse, height=28
        )
        self._browse_btn.pack(pady=(0, 4))

    def _browse(self, event=None):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("All files", "*.*"),
            ],
        )
        if file_path:
            self._set_image(file_path)

    def _on_drop(self, event):
        raw = event.data.strip()
        if raw.startswith("{") and raw.endswith("}"):
            raw = raw[1:-1]
        path = Path(raw).resolve()
        if path.suffix.lower().lstrip(".") in ("png", "jpg", "jpeg", "gif", "bmp", "webp"):
            self._set_image(str(path))

    def _set_image(self, path):
        self._image_path = path
        self._inner.config(text=Path(path).name)
        self.on_image_selected(path)

    @property
    def image_path(self):
        return self._image_path
