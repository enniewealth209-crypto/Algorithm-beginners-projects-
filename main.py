import os
import time
from logic import CountryLogic
from ui import CountryUI, SplashScreen
import customtkinter as ctk

import sys

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def main():
    """
    Main entry point for the Global Country Explorer application.
    Features a professional splash screen startup.
    """
    # Create the root app window
    # In CustomTkinter, the first window created is the root.
    # We initialize the main app logic and UI, then hide it for the splash.
    
    # Define paths
    DATA_PATH = get_resource_path(os.path.join("data", "countries.csv"))
    
    # Initialize logic first
    try:
        logic = CountryLogic(DATA_PATH)
    except Exception as e:
        print(f"Error initializing country database: {e}")
        return
    
    # Create Main UI (it will start hidden because of self.withdraw() in its __init__)
    app = CountryUI(logic)
    
    # Show Splash Screen as a Toplevel of the main app
    splash = SplashScreen()
    
    # Initialization simulation with progress
    splash.update_progress(0.2, "Loading core modules...")
    app.after(500, lambda: splash.update_progress(0.4, "Connecting to database..."))
    app.after(1000, lambda: splash.update_progress(0.7, "Preparing modern interface..."))
    app.after(1500, lambda: splash.update_progress(0.9, "Ready!"))
    
    def start_app():
        splash.destroy()
        app.deiconify() # Show the main window
        
    app.after(2000, start_app)
    
    # Start the event loop
    app.mainloop()

if __name__ == "__main__":
    main()
