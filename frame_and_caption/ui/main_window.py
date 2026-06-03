import threading
import tempfile
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk
from PIL import Image

from ..api_client import generate_caption
from ..config import Config, FrameConfig, APIConfig, load_config, save_config
from ..image_processor import add_frame_and_caption
from .api_panel import APIPanel
from .drop_zone import DropZone
from .frame_panel import FramePanel
from .prompt_panel import PromptPanel


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Frame & Caption")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)

        self._config = load_config()
        self._image_path = None
        self._caption = ""
        self._preview_pil = None

        self._build_ui()
        self._apply_config()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)

        self._left_panel = ctk.CTkScrollableFrame(self.root, width=360)
        self._left_panel.grid(row=0, column=0, sticky="nsw", padx=(8, 4), pady=8)

        self._drop_zone = DropZone(
            self._left_panel, on_image_selected=self._on_image_selected, height=120
        )
        self._drop_zone.pack(fill="x", pady=(0, 4))

        self._api_panel = APIPanel(
            self._left_panel, on_test_connection=self._on_test_connection
        )
        self._api_panel.pack(fill="x", pady=(0, 4))

        self._frame_panel = FramePanel(
            self._left_panel, on_settings_changed=self._refresh_preview
        )
        self._frame_panel.pack(fill="x", pady=(0, 4))

        self._prompt_panel = PromptPanel(self._left_panel)
        self._prompt_panel.pack(fill="x", pady=(0, 4))

        self._generate_btn = ctk.CTkButton(
            self._left_panel,
            text="Generate Caption",
            command=self._on_generate,
            height=36,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self._generate_btn.pack(fill="x", padx=8, pady=(0, 4))

        self._save_btn = ctk.CTkButton(
            self._left_panel,
            text="Save Framed Image",
            command=self._on_save,
            height=36,
            state="disabled",
        )
        self._save_btn.pack(fill="x", padx=8, pady=(0, 8))

        self._preview_frame = ctk.CTkFrame(self.root, fg_color="gray10")
        self._preview_frame.grid(row=0, column=1, sticky="nsew", padx=(4, 8), pady=8)
        self._preview_frame.grid_rowconfigure(0, weight=1)
        self._preview_frame.grid_columnconfigure(0, weight=1)

        self._preview_label = ctk.CTkLabel(self._preview_frame, text="No image selected", font=ctk.CTkFont(size=14))
        self._preview_label.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        self._preview_frame.bind("<Configure>", self._on_preview_resize)

        self._status_bar = ctk.CTkLabel(
            self.root, text="Ready", anchor="w",
            font=ctk.CTkFont(size=11), fg_color="gray20", corner_radius=0,
            height=28,
        )
        self._status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")

    def _apply_config(self):
        c = self._config
        self._api_panel.set_values(c.api.base_url, c.api.api_key, c.api.model)
        self._frame_panel.set_values(
            c.frame.color, c.frame.thickness, c.frame.headline, c.frame.font_size,
            c.frame.gradient_enabled, c.frame.gradient_color2, c.frame.gradient_direction
        )
        self._prompt_panel.set_prompt(c.prompt)

    def _on_image_selected(self, path):
        self._image_path = path
        self._caption = ""
        self._save_btn.configure(state="disabled")
        self._refresh_preview()
        self._set_status(f"Loaded: {Path(path).name}")

    def _refresh_preview(self, *_):
        if not self._image_path:
            return

        frame_vals = self._frame_panel.get_values()
        frame_config = FrameConfig(
            color=frame_vals["color"],
            thickness=frame_vals["thickness"],
            headline=frame_vals["headline"],
            font_size=frame_vals["font_size"],
            gradient_enabled=frame_vals["gradient_enabled"],
            gradient_color2=frame_vals["gradient_color2"],
            gradient_direction=frame_vals["gradient_direction"],
        )

        display_caption = self._caption if self._caption else "[AI Caption]"

        try:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp_path = tmp.name

            add_frame_and_caption(
                self._image_path, tmp_path, frame_config, display_caption
            )
            self._preview_pil = Image.open(tmp_path)
            self._show_preview_image()
        except Exception as e:
            self._set_status(f"Preview error: {e}")

    def _show_preview_image(self):
        if self._preview_pil is None:
            return

        frame_w = self._preview_frame.winfo_width()
        frame_h = self._preview_frame.winfo_height()

        if frame_w < 20 or frame_h < 20:
            return

        img = self._preview_pil.copy()
        img.thumbnail((frame_w - 32, frame_h - 32), Image.LANCZOS)

        self._preview_tk = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
        self._preview_label.configure(image=self._preview_tk, text="")

    def _on_preview_resize(self, event=None):
        if self._preview_pil:
            self._show_preview_image()

    def _on_generate(self):
        if not self._image_path:
            self._set_status("Error: No image selected")
            return

        api_vals = self._api_panel.get_values()
        if not api_vals["model"]:
            self._set_status("Error: Model name required")
            return

        self._generate_btn.configure(state="disabled", text="Generating...")
        self._set_status("Generating caption...")
        self._streamed = ""

        api_config = APIConfig(
            base_url=api_vals["base_url"],
            api_key=api_vals["api_key"],
            model=api_vals["model"],
        )
        prompt = self._prompt_panel.get_prompt()

        def _on_stream(part_type: str, text: str) -> None:
            self._streamed += text
            snippet = self._streamed[-72:]
            self.root.after(0, lambda: self._set_status(f"Generating... {snippet}"))

        def _thread():
            try:
                caption = generate_caption(
                    self._image_path, prompt, api_config, on_stream=_on_stream
                )
                self.root.after(0, lambda: self._on_caption_ready(caption))
            except Exception as e:
                self.root.after(0, lambda: self._on_caption_error(str(e)))

        threading.Thread(target=_thread, daemon=True).start()

    def _on_caption_ready(self, caption):
        self._caption = caption
        self._generate_btn.configure(state="normal", text="Generate Caption")
        self._save_btn.configure(state="normal")
        self._refresh_preview()
        self._set_status(f"Caption: {caption}")

    def _on_caption_error(self, error_msg):
        self._generate_btn.configure(state="normal", text="Generate Caption")
        self._set_status(f"Error: {error_msg}")

    def _on_save(self):
        if not self._image_path:
            return

        orig_name = Path(self._image_path).stem
        file_path = filedialog.asksaveasfilename(
            title="Save Framed Image",
            defaultextension=".png",
            initialfile=f"framed_{orig_name}.png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("All files", "*.*")],
        )
        if not file_path:
            return

        frame_vals = self._frame_panel.get_values()
        frame_config = FrameConfig(
            color=frame_vals["color"],
            thickness=frame_vals["thickness"],
            headline=frame_vals["headline"],
            font_size=frame_vals["font_size"],
            gradient_enabled=frame_vals["gradient_enabled"],
            gradient_color2=frame_vals["gradient_color2"],
            gradient_direction=frame_vals["gradient_direction"],
        )

        try:
            add_frame_and_caption(
                self._image_path, file_path, frame_config, self._caption
            )
            self._set_status(f"Saved: {file_path}")
        except Exception as e:
            self._set_status(f"Save error: {e}")

    def _on_test_connection(self, api_vals):
        self._api_panel.set_test_button_state(False)

        api_config = APIConfig(
            base_url=api_vals["base_url"],
            api_key=api_vals["api_key"],
            model=api_vals["model"],
        )

        def _thread():
            try:
                from openai import OpenAI
                client = OpenAI(base_url=api_config.base_url, api_key=api_config.api_key)
                models = client.models.list()
                names = [m.id for m in models]
                self.root.after(0, lambda: self._on_test_success(names))
            except Exception as e:
                self.root.after(0, lambda: self._on_test_error(str(e)))

        threading.Thread(target=_thread, daemon=True).start()

    def _on_test_success(self, models):
        self._api_panel.set_test_button_state(True)
        msg = f"Connected! {len(models)} models available."
        self._set_status(msg)

    def _on_test_error(self, error_msg):
        self._api_panel.set_test_button_state(True)
        self._set_status(f"Connection error: {error_msg}")

    def _on_close(self):
        self._save_config()
        self.root.destroy()

    def _save_config(self):
        api_vals = self._api_panel.get_values()
        frame_vals = self._frame_panel.get_values()
        self._config.api.base_url = api_vals["base_url"]
        self._config.api.api_key = api_vals["api_key"]
        self._config.api.model = api_vals["model"]
        self._config.frame.color = frame_vals["color"]
        self._config.frame.thickness = frame_vals["thickness"]
        self._config.frame.headline = frame_vals["headline"]
        self._config.frame.font_size = frame_vals["font_size"]
        self._config.frame.gradient_enabled = frame_vals["gradient_enabled"]
        self._config.frame.gradient_color2 = frame_vals["gradient_color2"]
        self._config.frame.gradient_direction = frame_vals["gradient_direction"]
        self._config.prompt = self._prompt_panel.get_prompt()
        save_config(self._config)

    def _set_status(self, text):
        self._status_bar.configure(text=text)
