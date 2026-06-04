import tkinter as tk
from tkinter import simpledialog

from PIL import Image, ImageTk

from ..config import FaceEntry

_FACE_COLORS = ["#00ff00", "#ff4444", "#4488ff", "#ffaa00", "#ff44ff", "#00ffff"]


class FaceSelector(tk.Frame):
    def __init__(self, master, on_faces_changed=None, **kwargs):
        super().__init__(master, **kwargs)
        self.on_faces_changed = on_faces_changed
        self._faces: list[FaceEntry] = []
        self._original_image: Image.Image | None = None
        self._display_image: ImageTk.PhotoImage | None = None
        self._scale = 1.0
        self._offset_x = 0
        self._offset_y = 0
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._current_rect_id: int | None = None
        self._face_items: dict[int, tuple[int, FaceEntry]] = {}

        self.canvas = tk.Canvas(self, bg="#1a1a1a", cursor="cross")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Button-3>", self._on_right_click)
        self.canvas.bind("<Delete>", self._on_delete_key)
        self.canvas.bind("<Configure>", self._redraw)

    def set_image(self, image_path: str):
        self._original_image = Image.open(image_path)
        self._faces = []
        self._redraw()
        self._notify()

    def get_faces(self) -> list[FaceEntry]:
        return list(self._faces)

    def set_faces(self, faces: list[FaceEntry]):
        self._faces = list(faces)
        self._redraw()

    def add_face(self, face: FaceEntry):
        self._faces.append(face)
        self._redraw()
        self._notify()

    def remove_face(self, face: FaceEntry):
        if face in self._faces:
            self._faces.remove(face)
            self._redraw()
            self._notify()

    def clear_faces(self):
        self._faces = []
        self._redraw()
        self._notify()

    def _notify(self):
        if self.on_faces_changed:
            self.on_faces_changed(self._faces)

    def _redraw(self, event=None):
        self.canvas.delete("all")
        self._face_items.clear()

        if self._original_image is None:
            return

        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw < 20 or ch < 20:
            return

        img_w, img_h = self._original_image.size
        self._scale = min(cw / img_w, ch / img_h)
        display_w = int(img_w * self._scale)
        display_h = int(img_h * self._scale)
        self._offset_x = (cw - display_w) // 2
        self._offset_y = (ch - display_h) // 2

        resized = self._original_image.resize((display_w, display_h), Image.LANCZOS)
        self._display_image = ImageTk.PhotoImage(resized)
        self.canvas.create_image(
            self._offset_x, self._offset_y, anchor="nw", image=self._display_image
        )

        for i, face in enumerate(self._faces):
            color = _FACE_COLORS[i % len(_FACE_COLORS)]
            x1 = int(face.x1 * self._scale + self._offset_x)
            y1 = int(face.y1 * self._scale + self._offset_y)
            x2 = int(face.x2 * self._scale + self._offset_x)
            y2 = int(face.y2 * self._scale + self._offset_y)

            rect_id = self.canvas.create_rectangle(
                x1, y1, x2, y2, outline=color, width=2
            )
            label_id = self.canvas.create_text(
                x1 + 4,
                y1 - 4,
                text=face.name,
                anchor="sw",
                fill=color,
                font=("TkDefaultFont", 10, "bold"),
            )
            self._face_items[rect_id] = (label_id, face)

    def _to_original(self, display_x: int, display_y: int) -> tuple[int, int]:
        ox = int((display_x - self._offset_x) / self._scale)
        oy = int((display_y - self._offset_y) / self._scale)
        return ox, oy

    def _on_press(self, event):
        if self._original_image is None:
            return
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def _on_drag(self, event):
        if self._original_image is None:
            return
        if self._current_rect_id is not None:
            self.canvas.delete(self._current_rect_id)
        self._current_rect_id = self.canvas.create_rectangle(
            self._drag_start_x,
            self._drag_start_y,
            event.x,
            event.y,
            outline="#ffff00",
            width=2,
            dash=(5, 5),
        )

    def _on_release(self, event):
        if self._original_image is None or self._current_rect_id is None:
            return

        self.canvas.delete(self._current_rect_id)
        self._current_rect_id = None

        x1 = min(self._drag_start_x, event.x)
        y1 = min(self._drag_start_y, event.y)
        x2 = max(self._drag_start_x, event.x)
        y2 = max(self._drag_start_y, event.y)

        min_size = 10
        if abs(x2 - x1) < min_size or abs(y2 - y1) < min_size:
            return

        ox1, oy1 = self._to_original(x1, y1)
        ox2, oy2 = self._to_original(x2, y2)
        ox1 = max(0, ox1)
        oy1 = max(0, oy1)
        ox2 = min(self._original_image.size[0], ox2)
        oy2 = min(self._original_image.size[1], oy2)

        self.canvas.focus_set()
        name = simpledialog.askstring("Name", "Enter person's name:", parent=self)
        if not name or not name.strip():
            return

        face = FaceEntry(name=name.strip(), x1=ox1, y1=oy1, x2=ox2, y2=oy2)
        self._faces.append(face)
        self._redraw()
        self._notify()

    def _on_right_click(self, event):
        for rect_id, (_, face) in self._face_items.items():
            coords = self.canvas.coords(rect_id)
            if coords[0] <= event.x <= coords[2] and coords[1] <= event.y <= coords[3]:
                self._faces.remove(face)
                self._redraw()
                self._notify()
                return

    def _on_delete_key(self, _event):
        if self._faces:
            self._faces = []
            self._redraw()
            self._notify()
