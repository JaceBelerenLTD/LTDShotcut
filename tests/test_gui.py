import unittest
from tkinter import Tk
from gui.main_window import MainWindow

class TestMainWindow(unittest.TestCase):
    def setUp(self):
        self.root = Tk()
        self.app = MainWindow(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_window_title(self):
        self.assertEqual(self.root.title(), "Media Display App")

if __name__ == "__main__":
    unittest.main()
