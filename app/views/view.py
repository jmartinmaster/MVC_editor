from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
    QTreeView, QListWidget, QListWidgetItem, QTextEdit, QPushButton, 
    QLabel, QStatusBar, QMenuBar, QToolBar, QCheckBox, QFileDialog
)
from PyQt6.QtGui import QFileSystemModel, QFont, QIcon, QAction
from PyQt6.QtCore import pyqtSignal, Qt, QDir, QModelIndex
import os

from app.views.editor import EditorPane

class ConnectionItemWidget(QWidget):
    """
    Custom widget to display connection items in the MVC Sync Inspector list.
    Displays a colorful badge based on the connection type.
    """
    def __init__(self, conn: dict, parent=None):
        super().__init__(parent)
        self.conn = conn
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)
        
        # Color definitions for type badges
        colors = {
            'signal_connect': ('#fab387', '#11111b', 'SIGNAL'),     # Peach
            'method_call': ('#89dceb', '#11111b', 'CALL'),          # Sky
            'property_access': ('#a6e3a1', '#11111b', 'ACCESS')     # Green
        }
        bg, fg, badge_text = colors.get(conn['type'], ('#cba6f7', '#11111b', 'CONN'))
        
        badge = QLabel(badge_text)
        badge.setStyleSheet(f"""
            background-color: {bg};
            color: {fg};
            font-weight: bold;
            font-size: 9px;
            border-radius: 3px;
            padding: 1px 4px;
        """)
        badge.setFixedWidth(55)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(badge)
        
        # Format connection details: source -> target
        src_label = f"{conn['source_role'].upper()}.{conn['source_element']}"
        tgt_label = f"{conn['target_role'].upper()}.{conn['target_element']}"
        arrow = "➔"
        
        text = f"{src_label} {arrow} {tgt_label}"
        text_label = QLabel(text)
        text_label.setStyleSheet("color: #cdd6f4; font-size: 11px; font-weight: 500;")
        layout.addWidget(text_label)
        layout.addStretch()


