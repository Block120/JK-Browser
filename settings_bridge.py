from PyQt6.QtCore import QObject, pyqtSlot

class SettingsBridge(QObject):
    def __init__(self, window):
        super().__init__(window)
        self.window = window

    @pyqtSlot(result=str)
    def getSearchEngine(self):
        return self.window.defaultSearchEngine

    @pyqtSlot(str, result=bool)
    def setSearchEngine(self, engine):
        search_urls = {
            "google": "google.com",
            "yahoo": "search.yahoo.com",
        }

        if engine not in search_urls:
            return False

        self.window.defaultSearchEngine = engine
        self.window.defaultEngineSearchUrl = search_urls[engine]
        return True
