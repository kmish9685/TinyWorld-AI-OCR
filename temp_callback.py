    def _on_language_change(self, event=None):
        """Show/hide custom language input based on selection"""
        selected = self.language_var.get()
        if selected == "Custom...":
            self.custom_lang_frame.pack(fill="x", pady=(8, 0))
        else:
            self.custom_lang_frame.pack_forget()
