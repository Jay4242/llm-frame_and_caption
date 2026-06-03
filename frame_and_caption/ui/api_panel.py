import customtkinter as ctk


class APIPanel(ctk.CTkFrame):
    def __init__(self, master, on_test_connection, **kwargs):
        super().__init__(master, **kwargs)
        self.on_test_connection = on_test_connection

        self._header = ctk.CTkLabel(self, text="API Settings", font=ctk.CTkFont(size=14, weight="bold"))
        self._header.pack(anchor="w", padx=8, pady=(8, 4))

        self._base_url_label = ctk.CTkLabel(self, text="Base URL:", font=ctk.CTkFont(size=11))
        self._base_url_label.pack(anchor="w", padx=8)
        self._base_url_entry = ctk.CTkEntry(self, placeholder_text="http://localhost:1234/v1")
        self._base_url_entry.pack(fill="x", padx=8, pady=(0, 4))

        self._api_key_label = ctk.CTkLabel(self, text="API Key:", font=ctk.CTkFont(size=11))
        self._api_key_label.pack(anchor="w", padx=8)
        self._api_key_entry = ctk.CTkEntry(self, placeholder_text="not-needed", show="*")
        self._api_key_entry.pack(fill="x", padx=8, pady=(0, 4))

        self._model_label = ctk.CTkLabel(self, text="Model:", font=ctk.CTkFont(size=11))
        self._model_label.pack(anchor="w", padx=8)
        self._model_entry = ctk.CTkEntry(self, placeholder_text="e.g. llama-3.2-vision")
        self._model_entry.pack(fill="x", padx=8, pady=(0, 4))

        self._test_btn = ctk.CTkButton(
            self, text="Test Connection", command=self._on_test, height=28
        )
        self._test_btn.pack(padx=8, pady=(4, 8))

    def _on_test(self):
        self.on_test_connection(self.get_values())

    def get_values(self):
        return {
            "base_url": self._base_url_entry.get().strip(),
            "api_key": self._api_key_entry.get().strip(),
            "model": self._model_entry.get().strip(),
        }

    def set_values(self, base_url, api_key, model):
        self._base_url_entry.delete(0, "end")
        self._base_url_entry.insert(0, base_url)
        self._api_key_entry.delete(0, "end")
        self._api_key_entry.insert(0, api_key)
        self._model_entry.delete(0, "end")
        self._model_entry.insert(0, model)

    def set_test_button_state(self, enabled):
        if enabled:
            self._test_btn.configure(state="normal", text="Test Connection")
        else:
            self._test_btn.configure(state="disabled", text="Testing...")
