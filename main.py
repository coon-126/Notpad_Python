import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit,
                             QAction, QFileDialog, QTabWidget,
                             QMessageBox, QStatusBar, QWidget, QTabBar)
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtCore import QFileInfo


class Notepad(QMainWindow):
    UNTITLED = "Untitled"
    STAR = "*"
    PLUS = "+"

    def __init__(self):
        super().__init__()
        self.tabs = None
        self.statusbar = None
        self.initUI()
        self.newFile()
        self.is_dark_mode = False

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Notepad')

        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.closeTab)
        self.tabs.currentChanged.connect(self.updateStatusbar)
        self.tabs.currentChanged.connect(self.tabSelected)
        self.tabs.currentChanged.connect(self.updateCursorPosition)

        self.setCentralWidget(self.tabs)

        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')

        new_file_action = QAction('New', self)
        new_file_action.setShortcut('Ctrl+N')
        new_file_action.triggered.connect(self.newFile)
        file_menu.addAction(new_file_action)

        open_file_action = QAction('Open', self)
        open_file_action.setShortcut('Ctrl+O')
        open_file_action.triggered.connect(self.openFile)
        file_menu.addAction(open_file_action)

        save_file_action = QAction('Save', self)
        save_file_action.setShortcut('Ctrl+S')
        save_file_action.triggered.connect(self.saveFile)
        file_menu.addAction(save_file_action)

        edit_menu = menubar.addMenu('Edit')

        cut_action = QAction('Cut', self)
        cut_action.setShortcut('Ctrl+X')
        cut_action.triggered.connect(lambda: self.getCurrentTextEdit().cut() if self.getCurrentTextEdit() else None)
        edit_menu.addAction(cut_action)

        copy_action = QAction('Copy', self)
        copy_action.setShortcut('Ctrl+C')
        copy_action.triggered.connect(lambda: self.getCurrentTextEdit().copy() if self.getCurrentTextEdit() else None)
        edit_menu.addAction(copy_action)

        paste_action = QAction('Paste', self)
        paste_action.setShortcut('Ctrl+V')
        paste_action.triggered.connect(lambda: self.getCurrentTextEdit().paste() if self.getCurrentTextEdit() else None)
        edit_menu.addAction(paste_action)

        view_menu = menubar.addMenu('View')

        theme_action = QAction('Toggle Theme', self)
        theme_action.triggered.connect(self.toggleTheme)
        view_menu.addAction(theme_action)

    def createNewTextEdit(self):
        text = QTextEdit()
        text.textChanged.connect(self.documentWasModified)
        text.cursorPositionChanged.connect(self.updateCursorPosition)
        return text

    def newFile(self):
        text = self.createNewTextEdit()
        index = self.tabs.insertTab(self.tabs.count() - 1, text, self.UNTITLED)
        self.tabs.setCurrentIndex(index)

    def addPlusButton(self):
        plusButton = QWidget()
        index = self.tabs.addTab(plusButton, self.PLUS)
        self.tabs.tabBar().setTabButton(index, QTabBar.RightSide, None)  # disable close button

    def tabSelected(self, index):
        if self.tabs.tabText(index) == self.PLUS:
            self.newFile()

    def documentWasModified(self):
        self.tabs.setTabText(self.tabs.currentIndex(), f"{self.STAR} {self.tabs.tabText(self.tabs.currentIndex())}")

    def isCurrentTabEmpty(self):
        current_text = self.getCurrentTextEdit()
        return self.tabs.tabText(
            self.tabs.currentIndex()) == self.UNTITLED and not current_text.toPlainText() and not self.STAR in self.tabs.tabText(
            self.tabs.currentIndex())

    def openFile(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open file')

        if fname:
            try:
                with open(fname, 'r') as f:
                    data = f.read()

                if self.isCurrentTabEmpty():
                    self.getCurrentTextEdit().setText(data)
                    self.tabs.setTabText(self.tabs.currentIndex(), QFileInfo(fname).fileName())
                    self.getCurrentTextEdit().document().setModified(False)
                else:
                    text = self.createNewTextEdit()
                    text.setText(data)
                    index = self.tabs.insertTab(self.tabs.count() - 1, text, QFileInfo(fname).fileName())
                    self.tabs.setCurrentIndex(index)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def saveFile(self):
        fname, _ = QFileDialog.getSaveFileName(self, 'Save file')

        if fname:
            try:
                index = self.tabs.currentIndex()
                text = self.tabs.widget(index)
                with open(fname, 'w') as f:
                    f.write(text.toPlainText())
                self.tabs.setTabText(index, QFileInfo(fname).fileName())
                text.document().setModified(False)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def closeTab(self, index):
        if self.tabs.tabText(index) == self.PLUS:  # Prevent closing '+' tab
            return

        if self.tabs.tabText(index).startswith(self.STAR):
            if QMessageBox.question(self, "Unsaved Changes",
                                    "Do you want to save changes to this document before closing?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes) == QMessageBox.Yes:
                self.saveFile()
        self.tabs.removeTab(index)

    def closeEvent(self, event: QCloseEvent):
        QTextEditTabs = [index for index in range(self.tabs.count())
                         if isinstance(self.tabs.widget(index), QTextEdit)]
        while QTextEditTabs:  # Only consider QTextEdit tabs
            if self.tabs.tabText(QTextEditTabs[0]).startswith(self.STAR):
                self.tabs.setCurrentIndex(QTextEditTabs[0])
                if QMessageBox.question(self, "Unsaved Changes",
                                        "Do you want to save changes to your documents before closing?",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes) == QMessageBox.Yes:
                    self.saveFile()
                else:
                    self.tabs.removeTab(QTextEditTabs[0])
            else:
                self.tabs.removeTab(QTextEditTabs[0])
            QTextEditTabs.pop(0)
        event.accept()

    def getCurrentTextEdit(self):
        currentWidget = self.tabs.currentWidget()
        if isinstance(currentWidget, QTextEdit):
            return currentWidget
        return None

    def updateStatusbar(self, index):
        if self.tabs.count() > 1 and self.tabs.tabText(index) != self.PLUS:
            self.statusbar.showMessage(self.tabs.tabText(index))

    def updateCursorPosition(self):
        if self.getCurrentTextEdit():
            cursor = self.getCurrentTextEdit().textCursor()
            line = cursor.blockNumber() + 1
            col = cursor.columnNumber() + 1
            self.statusbar.showMessage(f'Ln {line}, Col {col}', 0)

    def toggleTheme(self):
        light_stylesheet = """
            QWidget { background-color: #FFFFFF; color: #000000; }
            QTextEdit { background-color: #FFFFFF; color: #000000; }
            QTabWidget::pane { border: none; background: #FFFFFF; }
            QTabWidget::tab-bar { left: 5px; }
            QTabBar::tab { background-color: #FFFFFF; color: #000000; border: 1px solid #C4C4C4; padding: 2px; }
            QTabBar::tab:selected { border-color: #9B9B9B; border-bottom-color: #FFFFFF; }
            QTabBar::tab:!selected { margin-top: 2px; }
            QMenuBar::item { background: transparent; }
            QMenuBar::item:selected { background: #CCCCCC; }
            QMenu::item:selected { background: #CCCCCC; }
        """
        dark_stylesheet = """
            QWidget { background-color: #2B2B2B; color: #ECECEC; }
            QTextEdit { background-color: #2B2B2B; color: #ECECEC; }
            QTabWidget::pane { border: none; background: #2B2B2B; }
            QTabWidget::tab-bar { left: 5px; }
            QTabBar::tab { background-color: #2B2B2B; color: #ECECEC; border: 1px solid #4D4D4D; padding: 2px; }
            QTabBar::tab:selected { border-color: #4D4D4D; border-bottom-color: #2B2B2B; }
            QTabBar::tab:!selected { margin-top: 2px; }
            QMenuBar::item { background: transparent; }
            QMenuBar::item:selected { background: #404040; }
            QMenu::item:selected { background: #404040; }
        """

        if self.is_dark_mode:
            self.setStyleSheet(light_stylesheet)
            self.is_dark_mode = False
        else:
            self.setStyleSheet(dark_stylesheet)
            self.is_dark_mode = True


def main():
    app = QApplication(sys.argv)
    notepad = Notepad()
    notepad.addPlusButton()  # Add "+" button at the end
    notepad.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
