import customtkinter as ctk
import tkinter as tk
from logic import CountryLogic
from PIL import Image, ImageTk
import requests
from io import BytesIO
import json
import winsound # For system sounds on Windows
import os
import threading

import sys
import webbrowser

# Initial theme setup
def get_settings_path():
    """ Get persistent path for settings.json """
    if getattr(sys, 'frozen', False):
        # If frozen (packaged), settings should be next to the .exe
        return os.path.join(os.path.dirname(sys.executable), "settings.json")
    return "settings.json"

def get_saved_theme():
    try:
        with open(get_settings_path(), "r") as f:
            return json.load(f).get("theme", "System")
    except:
        return "System"

ctk.set_appearance_mode(get_saved_theme())
ctk.set_default_color_theme("blue")

class SplashScreen(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.title("Loading...")
        self.geometry("400x300")
        self.overrideredirect(True) # Remove title bar
        
        # Center the window
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (400 // 2)
        y = (screen_height // 2) - (300 // 2)
        self.geometry(f"400x300+{x}+{y}")

        self.configure(fg_color="#1a1a1a")
        
        self.label = ctk.CTkLabel(self, text="🌍\nGlobal Country Explorer", font=("Segoe UI", 28, "bold"), text_color="#3498db")
        self.label.pack(expand=True, pady=(40, 0))
        
        self.progress = ctk.CTkProgressBar(self, width=300, height=12, corner_radius=6, progress_color="#3498db")
        self.progress.pack(pady=30)
        self.progress.set(0)
        
        self.status_label = ctk.CTkLabel(self, text="Initializing professional suite...", font=("Segoe UI", 12), text_color="#95a5a6")
        self.status_label.pack(pady=(0, 40))

    def update_progress(self, value, status):
        self.progress.set(value)
        self.status_label.configure(text=status)
        self.update()

class CountryUI(ctk.CTk):
    """
    A professional, modern GUI for the Global Country Explorer.
    Features a sidebar, 3D effects, animations, and dark mode support.
    """
    def __init__(self, logic: CountryLogic):
        super().__init__()
        self.logic = logic
        self.withdraw() # Start hidden for splash screen flow
        
        # --- Window Configuration ---
        self.title("Global Country Explorer")
        self.geometry("900x650")
        
        # --- Main Layout Grid ---
        # Column 0: Sidebar (fixed width)
        # Column 1: Main Content (expandable)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.setup_sidebar()

        # --- Main Content Area ---
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(1, weight=1)

        self.setup_header()
        self.setup_results_area()
        self.setup_status_bar()
        
        # --- Autocomplete Listbox ---
        self.suggestion_list = tk.Listbox(
            self, 
            height=5, 
            font=("Segoe UI", 12),
            background="white",
            foreground="black",
            relief="solid",
            borderwidth=1,
            highlightthickness=0,
            selectbackground="#1a73e8",
            selectforeground="white"
        )
        self.suggestion_list.bind("<<ListboxSelect>>", self.on_suggestion_select)

        # Initial State
        self.search_history = []
        self.current_data = None
        self.hide_results()

    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1) # Spacer

        # Logo/Title
        self.logo_label = ctk.CTkLabel(self.sidebar, text="Country\nExplorer", font=("Segoe UI", 24, "bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Search History Section
        self.history_label = ctk.CTkLabel(self.sidebar, text="Recent Searches", font=("Segoe UI", 14, "bold"))
        self.history_label.grid(row=1, column=0, padx=20, pady=(20, 10), sticky="w")
        
        self.history_scroll = ctk.CTkScrollableFrame(self.sidebar, label_text="", height=300)
        self.history_scroll.grid(row=2, column=0, padx=10, pady=0, sticky="nsew")
        
        # Appearance Mode
        self.appearance_label = ctk.CTkLabel(self.sidebar, text="Appearance Mode:", anchor="w")
        self.appearance_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_optionemenu = ctk.CTkOptionMenu(
            self.sidebar, values=["Light", "Dark", "System"],
            command=self.change_appearance_mode
        )
        self.appearance_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 20))
        self.appearance_optionemenu.set(get_saved_theme())

    def setup_status_bar(self):
        self.status_bar = ctk.CTkFrame(self, height=25, corner_radius=0)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        self.status_text = ctk.CTkLabel(self.status_bar, text="Ready", font=("Segoe UI", 10))
        self.status_text.pack(side="left", padx=20)
        
        self.db_status = ctk.CTkLabel(self.status_bar, text=f"Database: {len(self.logic.country_names)} countries", font=("Segoe UI", 10))
        self.db_status.pack(side="right", padx=20)

    def setup_header(self):
        self.header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.header_frame.grid_columnconfigure(0, weight=1)

        # Search Container
        self.search_bar = ctk.CTkEntry(
            self.header_frame, 
            placeholder_text="🔍 Search for a country...",
            height=45,
            font=("Segoe UI", 16)
        )
        self.search_bar.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.search_bar.bind("<KeyRelease>", self.on_typing)
        self.search_bar.bind("<Return>", lambda e: self.search_country())

        self.search_btn = ctk.CTkButton(
            self.header_frame, text="Search", width=100, height=45,
            font=("Segoe UI", 14, "bold"), command=self.search_country
        )
        self.search_btn.grid(row=0, column=1, padx=5)

        self.clear_btn = ctk.CTkButton(
            self.header_frame, text="Clear", width=80, height=45,
            fg_color="gray", hover_color="#555555",
            font=("Segoe UI", 14), command=self.clear_all
        )
        self.clear_btn.grid(row=0, column=2, padx=5)

        # Error Label
        self.error_label = ctk.CTkLabel(self.header_frame, text="", text_color="#e74c3c", font=("Segoe UI", 12))
        self.error_label.grid(row=1, column=0, columnspan=3, pady=(5, 0), sticky="w")

    def setup_results_area(self):
        # 3D Effect Container
        self.results_container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.results_container.grid(row=1, column=0, sticky="nsew")
        self.results_container.grid_columnconfigure(0, weight=1)

        # Shadow
        self.shadow_frame = ctk.CTkFrame(self.results_container, corner_radius=20, fg_color="#d0d0d0")
        self.shadow_frame.grid(row=0, column=0, padx=(8, 0), pady=(8, 0), sticky="nsew")

        # Main Card
        self.result_card = ctk.CTkFrame(self.results_container, corner_radius=20, border_width=1, border_color="#3498db")
        self.result_card.grid(row=0, column=0, padx=(0, 8), pady=(0, 8), sticky="nsew")
        self.result_card.grid_columnconfigure((0, 1), weight=1)

        # --- Left Column: Info ---
        self.info_panel = ctk.CTkFrame(self.result_card, fg_color="transparent")
        self.info_panel.grid(row=0, column=0, padx=30, pady=30, sticky="nsew")

        self.name_label = ctk.CTkLabel(self.info_panel, text="", font=("Segoe UI", 32, "bold"), text_color="#2980b9")
        self.name_label.pack(anchor="w", pady=(0, 20))

        self.details_frame = ctk.CTkFrame(self.info_panel, fg_color="transparent")
        self.details_frame.pack(fill="both", expand=True)

        self.labels = {}
        icons = {"capital": "🏛️", "continent": "🌍", "population": "👥"}
        for field, icon in icons.items():
            f = ctk.CTkFrame(self.details_frame, fg_color="transparent")
            f.pack(fill="x", pady=8)
            
            ctk.CTkLabel(f, text=f"{icon} {field.capitalize()}:", font=("Segoe UI", 14, "bold"), width=120, anchor="w").pack(side="left")
            
            color = "#27ae60" if field == "population" else None
            size = 20 if field == "population" else 15
            self.labels[field] = ctk.CTkLabel(f, text="", font=("Segoe UI", size, "bold" if field == "population" else "normal"), text_color=color, anchor="w")
            self.labels[field].pack(side="left", fill="x")

        # --- Actions Area ---
        self.actions_frame = ctk.CTkFrame(self.info_panel, fg_color="transparent")
        self.actions_frame.pack(fill="x", pady=(20, 0))

        self.copy_btn = ctk.CTkButton(
            self.actions_frame, text="📋 Copy Info", width=100, height=32,
            font=("Segoe UI", 12), command=self.copy_to_clipboard,
            fg_color="#34495e", hover_color="#2c3e50"
        )
        self.copy_btn.pack(side="left", padx=(0, 10))

        self.export_btn = ctk.CTkButton(
            self.actions_frame, text="💾 Export JSON", width=100, height=32,
            font=("Segoe UI", 12), command=self.export_country_data,
            fg_color="#34495e", hover_color="#2c3e50"
        )
        self.export_btn.pack(side="left")

        # --- Right Column: Visuals ---
        self.visuals_panel = ctk.CTkFrame(self.result_card, fg_color="transparent")
        self.visuals_panel.grid(row=0, column=1, padx=30, pady=30, sticky="nsew")

        self.flag_label = ctk.CTkLabel(self.visuals_panel, text="")
        self.flag_label.pack(pady=(0, 20))

        self.map_frame = ctk.CTkFrame(self.visuals_panel, fg_color="#ecf0f1", corner_radius=15, width=320, height=220)
        self.map_frame.pack()
        self.map_frame.pack_propagate(False)
        self.map_label = ctk.CTkLabel(self.map_frame, text="Loading Map...", font=("Segoe UI", 12))
        self.map_label.pack(expand=True)

        self.google_maps_btn = ctk.CTkButton(
            self.visuals_panel, text="🌐 View on Google Maps", width=200, height=32,
            font=("Segoe UI", 12), command=self.open_google_maps,
            fg_color="#3498db", hover_color="#2980b9"
        )

    def change_appearance_mode(self, new_mode):
        ctk.set_appearance_mode(new_mode)
        # Update suggestion list colors based on theme
        if new_mode == "Dark":
            self.suggestion_list.configure(bg="#2c3e50", fg="white")
        else:
            self.suggestion_list.configure(bg="white", fg="black")
        
        # Save preference in a persistent location
        try:
            with open(get_settings_path(), "w") as f:
                json.dump({"theme": new_mode}, f)
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def on_typing(self, event):
        query = self.search_bar.get().strip()
        if not query:
            self.suggestion_list.place_forget()
            return
            
        suggestions = self.logic.get_suggestions(query)
        if suggestions:
            self.update_idletasks()
            # Position relative to main_content
            x = self.header_frame.winfo_x() + self.search_bar.winfo_x() + 20 # Offset for sidebar
            y = self.header_frame.winfo_y() + self.search_bar.winfo_y() + self.search_bar.winfo_height() + 20
            w = self.search_bar.winfo_width()
            
            self.suggestion_list.delete(0, tk.END)
            for s in suggestions[:5]:
                self.suggestion_list.insert(tk.END, s)
            
            self.suggestion_list.place(x=x, y=y, width=w)
            self.suggestion_list.lift()
        else:
            self.suggestion_list.place_forget()

    def on_suggestion_select(self, event):
        selection = self.suggestion_list.curselection()
        if not selection: return
        selected = self.suggestion_list.get(selection[0])
        self.search_bar.delete(0, tk.END)
        self.search_bar.insert(0, selected)
        self.suggestion_list.place_forget()
        self.search_country()

    def search_country(self):
        self.suggestion_list.place_forget()
        query = self.search_bar.get().strip()
        if not query: return

        self.status_text.configure(text=f"Searching for '{query}'...")
        result = self.logic.get_country_info(query)
        if result:
            self.current_data = result
            self.error_label.configure(text="")
            winsound.MessageBeep(winsound.MB_OK)
            self.show_results(result)
            self.add_to_history(query)
            self.status_text.configure(text=f"Showing results for {result['name']}")
        else:
            self.current_data = None
            self.hide_results()
            winsound.MessageBeep(winsound.MB_ICONERROR)
            self.error_label.configure(text=f"Country '{query}' not found. Please check spelling.")
            self.status_text.configure(text="Country not found")

    def copy_to_clipboard(self):
        if not self.current_data: return
        
        data_str = (
            f"Country: {self.current_data['name']}\n"
            f"Capital: {self.current_data['capital']}\n"
            f"Continent: {self.current_data['continent']}\n"
            f"Population: {self.current_data['population']:,}"
        )
        self.clipboard_clear()
        self.clipboard_append(data_str)
        self.status_text.configure(text="Info copied to clipboard!")
        self.after(2000, lambda: self.status_text.configure(text=f"Showing results for {self.current_data['name']}"))

    def export_country_data(self):
        if not self.current_data: return
        
        file_path = tk.filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"{self.current_data['name'].lower()}_info.json"
        )
        
        if file_path:
            try:
                with open(file_path, "w") as f:
                    json.dump(self.current_data, f, indent=4)
                self.status_text.configure(text=f"Exported to {os.path.basename(file_path)}")
            except Exception as e:
                self.status_text.configure(text=f"Export failed: {str(e)}")

    def show_results(self, data):
        self.name_label.configure(text=data['name'])
        self.labels['capital'].configure(text=data['capital'])
        self.labels['continent'].configure(text=data['continent'])
        
        try:
            pop = int(data['population'])
            formatted_pop = f"{pop:,}"
        except:
            formatted_pop = str(data['population'])
            
        self.labels['population'].configure(text=formatted_pop)
        
        # Reset card for animation
        self.animate_slide_in(120)
        self.results_container.grid()

        self.flag_label.configure(image=None, text="⏳ Loading Flag...")
        self.map_label.configure(image=None, text="⏳ Loading Map...")

        if data.get('country_code'):
            threading.Thread(target=self.load_flag, args=(data['country_code'],), daemon=True).start()
        
        threading.Thread(target=self.load_map, args=(data['name'],), daemon=True).start()

    def hide_results(self):
        self.name_label.configure(text="")
        self.flag_label.configure(image=None, text="")
        self.map_label.configure(image=None, text="No Map Loaded")
        for lbl in self.labels.values():
            lbl.configure(text="")
        self.results_container.grid_remove()

    def load_flag(self, country_code):
        self.status_text.configure(text="Loading national flag...")
        try:
            url = f"https://flagcdn.com/w160/{country_code}.png"
            response = requests.get(url, timeout=5)
            img = Image.open(BytesIO(response.content))
            img = img.resize((160, 100), Image.LANCZOS)
            flag_image = ImageTk.PhotoImage(img)
            
            # Update UI from thread using .after()
            self.after(0, lambda: self._update_flag_ui(flag_image))
        except:
            self.after(0, lambda: self.flag_label.configure(image=None, text="Flag not found"))
            self.after(0, lambda: self.status_text.configure(text="Ready"))

    def _update_flag_ui(self, flag_image):
        self.flag_image = flag_image # Keep reference
        self.flag_label.configure(image=self.flag_image, text="")
        if self.current_data:
            self.status_text.configure(text=f"Showing results for {self.current_data['name']}")

    def load_map(self, country_name):
        self.status_text.configure(text="Fetching map data...")
        try:
            url = f"https://static-maps.yandex.ru/1.x/?lang=en_US&text={country_name}&z=3&l=map&size=320,220"
            response = requests.get(url, timeout=7)
            img = Image.open(BytesIO(response.content))
            map_image = ImageTk.PhotoImage(img)
            
            # Update UI from thread using .after()
            self.after(0, lambda: self._update_map_ui(map_image))
        except:
            self.after(0, lambda: self.map_label.configure(image=None, text="Map not found"))
        self.google_maps_btn.pack(pady=(10, 0))
        self.after(0, lambda: self.status_text.configure(text="Ready"))

    def _update_map_ui(self, map_image):
        self.map_image = map_image # Keep reference
        self.map_label.configure(image=self.map_image, text="")
        self.google_maps_btn.pack_forget()
        if self.current_data:
            self.status_text.configure(text=f"Showing results for {self.current_data['name']}")

    def animate_slide_in(self, current_pady):
        if current_pady > 0:
            current_pady -= 10
            self.results_container.grid(pady=(current_pady, 0))
            self.after(10, lambda: self.animate_slide_in(current_pady))
        else:
            self.results_container.grid(pady=0)

    def open_google_maps(self):
        if not self.current_data: return
        query = self.current_data['name']
        url = f"https://www.google.com/maps/search/?api=1&query={query}"
        webbrowser.open_new_tab(url)
        self.status_text.configure(text=f"Opening Google Maps for {query}...")

    def clear_all(self):
        self.search_bar.delete(0, tk.END)
        self.error_label.configure(text="")
        self.suggestion_list.place_forget()
        self.current_data = None
        self.status_text.configure(text="Ready")
        self.hide_results()

    def add_to_history(self, query):
        if query in self.search_history:
            self.search_history.remove(query)
        self.search_history.insert(0, query)
        if len(self.search_history) > 10:
            self.search_history.pop()
        self.update_history_sidebar()

    def update_history_sidebar(self):
        for widget in self.history_scroll.winfo_children():
            widget.destroy()

        for item in self.search_history:
            btn = ctk.CTkButton(
                self.history_scroll, text=item, anchor="w",
                fg_color="transparent", text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                command=lambda i=item: self.run_history_search(i)
            )
            btn.pack(fill="x", padx=5, pady=2)

    def run_history_search(self, query):
        self.search_bar.delete(0, tk.END)
        self.search_bar.insert(0, query)
        self.search_country()
