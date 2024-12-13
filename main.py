from gui.main_window import MainWindow
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

def main():
    app = ttk.Window(themename="flatly")  # Set the theme here
    MainWindow(app)  # Initialize your main window
    app.mainloop()

if __name__ == "__main__":
    main()
