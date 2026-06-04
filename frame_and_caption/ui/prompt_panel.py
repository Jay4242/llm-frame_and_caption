import customtkinter as ctk


class PromptPanel(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self._header = ctk.CTkLabel(
            self, text="LLM Prompt", font=ctk.CTkFont(size=14, weight="bold")
        )
        self._header.pack(anchor="w", padx=8, pady=(8, 4))

        self._instructions = ctk.CTkLabel(
            self,
            text='The LLM must return JSON with a "Caption" field.',
            font=ctk.CTkFont(size=10),
            text_color="gray60",
        )
        self._instructions.pack(anchor="w", padx=8)

        self._text = ctk.CTkTextbox(self, height=120, wrap="word")
        self._text.pack(fill="x", padx=8, pady=(4, 8))
        self._text.insert(
            "1.0",
            "You are a helpful assistant. "
            "Describe this image concisely in a single, brief, engaging caption. "
            'Respond with a JSON object containing a single key "Caption" with your caption text. '
            "Do not output anything else.",
        )

    def get_prompt(self) -> str:
        return self._text.get("1.0", "end-1c")

    def set_prompt(self, prompt: str) -> None:
        self._text.delete("1.0", "end")
        self._text.insert("1.0", prompt)
