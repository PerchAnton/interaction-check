"""An original teaching model, not a third-party editor or a discovered bug."""


class Editor:
    def __init__(self):
        self.saved = "Original"
        self.draft = None
        self.error = None

    def open(self):
        self.draft = self.saved
        self.error = None

    def type(self, text):
        if self.draft is None:
            raise ValueError("open the draft first")
        self.draft = text
        self.error = None

    def save(self):
        if self.draft is None:
            raise ValueError("open the draft first")
        if not self.draft.strip():
            self.error = "Enter a title"
            return
        self.saved = self.draft
        self.draft = None
        self.error = None

    def cancel(self):
        self.draft = None
        self.error = None
