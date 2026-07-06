from PyQt6.QtCore import QObject, pyqtSignal

class DocumentModel(QObject):
    """
    Model representing the text document content and its filesystem location.
    Provides signals when the contents or path change.
    """
    text_changed = pyqtSignal(str)
    file_path_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._text_content = ""
        self._file_path = None

    @property
    def text_content(self) -> str:
        return self._text_content

    @text_content.setter
    def text_content(self, text: str):
        if self._text_content != text:
            self._text_content = text
            self.text_changed.emit(text)

    @property
    def file_path(self) -> str:
        return self._file_path

    @file_path.setter
    def file_path(self, path: str):
        if self._file_path != path:
            self._file_path = path
            # Emit path name (or "Untitled" if None)
            self.file_path_changed.emit(path if path else "Untitled")
