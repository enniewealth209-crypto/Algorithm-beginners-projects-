import csv
import tkinter as tk
from tkinter import messagebox, ttk
import webbrowser

# --- Styling Constants ---
BG_COLOR = "#f0f2f5"
SIDEBAR_COLOR = "#ffffff"
CARD_COLOR = "#ffffff"
PRIMARY_COLOR = "#1a73e8"
TEXT_COLOR = "#333333"
HEADER_COLOR = "#1a73e8"
ACCENT_COLOR = "#4caf50"
HOVER_COLOR = "#1557b0"
PLACEHOLDER_COLOR = "#999999"
FONT_MAIN = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_HEADER = ("Segoe UI", 18, "bold")
FONT_SUBHEADER = ("Segoe UI", 12, "bold")
FONT_LINK = ("Segoe UI", 10, "underline")

def load_countries(filename):
    country_names = []
    country_data = {}

    try:
        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if not row or row.get('Country') is None:
                    continue
                name = (row.get('Country') or "").strip()
                capital = (row.get('Capital') or "").strip()
                continent = (row.get('Continent') or "").strip()
                population_str = (row.get('Population') or "0").strip()
                
                # Convert population to integer for sorting
                try:
                    population = int(population_str)
                except ValueError:
                    population = 0
                    
                if name == "":
                    continue
                country_names.append(name)
                country_data[name] = {
                    'Capital': capital,
                    'Continent': continent,
                    'Population': population
                }
    except FileNotFoundError:
        return [], {}

    country_names.sort()
    return country_names, country_data

def binary_search(arr, target):
    low = 0
    high = len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        mid_val = arr[mid]
        if mid_val == target:
            return True
        elif mid_val < target:
            low = mid + 1
        else:
            high = mid - 1
    return False

class CountryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Global Country Explorer")
        self.root.geometry("850x650")
        self.root.configure(bg=BG_COLOR)
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TFrame", background=BG_COLOR)
        self.style.configure("Sidebar.TFrame", background=SIDEBAR_COLOR)
        self.style.configure("Card.TFrame", background=CARD_COLOR, relief="flat")
        
        self.filename = 'countries.csv'
        self.all_country_list, self.country_info = load_countries(self.filename)
        self.current_display_list = list(self.all_country_list)
        self.placeholder = "Search for a country..."
        self.active_filter = None

        if not self.all_country_list:
            messagebox.showerror("Error", f"Could not load data from {self.filename}")
            self.root.destroy()
            return

        self.setup_ui()

    def setup_ui(self):
        # --- Sidebar ---
        self.sidebar = ttk.Frame(self.root, style="Sidebar.TFrame", padding=(10, 20))
        self.sidebar.pack(side="left", fill="y")
        
        ttk.Label(self.sidebar, text="Explorer", font=FONT_SUBHEADER, background=SIDEBAR_COLOR, foreground=HEADER_COLOR).pack(pady=(0, 5))
        
        # Filter Status Label
        self.filter_status = tk.Label(self.sidebar, text="All Countries", font=("Segoe UI", 8), bg=SIDEBAR_COLOR, fg="#888888")
        self.filter_status.pack(pady=(0, 10))

        # Search Box Container
        search_container = tk.Frame(self.sidebar, bg=SIDEBAR_COLOR)
        search_container.pack(fill="x", pady=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_container, textvariable=self.search_var, font=FONT_MAIN, relief="flat", highlightthickness=1, highlightbackground="#cccccc")
        self.search_entry.pack(fill="x", ipady=5)
        
        self.search_entry.insert(0, self.placeholder)
        self.search_entry.config(fg=PLACEHOLDER_COLOR)
        self.search_entry.bind('<FocusIn>', self.on_focus_in)
        self.search_entry.bind('<FocusOut>', self.on_focus_out)
        self.search_entry.bind('<KeyRelease>', self.handle_key_release)
        self.search_entry.bind('<Down>', self.move_suggestion_focus)
        self.search_entry.bind('<Up>', self.move_suggestion_focus)
        self.search_entry.bind('<Return>', self.on_return_pressed)

        # Sorting Controls
        sort_frame = tk.Frame(self.sidebar, bg=SIDEBAR_COLOR)
        sort_frame.pack(fill="x", pady=(0, 5))
        tk.Label(sort_frame, text="Sort by:", font=("Segoe UI", 8), bg=SIDEBAR_COLOR).pack(side="left")
        
        self.sort_var = tk.StringVar(value="Name")
        sort_menu = ttk.Combobox(sort_frame, textvariable=self.sort_var, values=["Name", "Population (High)", "Population (Low)"], font=("Segoe UI", 8), state="readonly", width=15)
        sort_menu.pack(side="left", padx=5)
        sort_menu.bind("<<ComboboxSelected>>", lambda e: self.apply_sort_and_filter())

        # Listbox for countries
        list_container = tk.Frame(self.sidebar, bg=SIDEBAR_COLOR)
        list_container.pack(fill="both", expand=True)
        
        self.country_listbox = tk.Listbox(list_container, font=FONT_MAIN, relief="flat", borderwidth=0, selectbackground=PRIMARY_COLOR, highlightthickness=0)
        self.country_listbox.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.country_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.country_listbox.config(yscrollcommand=scrollbar.set)
        
        self.update_listbox_content()
        self.country_listbox.bind('<<ListboxSelect>>', self.on_list_select)

        # --- Main Content ---
        self.main_content = ttk.Frame(self.root, padding=30)
        self.main_content.pack(side="right", fill="both", expand=True)
        
        header_frame = tk.Frame(self.main_content, bg=BG_COLOR)
        header_frame.pack(fill="x", pady=(0, 20))
        tk.Label(header_frame, text="Global Country Explorer", font=FONT_HEADER, bg=BG_COLOR, fg=HEADER_COLOR).pack(side="left")
        
        # Floating Suggestion Listbox
        self.suggestion_listbox = tk.Listbox(self.root, font=FONT_MAIN, height=8, relief="flat", highlightthickness=1, highlightbackground=PRIMARY_COLOR, selectbackground=PRIMARY_COLOR)
        self.suggestion_listbox.bind('<<ListboxSelect>>', self.select_suggestion)
        self.suggestion_listbox.bind('<Return>', self.select_suggestion)

        # --- Country Card ---
        self.card = tk.Frame(self.main_content, bg=CARD_COLOR, padx=30, pady=30, relief="flat", highlightthickness=1, highlightbackground="#e0e0e0")
        self.card.pack(fill="x", pady=20)
        
        self.name_label = tk.Label(self.card, text="Select a country to view details", font=FONT_SUBHEADER, bg=CARD_COLOR, fg=TEXT_COLOR)
        self.name_label.pack(anchor="w", pady=(0, 20))
        
        self.info_grid = tk.Frame(self.card, bg=CARD_COLOR)
        self.info_grid.pack(fill="x")
        
        self.details = {}
        for i, label in enumerate(["Capital", "Continent", "Population"]):
            tk.Label(self.info_grid, text=f"{label}:", font=FONT_BOLD, bg=CARD_COLOR, fg="#666666").grid(row=i, column=0, sticky="w", pady=8)
            
            # Continent label is interactive
            if label == "Continent":
                val_label = tk.Label(self.info_grid, text="-", font=FONT_LINK, bg=CARD_COLOR, fg=PRIMARY_COLOR, cursor="hand2")
                val_label.bind("<Button-1>", lambda e: self.filter_by_continent())
                # Add a tooltip hint
                val_label.bind("<Enter>", lambda e: self.details['Continent'].config(fg=HOVER_COLOR))
                val_label.bind("<Leave>", lambda e: self.details['Continent'].config(fg=PRIMARY_COLOR))
            else:
                val_label = tk.Label(self.info_grid, text="-", font=FONT_MAIN, bg=CARD_COLOR, fg=TEXT_COLOR)
                
            val_label.grid(row=i, column=1, sticky="w", padx=20, pady=8)
            self.details[label] = val_label

        # --- Actions ---
        action_frame = tk.Frame(self.main_content, bg=BG_COLOR)
        action_frame.pack(fill="x", pady=10)
        
        self.maps_btn = tk.Button(action_frame, text="View on Google Maps", command=self.open_maps, bg=ACCENT_COLOR, fg="white", font=FONT_BOLD, relief="flat", padx=20, pady=8, cursor="hand2", state="disabled")
        self.maps_btn.pack(side="left", padx=(0, 10))
        
        self.clear_btn = tk.Button(action_frame, text="Reset Filters", command=self.reset_all, bg="#e0e0e0", fg=TEXT_COLOR, font=FONT_BOLD, relief="flat", padx=20, pady=8, cursor="hand2")
        self.clear_btn.pack(side="left")

        self.root.bind('<Button-1>', self.check_click_outside)

    def update_listbox_content(self):
        self.country_listbox.delete(0, tk.END)
        for country in self.current_display_list:
            self.country_listbox.insert(tk.END, country)

    def apply_sort_and_filter(self):
        # 1. Filter
        if self.active_filter:
            self.current_display_list = [c for c in self.all_country_list if self.country_info[c]['Continent'] == self.active_filter]
            self.filter_status.config(text=f"Filtered: {self.active_filter}", fg=PRIMARY_COLOR)
        else:
            self.current_display_list = list(self.all_country_list)
            self.filter_status.config(text="All Countries", fg="#888888")

        # 2. Sort
        sort_type = self.sort_var.get()
        if sort_type == "Name":
            self.current_display_list.sort()
        elif sort_type == "Population (High)":
            self.current_display_list.sort(key=lambda c: self.country_info[c]['Population'], reverse=True)
        elif sort_type == "Population (Low)":
            self.current_display_list.sort(key=lambda c: self.country_info[c]['Population'])
        
        self.update_listbox_content()

    def filter_by_continent(self):
        continent = self.details['Continent'].cget("text")
        if continent and continent != "-":
            self.active_filter = continent
            self.apply_sort_and_filter()

    def reset_all(self):
        self.active_filter = None
        self.sort_var.set("Name")
        self.clear_display()
        self.apply_sort_and_filter()

    def open_maps(self):
        country = self.name_label.cget("text")
        if country and country != "Select a country to view details":
            url = f"https://www.google.com/maps/search/{country}"
            webbrowser.open(url)

    # --- Reusing enhanced search behavior from before ---
    def on_focus_in(self, event):
        if self.search_var.get() == self.placeholder:
            self.search_var.set("")
            self.search_entry.config(fg=TEXT_COLOR)

    def on_focus_out(self, event):
        if not self.search_var.get().strip():
            self.search_var.set(self.placeholder)
            self.search_entry.config(fg=PLACEHOLDER_COLOR)

    def handle_key_release(self, event):
        if event.keysym in ('Up', 'Down', 'Return', 'Escape'): return
        self.update_suggestions()

    def update_suggestions(self):
        query = self.search_var.get().strip().lower()
        if not query or query == self.placeholder.lower():
            self.suggestion_listbox.place_forget()
            return

        starts_with = [c for c in self.all_country_list if c.lower().startswith(query)]
        contains = [c for c in self.all_country_list if query in c.lower() and c not in starts_with]
        suggestions = starts_with + contains

        if suggestions:
            self.suggestion_listbox.delete(0, tk.END)
            for s in suggestions: self.suggestion_listbox.insert(tk.END, s)
            x = self.search_entry.winfo_rootx() - self.root.winfo_rootx()
            y = self.search_entry.winfo_rooty() - self.root.winfo_rooty() + self.search_entry.winfo_height()
            self.suggestion_listbox.place(x=x, y=y, width=self.search_entry.winfo_width())
            self.suggestion_listbox.lift()
        else:
            self.suggestion_listbox.place_forget()

    def move_suggestion_focus(self, event):
        if not self.suggestion_listbox.winfo_viewable(): return
        current_idx = self.suggestion_listbox.curselection()
        if event.keysym == 'Down':
            next_idx = (current_idx[0] + 1) if current_idx else 0
            if next_idx < self.suggestion_listbox.size():
                self.suggestion_listbox.selection_clear(0, tk.END)
                self.suggestion_listbox.selection_set(next_idx)
                self.suggestion_listbox.see(next_idx)
        elif event.keysym == 'Up':
            next_idx = (current_idx[0] - 1) if current_idx else 0
            if next_idx >= 0:
                self.suggestion_listbox.selection_clear(0, tk.END)
                self.suggestion_listbox.selection_set(next_idx)
                self.suggestion_listbox.see(next_idx)
        return "break"

    def on_return_pressed(self, event):
        selection = self.suggestion_listbox.curselection()
        if self.suggestion_listbox.winfo_viewable() and selection:
            self.select_suggestion(None)
        else:
            self.perform_search()

    def select_suggestion(self, event):
        selection = self.suggestion_listbox.curselection()
        if selection:
            index = selection[0]
            country = self.suggestion_listbox.get(index)
            self.search_var.set(country)
            self.search_entry.config(fg=TEXT_COLOR)
            self.suggestion_listbox.place_forget()
            self.perform_search()

    def perform_search(self):
        query = self.search_var.get().strip()
        if not query or query == self.placeholder: return
        self.suggestion_listbox.place_forget()
        query_title = query.title()
        if query_title in self.country_info:
            self.display_info(query_title)
            # Find in the potentially filtered list
            if query_title in self.current_display_list:
                idx = self.current_display_list.index(query_title)
                self.country_listbox.selection_clear(0, tk.END)
                self.country_listbox.selection_set(idx)
                self.country_listbox.see(idx)
        else:
            messagebox.showinfo("Not Found", f"No exact match for '{query}'.")

    def on_list_select(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            country = event.widget.get(index)
            self.display_info(country)
            self.search_var.set(country)
            self.search_entry.config(fg=TEXT_COLOR)

    def display_info(self, country):
        info = self.country_info[country]
        self.name_label.config(text=country, fg=PRIMARY_COLOR, font=FONT_HEADER)
        self.details['Capital'].config(text=info['Capital'])
        self.details['Continent'].config(text=info['Continent'])
        pop = info['Population']
        self.details['Population'].config(text=f"{pop:,}" if pop > 0 else "N/A")
        self.maps_btn.config(state="normal")

    def check_click_outside(self, event):
        if self.suggestion_listbox.winfo_viewable():
            if event.widget != self.search_entry and event.widget != self.suggestion_listbox:
                self.suggestion_listbox.place_forget()

    def clear_display(self):
        self.search_var.set(self.placeholder)
        self.search_entry.config(fg=PLACEHOLDER_COLOR)
        self.name_label.config(text="Select a country to view details", fg=TEXT_COLOR, font=FONT_SUBHEADER)
        for label in self.details: self.details[label].config(text="-")
        self.country_listbox.selection_clear(0, tk.END)
        self.suggestion_listbox.place_forget()
        self.maps_btn.config(state="disabled")

if __name__ == '__main__':
    root = tk.Tk()
    app = CountryApp(root)
    root.mainloop()
