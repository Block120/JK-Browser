# /// script
# dependencies = [
#     "PyQt6",
#     "pyqt6-webengine",
#     "psutil",
#     "pyqtdarktheme",
# ]
# ///
"""
 * COPYRIGHT (c) 2026 JKSW CO. LICENSED UNDER THE GNU GENERAL PUBLIC LICENSE VERSION 3.0
 @version 0.1
 @author JKSW Co.
 @author Jonah Gorski
 @author Kirin Goda
 @author JONAH GORSKI/ITSAGORSKI1
 @author KIRIN GODA/BLOCK120
 @license GNU-GPL-3.0
"""
import sys, os

os.environ["QTWEBENGINE_REMOTE_DEBUGGING"] = "9222"

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QAction, QKeySequence, QShortcut
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QApplication, QLineEdit, QMainWindow, QStyle, QToolBar, QTabWidget, QWidget, QVBoxLayout, QLabel, QPushButton
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSlot
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtWebEngineCore import QWebEnginePage

import tlds
import qdarktheme
from settings_bridge import SettingsBridge

class SettingsPage(QWebEnginePage):
    def __init__(self, settings_url, parent=None):
        super().__init__(parent)
        self.settings_url = settings_url

    def acceptNavigationRequest(self, url, navigation_type, is_main_frame):
        return is_main_frame and url == self.settings_url