class EditorView(QMainWindow):
    """
    Main View representing the high-fidelity dark-mode MVC Editor IDE.
    Contains layout logic for Explorer tree, Split Editors, Connections list, and Console.
    """
    # Signals for Controller actions
    open_folder_triggered = pyqtSignal()
    save_all_triggered = pyqtSignal()
    run_triggered = pyqtSignal()
    stop_triggered = pyqtSignal()
    file_selected = pyqtSignal(str)
    connection_double_clicked = pyqtSignal(dict)
    create_sibling_requested = pyqtSignal(str, str) # role, source_path
    sync_nav_toggled = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MVC Sync Editor")
        self.resize(1200, 800)
        self.init_ui()

    def init_ui(self):
        # Premium Catppuccin Mocha stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e2e;
            }
            QWidget {
                color: #cdd6f4;
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
            }
            QSplitter::handle {
                background-color: #313244;
            }
            QSplitter::handle:horizontal {
                width: 4px;
            }
            QSplitter::handle:vertical {
                height: 4px;
            }
            
            /* File tree and sidebar styling */
            QTreeView {
                background-color: #181825;
                border: 1px solid #313244;
                border-radius: 6px;
                padding: 4px;
                color: #cdd6f4;
            }
            QTreeView::item {
                padding: 4px 6px;
                border-radius: 4px;
            }
            QTreeView::item:hover {
                background-color: #313244;
            }
            QTreeView::item:selected {
                background-color: #45475a;
                color: #f5c2e7;
                font-weight: 500;
            }
            QHeaderView::section {
                background-color: #11111b;
                color: #a6adc8;
                padding: 4px;
                border: 1px solid #313244;
                font-size: 11px;
            }

            /* Inspector Sidebar */
            QListWidget {
                background-color: #181825;
                border: 1px solid #313244;
                border-radius: 6px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 2px;
                border-bottom: 1px solid #1e1e2e;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: #313244;
            }
            QListWidget::item:selected {
                background-color: #45475a;
            }

            /* Console Text Box */
            QTextEdit#ConsoleOut {
                background-color: #11111b;
                color: #a6e3a1;
                font-family: 'Consolas', monospace;
                font-size: 12px;
                border: 1px solid #313244;
                border-radius: 6px;
                padding: 8px;
            }

            /* Menu and Tool bars */
            QMenuBar {
                background-color: #11111b;
                border-bottom: 1px solid #313244;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 6px 12px;
            }
            QMenuBar::item:selected {
                background-color: #313244;
                border-radius: 4px;
            }
            QMenu {
                background-color: #181825;
                border: 1px solid #313244;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #313244;
                color: #f5c2e7;
            }
            
            QToolBar {
                background-color: #181825;
                border-bottom: 1px solid #313244;
                spacing: 8px;
                padding: 4px 10px;
            }
            QToolButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
                font-weight: 500;
            }
            QToolButton:hover {
                background-color: #313244;
            }

            /* Status Bar */
            QStatusBar {
                background-color: #11111b;
                color: #a6adc8;
                border-top: 1px solid #313244;
            }
            
            /* Labels */
            QLabel {
                font-size: 12px;
            }
        """)

        # Main layout splitting vertical sections
        self.vertical_splitter = QSplitter(Qt.Orientation.Vertical)
        self.setCentralWidget(self.vertical_splitter)

        # Top section: Sidebar + Editors + Inspector
        self.top_horizontal_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.vertical_splitter.addWidget(self.top_horizontal_splitter)

        # 1. Left Sidebar: Workspace Folder Tree
        self.sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(self.sidebar_widget)
        sidebar_layout.setContentsMargins(6, 6, 6, 6)
        sidebar_layout.setSpacing(6)
        
        sidebar_header = QLabel("WORKSPACE")
        sidebar_header.setStyleSheet("color: #b4befe; font-weight: bold; font-size: 11px; letter-spacing: 1px;")
        sidebar_layout.addWidget(sidebar_header)
        
        self.open_dir_btn = QPushButton("Open Folder")
        self.open_dir_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.open_dir_btn.setStyleSheet("""
            QPushButton {
                background-color: #89b4fa;
                color: #11111b;
                font-size: 11px;
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #b4befe;
            }
        """)
        self.open_dir_btn.clicked.connect(self.open_folder_triggered.emit)
        sidebar_layout.addWidget(self.open_dir_btn)

        self.dir_tree = QTreeView()
        self.dir_tree.setHeaderHidden(True)
        self.dir_model = QFileSystemModel()
        self.dir_model.setFilter(QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.NoDotAndDotDot)
        self.dir_model.setNameFilters(["*.py", "*.txt", "*.md", "*.json"])
        self.dir_model.setNameFilterDisables(False)
        self.dir_tree.setModel(self.dir_model)
        self.dir_tree.doubleClicked.connect(self._on_tree_item_double_clicked)
        
        sidebar_layout.addWidget(self.dir_tree)
        self.top_horizontal_splitter.addWidget(self.sidebar_widget)

        # 2. Central Split Editors (Model, View, Controller)
        self.editors_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.top_horizontal_splitter.addWidget(self.editors_splitter)

        # Initialize the 3 editor columns
        self.model_pane = EditorPane('model', 'Model', '#a6e3a1', self)       # Green
        self.view_pane = EditorPane('view', 'View', '#f5c2e7', self)         # Pink
        self.controller_pane = EditorPane('controller', 'Controller', '#89b4fa', self) # Blue
        
        # Connect creation handlers inside panels to main layout signals
        self.model_pane.create_clicked.connect(self._on_create_sibling_clicked)
        self.view_pane.create_clicked.connect(self._on_create_sibling_clicked)
        self.controller_pane.create_clicked.connect(self._on_create_sibling_clicked)

        self.editors_splitter.addWidget(self.model_pane)
        self.editors_splitter.addWidget(self.view_pane)
        self.editors_splitter.addWidget(self.controller_pane)
        
        # Set even distribution widths initially
        self.editors_splitter.setSizes([400, 400, 400])

        # 3. Right Sidebar: MVC Sync Inspector (Relations list)
        self.inspector_widget = QWidget()
        inspector_layout = QVBoxLayout(self.inspector_widget)
        inspector_layout.setContentsMargins(6, 6, 6, 6)
        inspector_layout.setSpacing(6)
        
        inspector_header = QLabel("MVC SYNC INSPECTOR")
        inspector_header.setStyleSheet("color: #f5c2e7; font-weight: bold; font-size: 11px; letter-spacing: 1px;")
        inspector_layout.addWidget(inspector_header)
        
        self.connections_list = QListWidget()
        self.connections_list.itemDoubleClicked.connect(self._on_connection_double_clicked)
        inspector_layout.addWidget(self.connections_list)
        
        self.top_horizontal_splitter.addWidget(self.inspector_widget)

        # Configure initial horizontal sizes
        self.top_horizontal_splitter.setSizes([200, 800, 200])

        # 4. Bottom Section: Console Subprocess logs
        self.console_widget = QWidget()
        console_layout = QVBoxLayout(self.console_widget)
        console_layout.setContentsMargins(12, 4, 12, 8)
        console_layout.setSpacing(6)
        
        console_header_layout = QHBoxLayout()
        console_title = QLabel("RUN CONSOLE")
        console_title.setStyleSheet("color: #a6e3a1; font-weight: bold; font-size: 11px; letter-spacing: 1px;")
        console_header_layout.addWidget(console_title)
        console_header_layout.addStretch()
        
        self.run_btn = QPushButton("Run Application")
        self.run_btn.setStyleSheet("""
            QPushButton {
                background-color: #a6e3a1;
                color: #11111b;
                font-size: 10px;
                font-weight: bold;
                padding: 3px 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #cdd6f4;
            }
        """)
        self.run_btn.clicked.connect(self.run_triggered.emit)
        console_header_layout.addWidget(self.run_btn)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f38ba8;
                color: #11111b;
                font-size: 10px;
                font-weight: bold;
                padding: 3px 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #cdd6f4;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_triggered.emit)
        console_header_layout.addWidget(self.stop_btn)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #45475a;
                color: #cdd6f4;
                font-size: 10px;
                font-weight: bold;
                padding: 3px 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #585b70;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_console)
        console_header_layout.addWidget(self.clear_btn)
        
        console_layout.addLayout(console_header_layout)
        
        self.console_out = QTextEdit()
        self.console_out.setObjectName("ConsoleOut")
        self.console_out.setReadOnly(True)
        self.console_out.setPlaceholderText("Execute code to see subprocess console outputs here...")
        console_layout.addWidget(self.console_out)
        
        self.vertical_splitter.addWidget(self.console_widget)
        
        # Configure initial vertical sizes: 80% Top, 20% Bottom Console
        self.vertical_splitter.setSizes([600, 150])

        # 5. Menus and Toolbars
        self.create_menu_and_toolbar()

        # 6. Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def create_menu_and_toolbar(self):
        # Menus
        menu_bar = self.menuBar()
        
        file_menu = menu_bar.addMenu("File")
        open_dir_action = QAction("Open Workspace Folder...", self)
        open_dir_action.triggered.connect(self.open_folder_triggered.emit)
        file_menu.addAction(open_dir_action)
        
        save_action = QAction("Save All (Ctrl+S)", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_all_triggered.emit)
        file_menu.addAction(save_action)
        
        run_menu = menu_bar.addMenu("Run")
        run_action = QAction("Run Program (F5)", self)
        run_action.setShortcut("F5")
        run_action.triggered.connect(self.run_triggered.emit)
        run_menu.addAction(run_action)
        
        stop_action = QAction("Stop Running", self)
        stop_action.triggered.connect(self.stop_triggered.emit)
        run_menu.addAction(stop_action)

        # Toolbar
        self.toolbar = QToolBar("Editor Actions")
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)
        
        # Open workspace folder button
        open_folder_act = QAction("Open Folder", self)
        open_folder_act.triggered.connect(self.open_folder_triggered.emit)
        self.toolbar.addAction(open_folder_act)
        
        # Save all button
        save_all_act = QAction("Save All (Ctrl+S)", self)
        save_all_act.triggered.connect(self.save_all_triggered.emit)
        self.toolbar.addAction(save_all_act)
        
        self.toolbar.addSeparator()
        
        # Run / Stop buttons
        self.run_action_tb = QAction("Run App", self)
        self.run_action_tb.triggered.connect(self.run_triggered.emit)
        self.toolbar.addAction(self.run_action_tb)

        self.stop_action_tb = QAction("Stop", self)
        self.stop_action_tb.setEnabled(False)
        self.stop_action_tb.triggered.connect(self.stop_triggered.emit)
        self.toolbar.addAction(self.stop_action_tb)
        
        self.toolbar.addSeparator()

        # Auto-sync navigation toggle
        self.sync_nav_checkbox = QCheckBox("Auto-Sync Navigation")
        self.sync_nav_checkbox.setChecked(True)
        self.sync_nav_checkbox.setStyleSheet("margin-left: 10px; font-size: 11px;")
        self.sync_nav_checkbox.stateChanged.connect(self._on_sync_toggled)
        self.toolbar.addWidget(self.sync_nav_checkbox)

    # Handlers & Slots
    def load_workspace(self, path: str):
        """
        Sets the root directory of the workspace explorer file tree.
        """
        self.dir_model.setRootPath(path)
        self.dir_tree.setRootIndex(self.dir_model.index(path))
        self.status_bar.showMessage(f"Loaded workspace: {path}")

    def _on_tree_item_double_clicked(self, index: QModelIndex):
        path = self.dir_model.filePath(index)
        if not self.dir_model.isDir(index):
            self.file_selected.emit(path)

    def _on_create_sibling_clicked(self, role: str):
        # We need to construct the path. Let's find one of the sibling paths to base off of.
        # The controller will handle the exact path resolution, so we pass role and active file.
        # We can find the current loaded files
        active_paths = [self.model_pane.file_label.text(), self.view_pane.file_label.text(), self.controller_pane.file_label.text()]
        # Filter placeholders out
        valid_paths = [p for p in active_paths if p and p != "No File Loaded"]
        if valid_paths:
            # We pass the role to create and the base filename
            self.create_sibling_requested.emit(role, valid_paths[0])

    def populate_connections(self, connections: list):
        """
        Populates the Inspector list with cross-references.
        """
        self.connections_list.clear()
        for conn in connections:
            item = QListWidgetItem(self.connections_list)
            # Size hint to give spacing
            item.setSizeHint(ConnectionItemWidget(conn).sizeHint())
            self.connections_list.addItem(item)
            
            # Set the custom widget
            widget = ConnectionItemWidget(conn, self.connections_list)
            self.connections_list.setItemWidget(item, widget)

    def _on_connection_double_clicked(self, item: QListWidgetItem):
        widget = self.connections_list.itemWidget(item)
        if widget and isinstance(widget, ConnectionItemWidget):
            self.connection_double_clicked.emit(widget.conn)

    def _on_sync_toggled(self, state):
        self.sync_nav_toggled.emit(state == 2) # 2 corresponds to Checked in Qt

    def append_console_text(self, text: str, is_error: bool = False):
        self.console_out.moveCursor(self.console_out.textCursor().MoveOperation.End)
        color = "#f38ba8" if is_error else "#a6e3a1"
        self.console_out.insertHtml(f'<span style="color: {color};">{text.replace("\n", "<br>")}</span>')
        self.console_out.moveCursor(self.console_out.textCursor().MoveOperation.End)

    def clear_console(self):
        self.console_out.clear()

    def set_running_state(self, running: bool):
        self.run_btn.setEnabled(not running)
        self.run_action_tb.setEnabled(not running)
        self.stop_btn.setEnabled(running)
        self.stop_action_tb.setEnabled(running)

    def show_status(self, message: str):
        self.status_bar.showMessage(message, 4000)
