import customtkinter as ctk

from ..config import FaceEntry


class FacePanel(ctk.CTkFrame):
    def __init__(self, master, on_add_face=None, on_delete_face=None, **kwargs):
        super().__init__(master, **kwargs)
        self.on_add_face = on_add_face
        self.on_delete_face = on_delete_face

        self._header = ctk.CTkLabel(
            self, text="Named Faces", font=ctk.CTkFont(size=14, weight="bold"),
        )
        self._header.pack(anchor="w", padx=8, pady=(8, 4))

        self._instructions = ctk.CTkLabel(
            self,
            text="Draw boxes on faces in the right panel, then name them.",
            font=ctk.CTkFont(size=10),
            text_color="gray60",
        )
        self._instructions.pack(anchor="w", padx=8)

        self._add_btn = ctk.CTkButton(
            self, text="Draw Faces", height=28,
            command=self._on_add,
        )
        self._add_btn.pack(fill="x", padx=8, pady=(4, 4))

        self._face_list = ctk.CTkFrame(self, fg_color="transparent")
        self._face_list.pack(fill="x", padx=8, pady=(0, 4))

        self._status_label = ctk.CTkLabel(
            self, text="No faces added", font=ctk.CTkFont(size=11),
            text_color="gray60",
        )
        self._status_label.pack(anchor="w", padx=8, pady=(0, 8))

    def update_faces(self, faces: list[FaceEntry]):
        for widget in self._face_list.winfo_children():
            widget.destroy()

        if not faces:
            self._status_label.configure(text="No faces added")
        else:
            self._status_label.configure(text=f"{len(faces)} face(s) listed")

        for face in faces:
            row = ctk.CTkFrame(self._face_list, fg_color="transparent")
            row.pack(fill="x", pady=(0, 2))

            label = ctk.CTkLabel(
                row, text=face.name,
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w",
            )
            label.pack(side="left", padx=(0, 8))

            del_btn = ctk.CTkButton(
                row, text="\u00d7", width=24, height=24,
                command=lambda f=face: self._on_delete(f),
            )
            del_btn.pack(side="right", padx=(0, 4))

    def _on_add(self):
        if self.on_add_face:
            self.on_add_face()

    def _on_delete(self, face: FaceEntry):
        if self.on_delete_face:
            self.on_delete_face(face)