# Create a main window class
class MainWindow(QMainWindow):
    def setupBrowser(self):
        confFile = open("browser.conf", 'rt')
        confText = confFile.read()
        uvLockFile = open("uv.lock", 'rt')
        uvLockText = uvLockFile.read()

        if "searchEngine = 'Google (google.com)'" in confText or "searchEngine = " not in confText:
            self.defaultSearchEngine = "google"
            self.defaultEngineSearchUrl = "google.com/search?q="
        elif "searchEngine = 'Yahoo (yahoo.com)" in confText:
            self.defaultSearchEngine = "yahoo"
            self.defaultEngineSearchUrl = 'search.yahoo.com/search?p='
        self.confText = confText
        self.uvLockText = uvLockText
    # Constructor of this class
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("JK-Browser")
        self.setupBrowser()
        # To provide a widget for viewing and editing web documents:
        self.browser = QWebEngineView()

        self.normal_page = QWebEnginePage(self)
        self.browser.setPage(self.normal_page)

        settings_path = Path(__file__).resolve().parent / "settings.html"
        self.settings_url = QUrl.fromLocalFile(str(settings_path))
        self.settings_page = SettingsPage(self.settings_url, self)

        self.settings_bridge = SettingsBridge(self)
        self.settings_channel = QWebChannel(self.settings_page)
        self.settings_channel.registerObject("settings", self.settings_bridge)
        self.settings_page.setWebChannel(self.settings_channel)


        self.devtools_window = None
        # Bind F12 key to toggle Developer Tools panel
        self.devtools_shortcut = QShortcut(QKeySequence("F12"), self)
        self.devtools_shortcut.activated.connect(self.toggle_developer_tools)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        mainLayout = QVBoxLayout(central_widget)
        mainLayout.addWidget(self.browser)

        # To set default browser homepage as google homepage:
        if self.defaultSearchEngine == "google":
            self.browser.setUrl(QUrl("https://www.google.com"))
        elif self.defaultSearchEngine == "yahoo":
            self.browser.setUrl(QUrl("https://yahoo.com"))
        # To set browser as central widget of main window:
        # To open browser in a maximized window:
        self.showMaximized()

        # To create a navigation bar:
        navbar = QToolBar()
        navbar.adjustSize()
        # To add the navigation bar to the browser:
        self.addToolBar(navbar)

        # To add back button within navigation bar:
        back_btn = QAction(
            self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowBack),
            'Back',
            self,
        )
        back_btn.triggered.connect(self.go_back)
        navbar.addAction(back_btn)

        # To add forward button within navigation bar:
        forward_btn = QAction(
            self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowForward),
            'Forward',
            self,
        )
        forward_btn.triggered.connect(self.browser.forward)
        navbar.addAction(forward_btn)

        # To add reload button within navigation bar:
        reload_btn = QAction('⟳', self)
        reload_btn.triggered.connect(self.browser.reload)
        navbar.addAction(reload_btn)

        # To add URL bar within navigation bar:
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.open_url)
        navbar.addWidget(self.url_bar)
        self.browser.urlChanged.connect(self.update_url)

    def checkIfURL(self, url):
        if "jk-browser://" in url or "jk-b://" in url:
            if url == "jk-browser://exit" or url == "jk-b://exit":
                QApplication.quit()
                return "exit"
            elif url == "jk-browser://version" or url == "jk-b://version":
                return "version"
            elif url == "jk-browser://settings" or url == "jk-b://settings":
                return "settings"
        if " " in url or "." not in url:
            return self.defaultEngineSearchUrl + url
        elif " " not in url and "." in url:
            return url

    # To navigate to desired URL specified within URL bar:
    def open_url(self):
        url = self.url_bar.text()
        urlValid = str(self.checkIfURL(url))
        url = urlValid
        if url == "exit":
            return
        if url == "settings":
            self.showSettings()
            return
        self.browser.setPage(self.normal_page)
        if url == "version":
            version = ""
            if self.uvLockText.find("version = ") != -1:
                version = self.uvLockText[self.uvLockText.find("version = ")+10:self.uvLockText.find("revision")-1]
            else:
                version = "version not found"
            self.browser.setHtml(f"""
                <!DOCTYPE html>
                <html>
                    <head>
                        <title>Version</title>
                        <style>
                            * {{
                                font-family: monospace;
                                background-color: #000000;
                                color: #ffffff
                            }}
                        </style>
                    </head>
                    <body>
                        <p>
                            {version}<br>
                            COPYRIGHT (c) 2026 JKSW Co. LICENSED UNDER THE GNU GENERAL PUBLIC LICENSE v3.0
                        </p>
                    </body>
                </html>
                """)
            return
        if "http://" not in url and "https://" not in url:
            self.browser.setUrl(QUrl("https://" + url))
        else:
            self.browser.setUrl(QUrl(url))

    def showSettings(self):
        self.browser.setPage(self.settings_page)
        self.browser.setUrl(self.settings_url)
        self.url_bar.setText("jk-b://settings")

    # To update the URL bar contents when navigated from one page to another:
    def update_url(self, q):
        if self.browser.page() is self.settings_page:
            self.url_bar.setText("jk-b://settings")
        else:
            self.url_bar.setText(q.toString())

    def toggle_developer_tools(self):
        if self.devtools_window and self.devtools_window.isVisible():
            self.devtools_window.close()
            return

        # Create or update inspector window targeting the active page profile
        self.devtools_window = QMainWindow(self)
        self.devtools_window.setWindowTitle("Developer Tools")
        self.devtools_window.resize(900, 600)

        inspector_view = QWebEngineView()
        self.devtools_window.setCentralWidget(inspector_view)

        # Link current page to the inspection engine
        self.browser.page().setDevToolsPage(inspector_view.page())
        self.devtools_window.show()

    def go_back(self):
        if self.browser.page() is self.settings_page:
            self.browser.setPage(self.normal_page)
            self.update_url(self.normal_page.url())
        else:
            self.browser.back()


# To call constructor of the C++ class QApplication:
# Here, sys.argv is used to initialize the QT application
QApplication.setApplicationName("JK-Browser")
QApplication.setApplicationDisplayName("JK-Browser")
app = QApplication(sys.argv)
qdarktheme.setup_theme()
# To create an object of MainWindow class defined above:
window = MainWindow()
# To run the main event loop and wait until exit() is called:
app.exec()
