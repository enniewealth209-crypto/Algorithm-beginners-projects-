import PyInstaller.__main__
import os
import customtkinter

# Get the path to customtkinter
ctk_path = os.path.dirname(customtkinter.__file__)

# Define the build parameters
PyInstaller.__main__.run([
    'main.py',                    # Entry point
    '--name=CountryExplorer',      # Name of the .exe
    '--onefile',                   # Single executable file
    '--noconsole',                 # No command prompt window
    '--clean',                     # Clean cache before build
    # Add our data folder (CSV file)
    f'--add-data=data{os.pathsep}data',
    # Add customtkinter library data
    f'--add-data={ctk_path}{os.pathsep}customtkinter',
    # Ensure dependencies are found
    '--hidden-import=PIL.Image',
    '--hidden-import=PIL.ImageTk',
    '--hidden-import=requests',
    '--hidden-import=pycountry',
])

print("\n--- Build process complete! ---")
print("Your executable can be found in the 'dist' folder.")
