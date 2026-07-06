import sys
from PyQt6.QtWidgets import QApplication
from app.models.model import DocumentModel
from app.views.view import EditorView
from app.controllers.controller import EditorController

def main():
    app = QApplication(sys.argv)
    
    # Initialize the Model, View, and Controller
    model = DocumentModel()
    view = EditorView()
    controller = EditorController(model, view)
    
    # Show window
    view.show()
    
    # Execute the application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
