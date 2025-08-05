import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import threading
from typing import Dict, List, Any
from .api_client import RealmVTTClient
from .import_manager import ImportManager

class OggDudeImporterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OggDude to Realm VTT Importer")
        self.root.geometry("800x600")
        
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
        # Title
        title_label = ttk.Label(parent, text="Realm VTT Login", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # Login frame
        login_frame = ttk.LabelFrame(parent, text="Login Credentials", padding=20)
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
        
        # Login status indicator
        self.login_status_frame = ttk.Frame(login_button_frame)
        self.login_status_frame.pack(side=tk.LEFT, padx=10)
        
        self.login_status_icon = ttk.Label(self.login_status_frame, text="", font=("Arial", 14))
        self.login_status_icon.pack(side=tk.LEFT)
        
        self.login_status_text = ttk.Label(self.login_status_frame, text="", font=("Arial", 10))
        self.login_status_text.pack(side=tk.LEFT, padx=5)
        
        # Campaign frame
        campaign_frame = ttk.LabelFrame(parent, text="Campaign", padding=20)
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
        status_frame = ttk.LabelFrame(parent, text="Connection Status", padding=20)
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
    
    def create_config_tab(self, parent):
        """Create configuration tab"""
        # Title
        title_label = ttk.Label(parent, text="Import Configuration", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # Sources frame
        sources_frame = ttk.LabelFrame(parent, text="Data Sources", padding=20)
        sources_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Create checkboxes for sources
        self.source_vars = {}
        for i, source in enumerate(self.sources_config.get('sources', [])):
            var = tk.BooleanVar()
            self.source_vars[source['key']] = var
            cb = ttk.Checkbutton(sources_frame, text=source['name'], variable=var)
            cb.grid(row=i//2, column=i%2, sticky=tk.W, padx=10, pady=5)
        
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
    
    def create_import_tab(self, parent):
        """Create import tab"""
        # Title
        title_label = ttk.Label(parent, text="Import Data", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # Buttons frame
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(pady=10)
        
        # Check setup button
        check_setup_button = ttk.Button(buttons_frame, text="Check Setup", command=self.show_setup_status)
        check_setup_button.pack(side=tk.LEFT, padx=5)
        
        # Parse button
        parse_button = ttk.Button(buttons_frame, text="Parse Files", command=self.parse_files)
        parse_button.pack(side=tk.LEFT, padx=5)
        
        # Record counts frame
        counts_frame = ttk.LabelFrame(parent, text="Record Counts", padding=20)
        counts_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Create labels for record counts
        self.count_labels = {}
        record_types = [
            'weapons', 'species', 'careers', 'specializations', 
            'talents', 'force_powers', 'vehicles', 'armor', 'gear', 'npcs'
        ]
        
        for i, record_type in enumerate(record_types):
            label = ttk.Label(counts_frame, text=f"{record_type.title()}: 0")
            label.grid(row=i//2, column=i%2, sticky=tk.W, padx=10, pady=5)
            self.count_labels[record_type] = label
        
        # Import button
        self.import_button = ttk.Button(parent, text="Start Import", command=self.start_import, state=tk.DISABLED)
        self.import_button.pack(pady=10)
        
        # Stop button
        self.stop_button = ttk.Button(parent, text="Stop Import", command=self.stop_import, state=tk.DISABLED)
        self.stop_button.pack(pady=5)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(parent, text="Import Progress", padding=20)
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
            
            # Show success message
            messagebox.showinfo("Login Success", "Successfully logged in to Realm VTT!")
            
        except Exception as e:
            self.update_login_status(f"Login failed: {e}", "error")
            self.update_connection_status()
            self.update_status(f"Login failed: {e}")
            
            # Show error message
            messagebox.showerror("Login Failed", f"Failed to login: {e}")
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
                
                # Show success message
                messagebox.showinfo("Campaign Found", f"Successfully found campaign!\nCampaign ID: {campaign_id}")
            else:
                self.update_campaign_status("Campaign not found", "error")
                self.update_connection_status()
                self.update_status("Campaign not found")
                
                # Show error message
                messagebox.showerror("Campaign Not Found", "The campaign invite code was not found or you don't have access to it.")
        except Exception as e:
            self.update_campaign_status(f"Lookup failed: {e}", "error")
            self.update_connection_status()
            self.update_status(f"Campaign lookup failed: {e}")
            
            # Show error message
            messagebox.showerror("Campaign Lookup Failed", f"Failed to lookup campaign: {e}")
        finally:
            self.lookup_button.config(state=tk.NORMAL)
    
    def browse_oggdude_directory(self):
        """Browse for OggDude directory"""
        directory = filedialog.askdirectory(title="Select OggDude Directory")
        if directory:
            self.oggdude_path_var.set(directory)
            self.import_manager.set_oggdude_directory(directory)
    
    def browse_adversaries_directory(self):
        """Browse for Adversaries directory"""
        directory = filedialog.askdirectory(title="Select Adversaries Directory")
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
        
        # Set selected sources in import manager
        self.import_manager.set_selected_sources(selected_sources)
        
        try:
            # Parse files
            counts = self.import_manager.parse_files()
            
            # Update count labels
            for record_type, count in counts.items():
                if record_type in self.count_labels:
                    self.count_labels[record_type].config(text=f"{record_type.title()}: {count}")
            
            # Enable import button if we have records
            total_records = sum(counts.values())
            if total_records > 0:
                self.import_button.config(state=tk.NORMAL)
                messagebox.showinfo("Success", f"Found {total_records} records to import")
            else:
                self.import_button.config(state=tk.DISABLED)
                messagebox.showwarning("Warning", "No records found matching selected sources")
                
        except Exception as e:
            self.import_button.config(state=tk.DISABLED)
            messagebox.showerror("Error", f"Failed to parse files: {e}")
            self.update_status(f"Parse error: {e}")
    
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
        
        # Check directories
        if not self.oggdude_path_var.get() and not self.adversaries_path_var.get():
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
    
    def update_status(self, message: str):
        """Update status log"""
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_status(self):
        """Clear status log"""
        self.status_text.delete(1.0, tk.END) 