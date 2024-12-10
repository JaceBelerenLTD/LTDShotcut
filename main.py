import tkinter as tk
from gui.main_window import MainWindow

def main():
    """
    Entry point of the application.
    Initializes the root window and starts the GUI.
    """
    root = tk.Tk()  # Create the root Tkinter window
    app = MainWindow(root)  # Pass the root window to MainWindow
    root.mainloop()  # Start the Tkinter event loop

if __name__ == "__main__":
    main()
