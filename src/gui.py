import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import threading
from typing import Dict, List, Any
from api_client import RealmVTTClient
from import_manager import ImportManager
import os

class OggDudeImporterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OggDude to Realm VTT Importer")
        self.root.geometry("800x600")
        
        # Center the window on screen
        self.center_window()
        
        # Initialize components
        self.api_client = RealmVTTClient()
        self.import_manager = ImportManager(self.api_client)
        
        # Set up callbacks
        self.import_manager.set_progress_callback(self.update_progress)
        self.import_manager.set_status_callback(self.update_status)
        
        # Variables
        self.email_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.two_fa_var = tk.StringVar()
        self.invite_code_var = tk.StringVar()
        self.oggdude_path_var = tk.StringVar()
        self.adversaries_path_var = tk.StringVar()
        self.selected_sources = []
        self.campaign_id = None
        
        # Progress monitoring
        self.progress_monitor_id = None
        
        # Load sources configuration
        self.sources_config = self.load_sources_config()
        
        self.create_widgets()
        
        # Load saved credentials on startup
        self.load_credentials_on_startup()
    
    def center_window(self):
        """Center the window on the screen"""
        # Update the window to get accurate dimensions
        self.root.update_idletasks()
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Get window dimensions
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        
        # Calculate position
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Set window position
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def get_default_directory(self):
        """Get the default directory (project root directory)"""
        import os
        # Get the src directory
        src_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to get the project root
        project_root = os.path.dirname(src_dir)
        return project_root
    
    def get_default_oggdata_directory(self):
        """Get the default OggData directory"""
        import os
        project_root = self.get_default_directory()
        oggdata_dir = os.path.join(project_root, "OggData")
        return oggdata_dir
    
    def get_default_adversaries_directory(self):
        """Get the default Adversaries directory"""
        import os
        project_root = self.get_default_directory()
        adversaries_dir = os.path.join(project_root, "Adversaries")
        return adversaries_dir
    
    def load_sources_config(self) -> Dict[str, Any]:
        """Load sources configuration"""
        try:
            with open('config/sources.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"sources": []}
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Login tab
        login_frame = ttk.Frame(notebook)
        notebook.add(login_frame, text="Login")
        self.create_login_tab(login_frame)
        
        # Configuration tab
        config_frame = ttk.Frame(notebook)
        notebook.add(config_frame, text="Configuration")
        self.create_config_tab(config_frame)
        
        # Import tab
        import_frame = ttk.Frame(notebook)
        notebook.add(import_frame, text="Import")
        self.create_import_tab(import_frame)
        
        # Status tab
        status_frame = ttk.Frame(notebook)
        notebook.add(status_frame, text="Status")
        self.create_status_tab(status_frame)
        
        # Initialize connection status
        self.update_connection_status()
    
    def create_login_tab(self, parent):
        """Create login tab"""
        # Create a canvas with scrollbar
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Create the window in the canvas with proper width handling
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Function to update the canvas window width when canvas is resized
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind('<Configure>', on_canvas_configure)
        
        # Title
        title_label = ttk.Label(scrollable_frame, text="Realm VTT Login", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # Login frame
        login_frame = ttk.LabelFrame(scrollable_frame, text="Login Credentials", padding=20)
        login_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Email
        ttk.Label(login_frame, text="Email:").grid(row=0, column=0, sticky=tk.W, pady=5)
        email_entry = ttk.Entry(login_frame, textvariable=self.email_var, width=40)
        email_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Password
        ttk.Label(login_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        password_entry = ttk.Entry(login_frame, textvariable=self.password_var, show="*", width=40)
        password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # 2FA Code (optional)
        ttk.Label(login_frame, text="2FA Code (optional):").grid(row=2, column=0, sticky=tk.W, pady=5)
        two_fa_entry = ttk.Entry(login_frame, textvariable=self.two_fa_var, width=40)
        two_fa_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Login button and status
        login_button_frame = ttk.Frame(login_frame)
        login_button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        self.login_button = ttk.Button(login_button_frame, text="Login", command=self.login)
        self.login_button.pack(side=tk.LEFT, padx=5)
        
        # Save credentials checkbox
        self.save_credentials_var = tk.BooleanVar()
        save_checkbox = ttk.Checkbutton(login_button_frame, text="Save credentials", variable=self.save_credentials_var)
        save_checkbox.pack(side=tk.LEFT, padx=10)
        
        # Login status indicator
        self.login_status_frame = ttk.Frame(login_button_frame)
        self.login_status_frame.pack(side=tk.LEFT, padx=10)
        
        self.login_status_icon = ttk.Label(self.login_status_frame, text="", font=("Arial", 14))
        self.login_status_icon.pack(side=tk.LEFT)
        
        self.login_status_text = ttk.Label(self.login_status_frame, text="", font=("Arial", 10))
        self.login_status_text.pack(side=tk.LEFT, padx=5)
        
        # Warning about plain text storage
        warning_frame = ttk.Frame(login_frame)
        warning_frame.grid(row=4, column=0, columnspan=2, pady=5)
        
        warning_label = ttk.Label(warning_frame, text="⚠️ Warning: Credentials will be stored in plain text", 
                                 foreground="orange", font=("Arial", 9))
        warning_label.pack()
        
        # Save/Load buttons frame
        save_load_frame = ttk.Frame(login_frame)
        save_load_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        save_button = ttk.Button(save_load_frame, text="Save Credentials", command=self.save_credentials)
        save_button.pack(side=tk.LEFT, padx=5)
        
        load_button = ttk.Button(save_load_frame, text="Load Credentials", command=self.load_credentials)
        load_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = ttk.Button(save_load_frame, text="Clear Saved", command=self.clear_saved_credentials)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Campaign frame
        campaign_frame = ttk.LabelFrame(scrollable_frame, text="Campaign", padding=20)
        campaign_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Invite code
        ttk.Label(campaign_frame, text="Campaign Invite Code:").grid(row=0, column=0, sticky=tk.W, pady=5)
        invite_entry = ttk.Entry(campaign_frame, textvariable=self.invite_code_var, width=40)
        invite_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Lookup button and status
        lookup_button_frame = ttk.Frame(campaign_frame)
        lookup_button_frame.grid(row=1, column=0, columnspan=2, pady=20)
        
        self.lookup_button = ttk.Button(lookup_button_frame, text="Lookup Campaign", command=self.lookup_campaign)
        self.lookup_button.pack(side=tk.LEFT, padx=5)
        
        # Campaign status indicator
        self.campaign_status_frame = ttk.Frame(lookup_button_frame)
        self.campaign_status_frame.pack(side=tk.LEFT, padx=10)
        
        self.campaign_status_icon = ttk.Label(self.campaign_status_frame, text="", font=("Arial", 14))
        self.campaign_status_icon.pack(side=tk.LEFT)
        
        self.campaign_status_text = ttk.Label(self.campaign_status_frame, text="", font=("Arial", 10))
        self.campaign_status_text.pack(side=tk.LEFT, padx=5)
        
        # Overall status section
        status_frame = ttk.LabelFrame(scrollable_frame, text="Connection Status", padding=20)
        status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Connection status
        self.connection_status_label = ttk.Label(status_frame, text="Not connected", font=("Arial", 12))
        self.connection_status_label.pack(pady=5)
        
        # Campaign info
        self.campaign_info_label = ttk.Label(status_frame, text="No campaign selected", font=("Arial", 10))
        self.campaign_info_label.pack(pady=5)
        
        # Configure grid weights
        login_frame.columnconfigure(1, weight=1)
        campaign_frame.columnconfigure(1, weight=1)
        
        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def create_config_tab(self, parent):
        """Create configuration tab"""
        # Title
        title_label = ttk.Label(parent, text="Import Configuration", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # Sources frame
        sources_frame = ttk.LabelFrame(parent, text="Data Sources", padding=20)
        sources_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Set a maximum height for the sources frame (about 300 pixels)
        sources_frame.configure(height=300)
        sources_frame.pack_propagate(False)  # Prevent the frame from expanding to fit content
        
        # Select/Deselect All buttons frame
        select_buttons_frame = ttk.Frame(sources_frame)
        select_buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        select_all_button = ttk.Button(select_buttons_frame, text="Select All", command=self.select_all_sources)
        select_all_button.pack(side=tk.LEFT, padx=5)
        
        deselect_all_button = ttk.Button(select_buttons_frame, text="Deselect All", command=self.deselect_all_sources)
        deselect_all_button.pack(side=tk.LEFT, padx=5)
        
        # Create a frame for the scrollable area
        sources_scroll_frame = ttk.Frame(sources_frame)
        sources_scroll_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Create canvas and scrollbar for sources
        sources_canvas = tk.Canvas(sources_scroll_frame)
        sources_scrollbar = ttk.Scrollbar(sources_scroll_frame, orient="vertical", command=sources_canvas.yview)
        sources_scrollable_frame = ttk.Frame(sources_canvas)
        
        sources_scrollable_frame.bind(
            "<Configure>",
            lambda e: sources_canvas.configure(scrollregion=sources_canvas.bbox("all"))
        )
        
        # Create the window in the canvas with proper width handling
        sources_canvas_window = sources_canvas.create_window((0, 0), window=sources_scrollable_frame, anchor="nw")
        sources_canvas.configure(yscrollcommand=sources_scrollbar.set)
        
        # Function to update the canvas window width when canvas is resized
        def on_sources_canvas_configure(event):
            sources_canvas.itemconfig(sources_canvas_window, width=event.width)
        
        sources_canvas.bind('<Configure>', on_sources_canvas_configure)
        
        # Create checkboxes for sources
        self.source_vars = {}
        for i, source in enumerate(self.sources_config.get('sources', [])):
            var = tk.BooleanVar()
            self.source_vars[source['key']] = var
            cb = ttk.Checkbutton(sources_scrollable_frame, text=source['name'], variable=var)
            cb.grid(row=i//2, column=i%2, sticky=tk.W, padx=10, pady=5)
        
        # Pack canvas and scrollbar
        sources_canvas.pack(side="left", fill="both", expand=True)
        sources_scrollbar.pack(side="right", fill="y")
        
        # Configure canvas scrolling with mouse wheel
        def _on_mousewheel(event):
            sources_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        sources_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # File paths frame
        paths_frame = ttk.LabelFrame(parent, text="File Paths", padding=20)
        paths_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # OggDude directory
        ttk.Label(paths_frame, text="OggDude Directory:").grid(row=0, column=0, sticky=tk.W, pady=5)
        oggdude_entry = ttk.Entry(paths_frame, textvariable=self.oggdude_path_var, width=50)
        oggdude_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        oggdude_button = ttk.Button(paths_frame, text="Browse", command=self.browse_oggdude_directory)
        oggdude_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Adversaries directory
        ttk.Label(paths_frame, text="Adversaries Directory:").grid(row=1, column=0, sticky=tk.W, pady=5)
        adversaries_entry = ttk.Entry(paths_frame, textvariable=self.adversaries_path_var, width=50)
        adversaries_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        adversaries_button = ttk.Button(paths_frame, text="Browse", command=self.browse_adversaries_directory)
        adversaries_button.grid(row=1, column=2, padx=5, pady=5)
        
        # Configure grid weights
        paths_frame.columnconfigure(1, weight=1)
        
        # Set default directories
        self.oggdude_path_var.set(self.get_default_oggdata_directory())
        self.adversaries_path_var.set(self.get_default_adversaries_directory())
        
        # Set the directories in the import manager
        self.import_manager.set_oggdude_directory(self.get_default_oggdata_directory())
        self.import_manager.set_adversaries_directory(self.get_default_adversaries_directory())
    
    def create_import_tab(self, parent):
        """Create import tab"""
        # Create a canvas with scrollbar
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Create the window in the canvas
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Function to update the canvas window width when canvas is resized
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind('<Configure>', on_canvas_configure)
        
        # Title
        title_label = ttk.Label(scrollable_frame, text="Import Data", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # Buttons frame
        buttons_frame = ttk.Frame(scrollable_frame)
        buttons_frame.pack(pady=10)
        
        # Check setup button
        check_setup_button = ttk.Button(buttons_frame, text="Check Setup", command=self.show_setup_status)
        check_setup_button.pack(side=tk.LEFT, padx=5)
        
        # Parse button
        parse_button = ttk.Button(buttons_frame, text="Parse Files", command=self.parse_files)
        parse_button.pack(side=tk.LEFT, padx=5)
        
        # Record type selection frame
        selection_frame = ttk.LabelFrame(scrollable_frame, text="Select Record Types to Import", padding=20)
        selection_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Create checkboxes for record types
        self.record_type_vars = {}
        record_types = [
            'items', 'species', 'careers', 'specializations', 
            'talents', 'force_powers', 'skills', 'npcs'
        ]
        
        for i, record_type in enumerate(record_types):
            # Special display name for NPCs to show it includes vehicles
            if record_type == 'npcs':
                display_name = 'NPCs / Vehicles'
            elif record_type == 'force_powers':
                display_name = 'Force Powers'
            else:
                display_name = record_type.title()
            
            var = tk.BooleanVar(value=True)  # Default to checked
            self.record_type_vars[record_type] = var
            
            checkbox = ttk.Checkbutton(selection_frame, text=display_name, variable=var, 
                                      command=self.update_warnings)
            checkbox.grid(row=i//2, column=i%2, sticky=tk.W, padx=10, pady=5)
        
        # Warning messages frame
        self.warnings_frame = ttk.LabelFrame(scrollable_frame, text="Import Warnings", padding=10)
        self.warnings_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # Warning labels (initially hidden)
        self.npc_warning_label = ttk.Label(self.warnings_frame, text="⚠️ Vehicles and NPCs will be missing equipment unless Items are also parsed.", foreground="orange")
        self.spec_warning_label = ttk.Label(self.warnings_frame, text="⚠️ Specializations without Talents also parsed will be missing the Talent records.", foreground="orange")
        
        # Max import frame
        max_import_frame = ttk.LabelFrame(scrollable_frame, text="Testing Options", padding=10)
        max_import_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(max_import_frame, text="Max records per type (for testing, 0 = no limit):").pack(side=tk.LEFT, padx=5)
        self.max_import_var = tk.StringVar(value="0")
        max_import_entry = ttk.Entry(max_import_frame, textvariable=self.max_import_var, width=10)
        max_import_entry.pack(side=tk.LEFT, padx=5)
        
        # Update existing records frame
        update_frame = ttk.LabelFrame(scrollable_frame, text="Import Options", padding=10)
        update_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.update_existing_var = tk.BooleanVar(value=True)  # Default to checked
        update_checkbox = ttk.Checkbutton(update_frame, text="Update Existing Records", variable=self.update_existing_var)
        update_checkbox.pack(anchor=tk.W, padx=5)
        
        # Record counts frame
        counts_frame = ttk.LabelFrame(scrollable_frame, text="Record Counts", padding=20)
        counts_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Create labels for record counts
        self.count_labels = {}
        
        for i, record_type in enumerate(record_types):
            # Special display name for NPCs to show it includes vehicles
            if record_type == 'npcs':
                display_name = 'NPCs / Vehicles'
            elif record_type == 'force_powers':
                display_name = 'Force Powers'
            else:
                display_name = record_type.title()
            
            label = ttk.Label(counts_frame, text=f"{display_name}: 0")
            label.grid(row=i//2, column=i%2, sticky=tk.W, padx=10, pady=5)
            self.count_labels[record_type] = label
        
        # Import button
        self.import_button = ttk.Button(scrollable_frame, text="Start Import", command=self.start_import, state=tk.DISABLED)
        self.import_button.pack(pady=10)
        
        # Stop button
        self.stop_button = ttk.Button(scrollable_frame, text="Stop Import", command=self.stop_import, state=tk.DISABLED)
        self.stop_button.pack(pady=5)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(scrollable_frame, text="Import Progress", padding=20)
        progress_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Progress label
        self.progress_label = ttk.Label(progress_frame, text="Ready to import")
        self.progress_label.pack(pady=5)
        
        # Current operation label
        self.operation_label = ttk.Label(progress_frame, text="", font=("Arial", 10))
        self.operation_label.pack(pady=5)
        
        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def create_status_tab(self, parent):
        """Create status tab"""
        # Title
        title_label = ttk.Label(parent, text="Import Status", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # Status text area
        self.status_text = scrolledtext.ScrolledText(parent, height=20, width=80)
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Clear button
        clear_button = ttk.Button(parent, text="Clear Log", command=self.clear_status)
        clear_button.pack(pady=10)
    
    def update_login_status(self, message: str, status_type: str = "info"):
        """Update login status with visual indicators"""
        if status_type == "success":
            self.login_status_icon.config(text="✓", foreground="green")
            self.login_status_text.config(text=message, foreground="green")
        elif status_type == "error":
            self.login_status_icon.config(text="✗", foreground="red")
            self.login_status_text.config(text=message, foreground="red")
        elif status_type == "loading":
            self.login_status_icon.config(text="⟳", foreground="blue")
            self.login_status_text.config(text=message, foreground="blue")
        else:
            self.login_status_icon.config(text="ℹ", foreground="black")
            self.login_status_text.config(text=message, foreground="black")
    
    def update_campaign_status(self, message: str, status_type: str = "info"):
        """Update campaign status with visual indicators"""
        if status_type == "success":
            self.campaign_status_icon.config(text="✓", foreground="green")
            self.campaign_status_text.config(text=message, foreground="green")
        elif status_type == "error":
            self.campaign_status_icon.config(text="✗", foreground="red")
            self.campaign_status_text.config(text=message, foreground="red")
        elif status_type == "loading":
            self.campaign_status_icon.config(text="⟳", foreground="blue")
            self.campaign_status_text.config(text=message, foreground="blue")
        else:
            self.campaign_status_icon.config(text="ℹ", foreground="black")
            self.campaign_status_text.config(text=message, foreground="black")
    
    def update_connection_status(self):
        """Update the overall connection status display"""
        if self.api_client.is_authenticated():
            self.connection_status_label.config(text="✓ Connected to Realm VTT", foreground="green")
            if self.campaign_id:
                self.campaign_info_label.config(text=f"Campaign ID: {self.campaign_id}", foreground="green")
            else:
                self.campaign_info_label.config(text="No campaign selected", foreground="orange")
        else:
            self.connection_status_label.config(text="✗ Not connected", foreground="red")
            self.campaign_info_label.config(text="No campaign selected", foreground="red")
    
    def login(self):
        """Handle login"""
        email = self.email_var.get().strip()
        password = self.password_var.get().strip()
        two_fa = self.two_fa_var.get().strip()
        
        if not email or not password:
            self.update_login_status("Please enter email and password", "error")
            return
        
        # Show loading state
        self.update_login_status("Logging in...", "loading")
        self.login_button.config(state=tk.DISABLED)
        self.root.update_idletasks()
        
        try:
            # Login to Realm VTT
            result = self.api_client.login(email, password, two_fa if two_fa else None)
            self.update_login_status("Login successful!", "success")
            self.update_connection_status()
            self.update_status("Login successful")
            
            # Auto-save credentials if checkbox is checked
            if self.save_credentials_var.get():
                self.save_credentials()
            
        except Exception as e:
            self.update_login_status(f"Login failed: {e}", "error")
            self.update_connection_status()
            self.update_status(f"Login failed: {e}")
            
        finally:
            self.login_button.config(state=tk.NORMAL)
    
    def lookup_campaign(self):
        """Handle campaign lookup"""
        invite_code = self.invite_code_var.get().strip()
        
        if not invite_code:
            self.update_campaign_status("Please enter an invite code", "error")
            return
        
        if not self.api_client.is_authenticated():
            self.update_campaign_status("Please login first", "error")
            return
        
        # Show loading state
        self.update_campaign_status("Looking up campaign...", "loading")
        self.lookup_button.config(state=tk.DISABLED)
        self.root.update_idletasks()
        
        try:
            # Lookup campaign
            campaign_id = self.api_client.get_campaign_id(invite_code)
            if campaign_id:
                self.campaign_id = campaign_id
                self.import_manager.set_campaign_id(campaign_id)
                self.update_campaign_status("Campaign found!", "success")
                self.update_connection_status()
                self.update_status(f"Campaign found: {campaign_id}")
                
                # Auto-save credentials if checkbox is checked
                if self.save_credentials_var.get():
                    self.save_credentials()
                
            else:
                self.update_campaign_status("Campaign not found", "error")
                self.update_connection_status()
                self.update_status("Campaign not found")
                
        except Exception as e:
            self.update_campaign_status(f"Lookup failed: {e}", "error")
            self.update_connection_status()
            self.update_status(f"Campaign lookup failed: {e}")
            
        finally:
            self.lookup_button.config(state=tk.NORMAL)
    
    def browse_oggdude_directory(self):
        """Browse for OggDude directory"""
        default_dir = self.get_default_oggdata_directory()
        directory = filedialog.askdirectory(
            title="Select OggDude Directory",
            initialdir=default_dir
        )
        if directory:
            self.oggdude_path_var.set(directory)
            self.import_manager.set_oggdude_directory(directory)
    
    def browse_adversaries_directory(self):
        """Browse for Adversaries directory"""
        default_dir = self.get_default_adversaries_directory()
        directory = filedialog.askdirectory(
            title="Select Adversaries Directory",
            initialdir=default_dir
        )
        if directory:
            self.adversaries_path_var.set(directory)
            self.import_manager.set_adversaries_directory(directory)
    
    def parse_files(self):
        """Parse files and show counts"""
        # Get selected sources
        selected_sources = [key for key, var in self.source_vars.items() if var.get()]
        
        # Check 1: Selected sources
        if not selected_sources:
            messagebox.showerror("No Sources Selected", 
                               "Please select at least one data source.\n\n"
                               "Check the sources you want to import in the Configuration tab.")
            return
        
        # Check 2: Directory paths
        if not self.oggdude_path_var.get() and not self.adversaries_path_var.get():
            messagebox.showerror("No Directories Selected", 
                               "Please select at least one directory.\n\n"
                               "Browse for your OggDude or Adversaries directories in the Configuration tab.")
            return
        
        # Check 3: Selected record types
        selected_record_types = self.get_selected_record_types()
        if not selected_record_types:
            messagebox.showerror("No Record Types Selected", 
                               "Please select at least one record type to import.\n\n"
                               "Check the record types you want to import above.")
            return
        
        # Set selected sources in import manager
        self.import_manager.set_selected_sources(selected_sources)
        
        # Set selected record types in import manager
        self.import_manager.set_selected_record_types(selected_record_types)
        
        # Set max import limit in import manager
        max_import_limit = self.get_max_import_limit()
        self.import_manager.set_max_import_limit(max_import_limit)
        
        try:
            # Parse files
            counts = self.import_manager.parse_files()
            
            # Debug: Print the counts we received
            print(f"DEBUG: Received counts from import manager: {counts}")
            
            # Filter counts based on selected record types
            filtered_counts = {record_type: count for record_type, count in counts.items() 
                             if record_type in selected_record_types}
            
            # Update count labels
            for record_type, count in counts.items():
                if record_type in self.count_labels:
                    # Use the same display name logic as when creating labels
                    if record_type == 'npcs':
                        display_name = 'NPCs / Vehicles'
                    elif record_type == 'force_powers':
                        display_name = 'Force Powers'
                    else:
                        display_name = record_type.title()
                    
                    # Show count in parentheses if not selected
                    if record_type in selected_record_types:
                        self.count_labels[record_type].config(text=f"{display_name}: {count}")
                    else:
                        self.count_labels[record_type].config(text=f"{display_name}: {count} (not selected)")
                    
                    print(f"DEBUG: Updated {record_type} label to {count}")
                else:
                    print(f"DEBUG: Record type '{record_type}' not found in count_labels: {list(self.count_labels.keys())}")
            
            # Update warnings
            self.update_warnings()
            
            # Enable import button if we have records in selected types
            total_records = sum(filtered_counts.values())
            if total_records > 0:
                self.import_button.config(state=tk.NORMAL)
                messagebox.showinfo("Success", f"Found {total_records} records to import from selected types")
            else:
                self.import_button.config(state=tk.DISABLED)
                messagebox.showwarning("Warning", "No records found in selected record types")
                
        except Exception as e:
            self.import_button.config(state=tk.DISABLED)
            messagebox.showerror("Error", f"Failed to parse files: {e}")
            self.update_status(f"Parse error: {e}")
    
    def update_warnings(self):
        """Update warning messages based on selected record types"""
        # Hide all warnings initially
        self.npc_warning_label.pack_forget()
        self.spec_warning_label.pack_forget()
        
        # Check if NPCs are selected but Items are not
        if self.record_type_vars['npcs'].get() and not self.record_type_vars['items'].get():
            self.npc_warning_label.pack(fill=tk.X, padx=5, pady=2)
        
        # Check if Specializations are selected but Talents are not
        if self.record_type_vars['specializations'].get() and not self.record_type_vars['talents'].get():
            self.spec_warning_label.pack(fill=tk.X, padx=5, pady=2)
    
    def get_selected_record_types(self) -> List[str]:
        """Get list of selected record types"""
        return [record_type for record_type, var in self.record_type_vars.items() if var.get()]
    
    def get_max_import_limit(self) -> int:
        """Get the maximum import limit from the GUI"""
        try:
            return int(self.max_import_var.get())
        except ValueError:
            return 0
    
    def get_update_existing_setting(self) -> bool:
        """Get the update existing records setting from the GUI"""
        return self.update_existing_var.get()
    
    def validate_setup(self) -> tuple[bool, list[str]]:
        """
        Validate the complete setup and return status
        
        Returns:
            tuple: (is_valid, list_of_issues)
        """
        issues = []
        
        # Check authentication
        if not self.api_client.is_authenticated():
            issues.append("Not logged in to Realm VTT")
        
        # Check campaign
        if not self.campaign_id:
            issues.append("No campaign selected")
        
        # Check sources
        selected_sources = [key for key, var in self.source_vars.items() if var.get()]
        if not selected_sources:
            issues.append("No data sources selected")
        
        # Check directories - check if they exist, not just if they're set
        oggdude_path = self.oggdude_path_var.get()
        adversaries_path = self.adversaries_path_var.get()
        
        # Check if directories are set and exist
        valid_directories = []
        if oggdude_path and os.path.exists(oggdude_path):
            valid_directories.append(oggdude_path)
        if adversaries_path and os.path.exists(adversaries_path):
            valid_directories.append(adversaries_path)
        
        if not valid_directories:
            issues.append("No directories selected")
        
        # Check if files were parsed (import button should be enabled)
        if hasattr(self, 'import_button') and self.import_button.cget('state') == tk.DISABLED:
            issues.append("Files not parsed (click 'Parse Files' first)")
        
        return len(issues) == 0, issues
    
    def show_setup_status(self):
        """Show a dialog with the current setup status"""
        is_valid, issues = self.validate_setup()
        
        if is_valid:
            selected_sources = [key for key, var in self.source_vars.items() if var.get()]
            source_names = [self.sources_config['sources'][i]['name'] for i, source in enumerate(self.sources_config['sources']) if source['key'] in selected_sources]
            
            messagebox.showinfo("Setup Status", 
                              f"✅ Setup is complete and ready for import!\n\n"
                              f"Campaign ID: {self.campaign_id}\n"
                              f"Sources: {', '.join(source_names)}\n"
                              f"Directories: {self.oggdude_path_var.get() or 'None'} / {self.adversaries_path_var.get() or 'None'}")
        else:
            message = "❌ Setup is incomplete. Please address the following issues:\n\n"
            for i, issue in enumerate(issues, 1):
                message += f"{i}. {issue}\n"
            message += "\nPlease complete the setup before starting import."
            
            messagebox.showwarning("Setup Incomplete", message)
    
    def start_import(self):
        """Start the import process"""
        # Comprehensive validation before starting import
        
        # Check 1: Login credentials and authentication
        if not self.api_client.is_authenticated():
            messagebox.showerror("Authentication Required", 
                               "Please login to Realm VTT first.\n\n"
                               "Go to the Login tab and enter your credentials.")
            return
        
        # Check 2: Campaign ID
        if not self.campaign_id:
            messagebox.showerror("Campaign Required", 
                               "Please lookup a campaign first.\n\n"
                               "Go to the Login tab and enter your campaign invite code.")
            return
        
        # Check 3: Selected sources
        selected_sources = [key for key, var in self.source_vars.items() if var.get()]
        if not selected_sources:
            messagebox.showerror("No Sources Selected", 
                               "Please select at least one data source.\n\n"
                               "Go to the Configuration tab and check the sources you want to import.")
            return
        
        # Check 4: Directory paths
        if not self.oggdude_path_var.get() and not self.adversaries_path_var.get():
            messagebox.showerror("No Directories Selected", 
                               "Please select at least one directory.\n\n"
                               "Go to the Configuration tab and browse for your OggDude or Adversaries directories.")
            return
        
        # Check 5: Import button should be enabled (meaning files were parsed successfully)
        if self.import_button.cget('state') == tk.DISABLED:
            messagebox.showerror("No Records Found", 
                               "No records were found to import.\n\n"
                               "Please click 'Parse Files' first to scan for available records.")
            return
        
        # All validations passed - confirm import
        result = messagebox.askyesno("Confirm Import", 
                                   f"Are you sure you want to start the import?\n\n"
                                   f"This will create records in your Realm VTT campaign:\n"
                                   f"• Campaign ID: {self.campaign_id}\n"
                                   f"• Sources: {', '.join([self.sources_config['sources'][i]['name'] for i, source in enumerate(self.sources_config['sources']) if source['key'] in selected_sources])}\n\n"
                                   f"This action cannot be undone.")
        if not result:
            return
        
        # Set selected record types and max import limit
        selected_record_types = self.get_selected_record_types()
        max_import_limit = self.get_max_import_limit()
        update_existing = self.get_update_existing_setting()
        
        self.import_manager.set_selected_record_types(selected_record_types)
        self.import_manager.set_max_import_limit(max_import_limit)
        self.import_manager.set_update_existing(update_existing)
        
        # Start import
        self.import_manager.start_import()
        self.import_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Start progress monitoring
        self.start_progress_monitoring()
    
    def stop_import(self):
        """Stop the import process"""
        self.import_manager.stop_import()
        self.import_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        # Stop progress monitoring
        self.stop_progress_monitoring()
    
    def start_progress_monitoring(self):
        """Start monitoring progress updates"""
        self.monitor_progress()
    
    def stop_progress_monitoring(self):
        """Stop monitoring progress updates"""
        if self.progress_monitor_id:
            self.root.after_cancel(self.progress_monitor_id)
            self.progress_monitor_id = None
    
    def monitor_progress(self):
        """Monitor progress and update UI"""
        if self.import_manager.is_import_running():
            # Get current progress
            current, total = self.import_manager.get_import_progress()
            operation = self.import_manager.get_current_operation()
            percentage = self.import_manager.get_progress_percentage()
            
            # Update progress bar
            self.progress_var.set(percentage)
            
            # Update labels
            if total > 0:
                self.progress_label.config(text=f"Progress: {current}/{total} ({percentage:.1f}%)")
            else:
                self.progress_label.config(text="Preparing import...")
            
            if operation:
                self.operation_label.config(text=f"Current: {operation}")
            
            # Schedule next update
            self.progress_monitor_id = self.root.after(100, self.monitor_progress)
        else:
            # Import finished
            self.stop_progress_monitoring()
            self.progress_label.config(text="Import completed")
            self.operation_label.config(text="")
    
    def update_progress(self, message: str, current: int, total: int):
        """Update progress bar and label (callback from import manager)"""
        if total > 0:
            progress = (current / total) * 100
            self.progress_var.set(progress)
        
        self.progress_label.config(text=f"{message} ({current}/{total})")
        self.operation_label.config(text=f"Current: {message}")
        self.update_status(message)
    
    def select_all_sources(self):
        """Select all source checkboxes"""
        for var in self.source_vars.values():
            var.set(True)
    
    def deselect_all_sources(self):
        """Deselect all source checkboxes"""
        for var in self.source_vars.values():
            var.set(False)
    
    def update_status(self, message: str):
        """Update status log"""
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_status(self):
        """Clear status log"""
        self.status_text.delete(1.0, tk.END) 
    
    def save_credentials(self):
        """Save current credentials to a file"""
        email = self.email_var.get()
        password = self.password_var.get()
        two_fa = self.two_fa_var.get()
        invite_code = self.invite_code_var.get()
        save_credentials = self.save_credentials_var.get()
        
        if not email or not password:
            self.update_login_status("Please enter email and password first.", "error")
            return
        
        credentials = {
            "email": email,
            "password": password,
            "two_fa": two_fa,
            "invite_code": invite_code
        }
        
        if save_credentials:
            try:
                with open('credentials.json', 'w') as f:
                    json.dump(credentials, f, indent=4)
                self.update_login_status("Credentials saved.", "success")
            except Exception as e:
                self.update_login_status(f"Failed to save credentials: {e}", "error")
        else:
            self.update_login_status("Credentials will not be saved.", "info")
    
    def load_credentials(self, silent=False):
        """Load credentials from a file"""
        try:
            with open('credentials.json', 'r') as f:
                credentials = json.load(f)
                self.email_var.set(credentials.get("email", ""))
                self.password_var.set(credentials.get("password", ""))
                self.two_fa_var.set(credentials.get("two_fa", ""))
                self.invite_code_var.set(credentials.get("invite_code", ""))
                self.save_credentials_var.set(True) # Assume saved if file exists
                
                if not silent:
                    self.update_login_status("Credentials loaded.", "success")
        except FileNotFoundError:
            if not silent:
                self.update_login_status("No saved credentials found.", "info")
        except Exception as e:
            if not silent:
                self.update_login_status(f"Failed to load credentials: {e}", "error")
    
    def clear_saved_credentials(self):
        """Clear saved credentials from the file"""
        if messagebox.askyesno("Clear Saved Credentials", "Are you sure you want to clear saved credentials?"):
            try:
                with open('credentials.json', 'w') as f:
                    json.dump({}, f)
                self.email_var.set("")
                self.password_var.set("")
                self.two_fa_var.set("")
                self.invite_code_var.set("")
                self.save_credentials_var.set(False)
                self.update_login_status("Credentials cleared.", "success")
            except Exception as e:
                self.update_login_status(f"Failed to clear credentials: {e}", "error")
    
    def load_credentials_on_startup(self):
        """Load credentials from 'credentials.json' on application startup"""
        self.load_credentials(silent=True) 