from PyQt6.QtWidgets import QFileDialog

class EditorController:
    """
    Controller connecting EditorView and DocumentModel.
    Listens for UI signals and coordinates changes in the Model.
    """
    def __init__(self, model, view):
        self.model = model
        self.view = view

        # Connect model signals to view slots
        self.model.text_changed.connect(self.view.set_content)
        self.model.file_path_changed.connect(self.view.set_file_path)

        # Connect view signals to controller actions
        self.view.open_triggered.connect(self.open_file)
        self.view.save_triggered.connect(self.save_file)
        self.view.text_user_edited.connect(self.update_model_text)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self.view, "Open File", "", "Text Files (*.txt);;Python Files (*.py);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Update the model
                self.model.text_content = content
                self.model.file_path = file_path
                self.view.show_message("File loaded successfully.")
            except Exception as e:
                self.view.show_message(f"Error loading file: {str(e)}")

    def save_file(self, content: str):
        file_path = self.model.file_path
        if not file_path:
            file_path, _ = QFileDialog.getSaveFileName(
                self.view, "Save File", "", "Text Files (*.txt);;Python Files (*.py);;All Files (*)"
            )
            if not file_path:
                return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            # Sync model state
            self.model.file_path = file_path
            self.model.text_content = content
            self.view.show_message("File saved successfully.")
        except Exception as e:
            self.view.show_message(f"Error saving file: {str(e)}")

    def update_model_text(self, text: str):
        # Update the model silently to keep text in sync without causing signals loops
        self.model._text_content = text
