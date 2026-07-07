# main.py - Entry point for MVC Sync Editor
# Copyright (C) 2026 Jamie Martin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
