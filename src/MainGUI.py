import customtkinter as ctk
from CTkMenuBar import *
import tkinter as tk
from tkinter import messagebox, simpledialog
import threading
import time
from typing import Optional
import logging
from rcon_service.RCONService import RCONService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class MinecraftRCONGUI:
    """
    A comprehensive GUI application for Minecraft RCON administration.
    
    Features:
    - Server connection management
    - Real-time player monitoring
    - Quick command execution
    - Server administration tools
    """
    
    def __init__(self):
        """Initialize the GUI application."""
        self.root = ctk.CTk()
        self.root.title("PyMCRCON-GUI - Minecraft RCON Client")
        self.root.geometry("1200x700")
        self.root.minsize(800, 500)
        
        # RCON service instance
        self.rcon_service: Optional[RCONService] = None
        self.connected = False
        
        # Connection details
        self.server_host = "127.0.0.1"
        self.server_port = 25575
        self.server_password = ""
        
        # Auto-refresh settings
        self.auto_refresh = True
        self.refresh_interval = 5  # seconds
        self.refresh_thread = None
        self.stop_refresh = threading.Event()
        
        # Setup GUI components
        self.setup_gui()
        self.start_auto_refresh()
        
    def setup_gui(self):
        """Setup all GUI components."""
        # Create menu bar
        self.setup_menu_bar()
        
        # Create main content area
        self.setup_main_content()
        
        # Create status bar
        self.setup_status_bar()
        
    def setup_menu_bar(self):
        """Setup the top menu bar using CTkMenuBar."""
        self.menu_bar = CTkMenuBar(self.root)
        
        # File menu
        self.file_menu = self.menu_bar.add_cascade("File")
        self.file_dropdown = CustomDropdownMenu(widget=self.file_menu)
        self.file_dropdown.add_option("Connect", command=self.show_connection_dialog)
        self.file_dropdown.add_option("Disconnect", command=self.disconnect_server)
        self.file_dropdown.add_separator()
        self.file_dropdown.add_option("Save Server Config", command=self.save_all)
        self.file_dropdown.add_option("Reload Server", command=self.reload_server)
        self.file_dropdown.add_separator()
        self.file_dropdown.add_option("Exit", command=self.root.quit)
        
        # Quick Commands menu
        self.commands_menu = self.menu_bar.add_cascade("Quick Commands")
        self.commands_dropdown = CustomDropdownMenu(widget=self.commands_menu)
        self.commands_dropdown.add_option("Set Time to Day", command=lambda: self.execute_quick_command("time set day"))
        self.commands_dropdown.add_option("Set Time to Night", command=lambda: self.execute_quick_command("time set night"))
        self.commands_dropdown.add_separator()
        self.commands_dropdown.add_option("Clear Weather", command=lambda: self.execute_quick_command("weather clear"))
        self.commands_dropdown.add_option("Set Rain", command=lambda: self.execute_quick_command("weather rain"))
        self.commands_dropdown.add_option("Set Thunder", command=lambda: self.execute_quick_command("weather thunder"))
        self.commands_dropdown.add_separator()
        self.commands_dropdown.add_option("Save World", command=self.save_all)
        self.commands_dropdown.add_option("Stop Server", command=self.stop_server_confirm)
        
    def setup_main_content(self):
        """Setup the main content area."""
        # Create main frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure grid weights
        self.main_frame.grid_columnconfigure(0, weight=3)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Left panel - Console and commands
        self.setup_left_panel()
        
        # Right panel - Server info and players
        self.setup_right_panel()
        
    def setup_left_panel(self):
        """Setup the left panel with console and command input."""
        self.left_panel = ctk.CTkFrame(self.main_frame)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Configure grid
        self.left_panel.grid_rowconfigure(0, weight=1)
        self.left_panel.grid_rowconfigure(1, weight=0)
        self.left_panel.grid_columnconfigure(0, weight=1)
        
        # Console output
        self.console_label = ctk.CTkLabel(self.left_panel, text="Console Output", font=ctk.CTkFont(size=16, weight="bold"))
        self.console_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        
        self.console_frame = ctk.CTkFrame(self.left_panel)
        self.console_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.console_frame.grid_rowconfigure(0, weight=1)
        self.console_frame.grid_columnconfigure(0, weight=1)
        
        self.console_text = ctk.CTkTextbox(self.console_frame, height=400, font=ctk.CTkFont(family="Consolas", size=12))
        self.console_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Command input area
        self.command_frame = ctk.CTkFrame(self.left_panel)
        self.command_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.command_frame.grid_columnconfigure(0, weight=1)
        
        self.command_label = ctk.CTkLabel(self.command_frame, text="Command Input:", font=ctk.CTkFont(size=14, weight="bold"))
        self.command_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        
        self.command_entry = ctk.CTkEntry(self.command_frame, placeholder_text="Enter command here...")
        self.command_entry.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))
        self.command_entry.bind("<Return>", self.execute_command)
        
        self.command_button = ctk.CTkButton(self.command_frame, text="Execute", command=self.execute_command)
        self.command_button.grid(row=1, column=1, padx=(5, 10), pady=(0, 5))
        
        # Quick action buttons
        self.quick_buttons_frame = ctk.CTkFrame(self.command_frame)
        self.quick_buttons_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 10))
        
        # Row 1 of quick buttons
        ctk.CTkButton(self.quick_buttons_frame, text="Day", width=60, command=lambda: self.execute_quick_command("time set day")).grid(row=0, column=0, padx=2, pady=2)
        ctk.CTkButton(self.quick_buttons_frame, text="Night", width=60, command=lambda: self.execute_quick_command("time set night")).grid(row=0, column=1, padx=2, pady=2)
        ctk.CTkButton(self.quick_buttons_frame, text="Clear", width=60, command=lambda: self.execute_quick_command("weather clear")).grid(row=0, column=2, padx=2, pady=2)
        ctk.CTkButton(self.quick_buttons_frame, text="Rain", width=60, command=lambda: self.execute_quick_command("weather rain")).grid(row=0, column=3, padx=2, pady=2)
        
        # Row 2 of quick buttons
        ctk.CTkButton(self.quick_buttons_frame, text="Save", width=60, command=self.save_all).grid(row=1, column=0, padx=2, pady=2)
        ctk.CTkButton(self.quick_buttons_frame, text="Reload", width=60, command=self.reload_server).grid(row=1, column=1, padx=2, pady=2)
        ctk.CTkButton(self.quick_buttons_frame, text="TPS", width=60, command=lambda: self.execute_quick_command("tps")).grid(row=1, column=2, padx=2, pady=2)
        ctk.CTkButton(self.quick_buttons_frame, text="Seed", width=60, command=self.get_seed).grid(row=1, column=3, padx=2, pady=2)
        
    def setup_right_panel(self):
        """Setup the right panel with server info and player list."""
        self.right_panel = ctk.CTkFrame(self.main_frame)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        # Configure grid
        self.right_panel.grid_rowconfigure(1, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)
        
        # Server connection info
        self.connection_frame = ctk.CTkFrame(self.right_panel)
        self.connection_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        self.connection_label = ctk.CTkLabel(self.connection_frame, text="Connected to:", font=ctk.CTkFont(size=14, weight="bold"))
        self.connection_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.connection_info = ctk.CTkLabel(self.connection_frame, text="Not Connected", font=ctk.CTkFont(size=12))
        self.connection_info.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Players section
        self.players_frame = ctk.CTkFrame(self.right_panel)
        self.players_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 5))
        self.players_frame.grid_rowconfigure(1, weight=1)
        self.players_frame.grid_columnconfigure(0, weight=1)
        
        self.players_label = ctk.CTkLabel(self.players_frame, text="Players Online: 0/0", font=ctk.CTkFont(size=14, weight="bold"))
        self.players_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        
        # Players list with scrollbar
        self.players_textbox = ctk.CTkTextbox(self.players_frame, height=200, font=ctk.CTkFont(size=12))
        self.players_textbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 5))
        
        # Player actions frame
        self.player_actions_frame = ctk.CTkFrame(self.players_frame)
        self.player_actions_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
        
        ctk.CTkButton(self.player_actions_frame, text="Kick Player", command=self.kick_player_dialog).pack(side="left", padx=2, pady=5)
        ctk.CTkButton(self.player_actions_frame, text="Ban Player", command=self.ban_player_dialog).pack(side="left", padx=2, pady=5)
        ctk.CTkButton(self.player_actions_frame, text="Message", command=self.message_player_dialog).pack(side="left", padx=2, pady=5)
        
        # Server actions
        self.server_actions_frame = ctk.CTkFrame(self.right_panel)
        self.server_actions_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
        
        ctk.CTkButton(self.server_actions_frame, text="Broadcast Message", command=self.broadcast_message_dialog).pack(pady=5, fill="x", padx=10)
        ctk.CTkButton(self.server_actions_frame, text="Server Settings", command=self.server_settings_dialog).pack(pady=2, fill="x", padx=10)
        
    def setup_status_bar(self):
        """Setup the status bar at the bottom."""
        self.status_frame = ctk.CTkFrame(self.root, height=30)
        self.status_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.status_label = ctk.CTkLabel(self.status_frame, text="Ready", font=ctk.CTkFont(size=11))
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # Auto refresh toggle
        self.auto_refresh_var = ctk.BooleanVar(value=True)
        self.auto_refresh_checkbox = ctk.CTkCheckBox(self.status_frame, text="Auto Refresh", 
                                                   variable=self.auto_refresh_var, command=self.toggle_auto_refresh)
        self.auto_refresh_checkbox.pack(side="right", padx=10, pady=5)
        
    def show_connection_dialog(self):
        """Show connection dialog."""
        dialog = ConnectionDialog(self.root, self.server_host, self.server_port, self.server_password)
        if dialog.result:
            self.server_host, self.server_port, self.server_password = dialog.result
            self.connect_to_server()
            
    def connect_to_server(self):
        """Connect to the Minecraft server."""
        if self.connected:
            self.disconnect_server()
            
        try:
            self.rcon_service = RCONService(self.server_host, self.server_port, self.server_password)
            self.rcon_service.connect()
            self.connected = True
            
            # Update UI
            connection_text = f"{self.server_host} on port {self.server_port}"
            self.connection_info.configure(text=connection_text)
            self.log_to_console(f"Connected to {connection_text}")
            self.update_status("Connected")
            
            # Initial data fetch
            self.refresh_player_list()
            
        except Exception as e:
            self.log_to_console(f"Failed to connect: {str(e)}")
            self.update_status("Connection failed")
            messagebox.showerror("Connection Error", f"Failed to connect to server:\n{str(e)}")
            
    def disconnect_server(self):
        """Disconnect from the server."""
        if self.rcon_service:
            try:
                self.rcon_service.disconnect()
            except:
                pass
            
        self.connected = False
        self.rcon_service = None
        self.connection_info.configure(text="Not Connected")
        self.players_label.configure(text="Players Online: 0/0")
        self.players_textbox.delete("0.0", "end")
        self.log_to_console("Disconnected from server")
        self.update_status("Disconnected")
        
    def execute_command(self, event=None):
        """Execute command from the input field."""
        command = self.command_entry.get().strip()
        if not command:
            return
            
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to a server first.")
            return
            
        try:
            response = self.rcon_service.send_command(command)
            self.log_to_console(f"> {command}")
            self.log_to_console(f"< {response}")
            self.command_entry.delete(0, "end")
            
            # Refresh player list if command might affect it
            if any(cmd in command.lower() for cmd in ['kick', 'ban', 'whitelist', 'op', 'deop']):
                self.refresh_player_list()
                
        except Exception as e:
            self.log_to_console(f"Command failed: {str(e)}")
            
    def execute_quick_command(self, command):
        """Execute a quick command."""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to a server first.")
            return
            
        try:
            response = self.rcon_service.send_command(command)
            self.log_to_console(f"> {command}")
            self.log_to_console(f"< {response}")
        except Exception as e:
            self.log_to_console(f"Command failed: {str(e)}")
            
    def save_all(self):
        """Save the world."""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to a server first.")
            return
            
        try:
            response = self.rcon_service.save_all()
            self.log_to_console(f"> save-all")
            self.log_to_console(f"< {response}")
        except Exception as e:
            self.log_to_console(f"Save failed: {str(e)}")
            
    def reload_server(self):
        """Reload the server."""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to a server first.")
            return
            
        try:
            response = self.rcon_service.reload_server()
            self.log_to_console(f"> reload")
            self.log_to_console(f"< {response}")
        except Exception as e:
            self.log_to_console(f"Reload failed: {str(e)}")
            
    def get_seed(self):
        """Get world seed."""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to a server first.")
            return
            
        try:
            response = self.rcon_service.get_seed()
            self.log_to_console(f"> seed")
            self.log_to_console(f"< {response}")
        except Exception as e:
            self.log_to_console(f"Seed command failed: {str(e)}")
            
    def stop_server_confirm(self):
        """Confirm and stop server."""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to a server first.")
            return
            
        if messagebox.askyesno("Confirm", "Are you sure you want to stop the server?"):
            try:
                response = self.rcon_service.stop_server()
                self.log_to_console(f"> stop")
                self.log_to_console(f"< {response}")
                # Server will disconnect us
                self.disconnect_server()
            except Exception as e:
                self.log_to_console(f"Stop command failed: {str(e)}")
                
    def refresh_player_list(self):
        """Refresh the player list."""
        if not self.connected:
            return
            
        try:
            players = self.rcon_service.get_player_list()
            current_count, max_count = self.rcon_service.get_player_count()
            
            # Update player count
            self.players_label.configure(text=f"Players Online: {current_count}/{max_count}")
            
            # Update player list
            self.players_textbox.delete("0.0", "end")
            if players:
                for player in players:
                    self.players_textbox.insert("end", f"{player}\n")
            else:
                self.players_textbox.insert("end", "No players online")
                
        except Exception as e:
            logger.error(f"Failed to refresh player list: {e}")
            
    def start_auto_refresh(self):
        """Start auto-refresh thread."""
        if self.refresh_thread and self.refresh_thread.is_alive():
            return
            
        self.stop_refresh.clear()
        self.refresh_thread = threading.Thread(target=self._auto_refresh_loop, daemon=True)
        self.refresh_thread.start()
        
    def toggle_auto_refresh(self):
        """Toggle auto refresh on/off."""
        self.auto_refresh = self.auto_refresh_var.get()
        
    def _auto_refresh_loop(self):
        """Auto refresh loop running in separate thread."""
        while not self.stop_refresh.is_set():
            if self.auto_refresh and self.connected:
                try:
                    self.root.after(0, self.refresh_player_list)
                except:
                    pass
            time.sleep(self.refresh_interval)
            
    def kick_player_dialog(self):
        """Show kick player dialog."""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to a server first.")
            return
            
        players = self.rcon_service.get_player_list()
        if not players:
            messagebox.showinfo("No Players", "No players are currently online.")
            return
            
        dialog = PlayerActionDialog(self.root, "Kick Player", players)
        if dialog.result:
            player, reason = dialog.result
            try:
                response = self.rcon_service.kick_player(player, reason)
                self.log_to_console(f"Kicked {player}: {reason}")
                self.log_to_console(f"< {response}")
                self.refresh_player_list()
            except Exception as e:
                self.log_to_console(f"Kick failed: {str(e)}")
                
    def ban_player_dialog(self):
        """Show ban player dialog."""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to a server first.")
            return
            
        players = self.rcon_service.get_player_list()
        if not players:
            messagebox.showinfo("No Players", "No players are currently online.")
            return
            
        dialog = PlayerActionDialog(self.root, "Ban Player", players)
        if dialog.result:
            player, reason = dialog.result
            try:
                response = self.rcon_service.ban_player(player, reason)
                self.log_to_console(f"Banned {player}: {reason}")
                self.log_to_console(f"< {response}")
                self.refresh_player_list()
            except Exception as e:
                self.log_to_console(f"Ban failed: {str(e)}")
                
    def message_player_dialog(self):
        """Show message player dialog."""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to a server first.")
            return
            
        players = self.rcon_service.get_player_list()
        if not players:
            messagebox.showinfo("No Players", "No players are currently online.")
            return
            
        dialog = PlayerMessageDialog(self.root, players)
        if dialog.result:
            player, message = dialog.result
            try:
                response = self.rcon_service.tell_player(player, message)
                self.log_to_console(f"Message to {player}: {message}")
                self.log_to_console(f"< {response}")
            except Exception as e:
                self.log_to_console(f"Message failed: {str(e)}")
                
    def broadcast_message_dialog(self):
        """Show broadcast message dialog."""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to a server first.")
            return
            
        message = simpledialog.askstring("Broadcast Message", "Enter message to broadcast:")
        if message:
            try:
                response = self.rcon_service.broadcast_message(message)
                self.log_to_console(f"Broadcast: {message}")
                self.log_to_console(f"< {response}")
            except Exception as e:
                self.log_to_console(f"Broadcast failed: {str(e)}")
                
    def server_settings_dialog(self):
        """Show server settings dialog."""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to a server first.")
            return
            
        dialog = ServerSettingsDialog(self.root, self.rcon_service)
        
    def log_to_console(self, message):
        """Log message to console."""
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.console_text.insert("end", formatted_message)
        self.console_text.see("end")
        
    def update_status(self, status):
        """Update status bar."""
        self.status_label.configure(text=status)
        
    def run(self):
        """Run the application."""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        """Handle application closing."""
        self.stop_refresh.set()
        if self.connected:
            self.disconnect_server()
        self.root.destroy()


class ConnectionDialog:
    """Dialog for server connection settings."""
    
    def __init__(self, parent, host="127.0.0.1", port=25575, password=""):
        self.result = None
        
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Connect to Server")
        self.dialog.geometry("400x350")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - 400) // 2
        y = (self.dialog.winfo_screenheight() - 350) // 2
        self.dialog.geometry(f"400x350+{x}+{y}")
        
        # Create form
        frame = ctk.CTkFrame(self.dialog)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(frame, text="Server Connection", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        # Host
        ctk.CTkLabel(frame, text="Host:").pack(anchor="w", padx=10)
        self.host_entry = ctk.CTkEntry(frame, width=300)
        self.host_entry.pack(pady=(5, 10), padx=10)
        self.host_entry.insert(0, host)
        
        # Port
        ctk.CTkLabel(frame, text="Port:").pack(anchor="w", padx=10)
        self.port_entry = ctk.CTkEntry(frame, width=300)
        self.port_entry.pack(pady=(5, 10), padx=10)
        self.port_entry.insert(0, str(port))
        
        # Password
        ctk.CTkLabel(frame, text="Password:").pack(anchor="w", padx=10)
        self.password_entry = ctk.CTkEntry(frame, width=300, show="*")
        self.password_entry.pack(pady=(5, 20), padx=10)
        self.password_entry.insert(0, password)
        
        # Buttons
        button_frame = ctk.CTkFrame(frame)
        button_frame.pack(pady=10)
        
        ctk.CTkButton(button_frame, text="Connect", command=self.connect).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Cancel", command=self.cancel).pack(side="left", padx=5)
        
        # Bind Enter key
        self.dialog.bind('<Return>', lambda e: self.connect())
        
    def connect(self):
        try:
            host = self.host_entry.get().strip()
            port = int(self.port_entry.get().strip())
            password = self.password_entry.get()
            
            if not host:
                messagebox.showerror("Error", "Host cannot be empty")
                return
                
            self.result = (host, port, password)
            self.dialog.destroy()
        except ValueError:
            messagebox.showerror("Error", "Port must be a valid number")
            
    def cancel(self):
        self.dialog.destroy()


class PlayerActionDialog:
    """Dialog for player actions (kick/ban)."""
    
    def __init__(self, parent, title, players):
        self.result = None
        
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("350x250")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - 350) // 2
        y = (self.dialog.winfo_screenheight() - 250) // 2
        self.dialog.geometry(f"350x250+{x}+{y}")
        
        frame = ctk.CTkFrame(self.dialog)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # Player selection
        ctk.CTkLabel(frame, text="Select Player:").pack(anchor="w", padx=10)
        self.player_var = ctk.StringVar(value=players[0] if players else "")
        self.player_menu = ctk.CTkOptionMenu(frame, variable=self.player_var, values=players)
        self.player_menu.pack(pady=(5, 10), padx=10, fill="x")
        
        # Reason
        ctk.CTkLabel(frame, text="Reason:").pack(anchor="w", padx=10)
        self.reason_entry = ctk.CTkEntry(frame, width=300, placeholder_text="Enter reason...")
        self.reason_entry.pack(pady=(5, 20), padx=10)
        self.reason_entry.insert(0, "Kicked by admin" if "Kick" in title else "Banned by admin")
        
        # Buttons
        button_frame = ctk.CTkFrame(frame)
        button_frame.pack(pady=10)
        
        ctk.CTkButton(button_frame, text="Execute", command=self.execute).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Cancel", command=self.cancel).pack(side="left", padx=5)
        
        # Bind Enter key
        self.dialog.bind('<Return>', lambda e: self.execute())
        
    def execute(self):
        player = self.player_var.get()
        reason = self.reason_entry.get().strip()
        
        if not player:
            messagebox.showerror("Error", "Please select a player")
            return
            
        if not reason:
            reason = "No reason provided"
            
        self.result = (player, reason)
        self.dialog.destroy()
        
    def cancel(self):
        self.dialog.destroy()


class PlayerMessageDialog:
    """Dialog for sending messages to players."""
    
    def __init__(self, parent, players):
        self.result = None
        
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Send Message to Player")
        self.dialog.geometry("350x250")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - 350) // 2
        y = (self.dialog.winfo_screenheight() - 250) // 2
        self.dialog.geometry(f"350x250+{x}+{y}")
        
        frame = ctk.CTkFrame(self.dialog)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(frame, text="Send Message", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # Player selection
        ctk.CTkLabel(frame, text="Select Player:").pack(anchor="w", padx=10)
        self.player_var = ctk.StringVar(value=players[0] if players else "")
        self.player_menu = ctk.CTkOptionMenu(frame, variable=self.player_var, values=players)
        self.player_menu.pack(pady=(5, 10), padx=10, fill="x")
        
        # Message
        ctk.CTkLabel(frame, text="Message:").pack(anchor="w", padx=10)
        self.message_entry = ctk.CTkEntry(frame, width=300, placeholder_text="Enter message...")
        self.message_entry.pack(pady=(5, 20), padx=10)
        
        # Buttons
        button_frame = ctk.CTkFrame(frame)
        button_frame.pack(pady=10)
        
        ctk.CTkButton(button_frame, text="Send", command=self.send).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Cancel", command=self.cancel).pack(side="left", padx=5)
        
        # Bind Enter key
        self.dialog.bind('<Return>', lambda e: self.send())
        
    def send(self):
        player = self.player_var.get()
        message = self.message_entry.get().strip()
        
        if not player:
            messagebox.showerror("Error", "Please select a player")
            return
            
        if not message:
            messagebox.showerror("Error", "Please enter a message")
            return
            
        self.result = (player, message)
        self.dialog.destroy()
        
    def cancel(self):
        self.dialog.destroy()


class ServerSettingsDialog:
    """Dialog for server settings and game rules."""
    
    def __init__(self, parent, rcon_service):
        self.rcon_service = rcon_service
        
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Server Settings")
        self.dialog.geometry("500x600")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - 500) // 2
        y = (self.dialog.winfo_screenheight() - 600) // 2
        self.dialog.geometry(f"500x600+{x}+{y}")
        
        # Create main frame with scrollbar
        main_frame = ctk.CTkScrollableFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(main_frame, text="Server Settings", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        # World Settings
        world_frame = ctk.CTkFrame(main_frame)
        world_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(world_frame, text="World Settings", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        
        # Time settings
        time_frame = ctk.CTkFrame(world_frame)
        time_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(time_frame, text="Time:").pack(side="left", padx=5)
        ctk.CTkButton(time_frame, text="Day", width=60, command=lambda: self.set_time("day")).pack(side="left", padx=2)
        ctk.CTkButton(time_frame, text="Night", width=60, command=lambda: self.set_time("night")).pack(side="left", padx=2)
        ctk.CTkButton(time_frame, text="Noon", width=60, command=lambda: self.set_time("noon")).pack(side="left", padx=2)
        ctk.CTkButton(time_frame, text="Midnight", width=80, command=lambda: self.set_time("midnight")).pack(side="left", padx=2)
        
        # Weather settings
        weather_frame = ctk.CTkFrame(world_frame)
        weather_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(weather_frame, text="Weather:").pack(side="left", padx=5)
        ctk.CTkButton(weather_frame, text="Clear", width=60, command=lambda: self.set_weather("clear")).pack(side="left", padx=2)
        ctk.CTkButton(weather_frame, text="Rain", width=60, command=lambda: self.set_weather("rain")).pack(side="left", padx=2)
        ctk.CTkButton(weather_frame, text="Thunder", width=70, command=lambda: self.set_weather("thunder")).pack(side="left", padx=2)
        
        # Difficulty settings
        difficulty_frame = ctk.CTkFrame(world_frame)
        difficulty_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(difficulty_frame, text="Difficulty:").pack(side="left", padx=5)
        self.difficulty_var = ctk.StringVar(value="normal")
        difficulty_menu = ctk.CTkOptionMenu(difficulty_frame, variable=self.difficulty_var, 
                                          values=["peaceful", "easy", "normal", "hard"],
                                          command=self.set_difficulty)
        difficulty_menu.pack(side="left", padx=5)
        
        # Game Rules
        gamerules_frame = ctk.CTkFrame(main_frame)
        gamerules_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(gamerules_frame, text="Game Rules", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        
        # Common game rules with checkboxes
        self.gamerule_vars = {}
        common_rules = [
            ("keepInventory", "Keep inventory on death"),
            ("doMobSpawning", "Enable mob spawning"),
            ("doDaylightCycle", "Enable daylight cycle"),
            ("doWeatherCycle", "Enable weather cycle"),
            ("mobGriefing", "Allow mob griefing"),
            ("doFireTick", "Enable fire spread"),
            ("showDeathMessages", "Show death messages"),
            ("announceAdvancements", "Announce advancements")
        ]
        
        for rule, description in common_rules:
            rule_frame = ctk.CTkFrame(gamerules_frame)
            rule_frame.pack(fill="x", padx=10, pady=2)
            
            var = ctk.BooleanVar()
            self.gamerule_vars[rule] = var
            
            checkbox = ctk.CTkCheckBox(rule_frame, text=description, variable=var,
                                     command=lambda r=rule: self.toggle_gamerule(r))
            checkbox.pack(side="left", padx=10, pady=5)
        
        # Player Management
        player_frame = ctk.CTkFrame(main_frame)
        player_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(player_frame, text="Player Management", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        
        # Whitelist controls
        whitelist_frame = ctk.CTkFrame(player_frame)
        whitelist_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(whitelist_frame, text="Whitelist:").pack(side="left", padx=5)
        ctk.CTkButton(whitelist_frame, text="On", width=50, command=self.whitelist_on).pack(side="left", padx=2)
        ctk.CTkButton(whitelist_frame, text="Off", width=50, command=self.whitelist_off).pack(side="left", padx=2)
        ctk.CTkButton(whitelist_frame, text="List", width=50, command=self.whitelist_list).pack(side="left", padx=2)
        ctk.CTkButton(whitelist_frame, text="Reload", width=60, command=self.whitelist_reload).pack(side="left", padx=2)
        
        # Add/Remove whitelist entry
        whitelist_manage_frame = ctk.CTkFrame(player_frame)
        whitelist_manage_frame.pack(fill="x", padx=10, pady=5)
        
        self.whitelist_entry = ctk.CTkEntry(whitelist_manage_frame, placeholder_text="Player name...")
        self.whitelist_entry.pack(side="left", padx=5, fill="x", expand=True)
        ctk.CTkButton(whitelist_manage_frame, text="Add", width=50, command=self.whitelist_add_player).pack(side="left", padx=2)
        ctk.CTkButton(whitelist_manage_frame, text="Remove", width=60, command=self.whitelist_remove_player).pack(side="left", padx=2)
        
        # Server Actions
        actions_frame = ctk.CTkFrame(main_frame)
        actions_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(actions_frame, text="Server Actions", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        
        actions_button_frame = ctk.CTkFrame(actions_frame)
        actions_button_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(actions_button_frame, text="Save World", command=self.save_world).pack(side="left", padx=5, fill="x", expand=True)
        ctk.CTkButton(actions_button_frame, text="Reload Server", command=self.reload_server).pack(side="left", padx=5, fill="x", expand=True)
        
        # Close button
        ctk.CTkButton(main_frame, text="Close", command=self.dialog.destroy).pack(pady=20)
        
        # Load current settings
        self.load_current_settings()
        
    def load_current_settings(self):
        """Load current server settings (basic implementation)."""
        try:
            # This is a basic implementation - in a real scenario, you might want to
            # query actual server settings
            pass
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            
    def set_time(self, time_value):
        """Set world time."""
        try:
            response = self.rcon_service.set_time(time_value)
            self.show_response(f"Time set to {time_value}", response)
        except Exception as e:
            self.show_error(f"Failed to set time: {e}")
            
    def set_weather(self, weather_type):
        """Set weather."""
        try:
            response = self.rcon_service.set_weather(weather_type)
            self.show_response(f"Weather set to {weather_type}", response)
        except Exception as e:
            self.show_error(f"Failed to set weather: {e}")
            
    def set_difficulty(self, difficulty):
        """Set difficulty."""
        try:
            response = self.rcon_service.set_difficulty(difficulty)
            self.show_response(f"Difficulty set to {difficulty}", response)
        except Exception as e:
            self.show_error(f"Failed to set difficulty: {e}")
            
    def toggle_gamerule(self, rule):
        """Toggle a game rule."""
        try:
            value = self.gamerule_vars[rule].get()
            response = self.rcon_service.set_gamerule(rule, value)
            self.show_response(f"Game rule {rule} set to {value}", response)
        except Exception as e:
            self.show_error(f"Failed to set game rule: {e}")
            
    def whitelist_on(self):
        """Enable whitelist."""
        try:
            response = self.rcon_service.whitelist_on()
            self.show_response("Whitelist enabled", response)
        except Exception as e:
            self.show_error(f"Failed to enable whitelist: {e}")
            
    def whitelist_off(self):
        """Disable whitelist."""
        try:
            response = self.rcon_service.whitelist_off()
            self.show_response("Whitelist disabled", response)
        except Exception as e:
            self.show_error(f"Failed to disable whitelist: {e}")
            
    def whitelist_list(self):
        """List whitelist."""
        try:
            response = self.rcon_service.whitelist_list()
            self.show_response("Whitelist:", response)
        except Exception as e:
            self.show_error(f"Failed to list whitelist: {e}")
            
    def whitelist_reload(self):
        """Reload whitelist."""
        try:
            response = self.rcon_service.whitelist_reload()
            self.show_response("Whitelist reloaded", response)
        except Exception as e:
            self.show_error(f"Failed to reload whitelist: {e}")
            
    def whitelist_add_player(self):
        """Add player to whitelist."""
        player = self.whitelist_entry.get().strip()
        if not player:
            messagebox.showwarning("Warning", "Please enter a player name")
            return
            
        try:
            response = self.rcon_service.whitelist_add(player)
            self.show_response(f"Added {player} to whitelist", response)
            self.whitelist_entry.delete(0, "end")
        except Exception as e:
            self.show_error(f"Failed to add to whitelist: {e}")
            
    def whitelist_remove_player(self):
        """Remove player from whitelist."""
        player = self.whitelist_entry.get().strip()
        if not player:
            messagebox.showwarning("Warning", "Please enter a player name")
            return
            
        try:
            response = self.rcon_service.whitelist_remove(player)
            self.show_response(f"Removed {player} from whitelist", response)
            self.whitelist_entry.delete(0, "end")
        except Exception as e:
            self.show_error(f"Failed to remove from whitelist: {e}")
            
    def save_world(self):
        """Save the world."""
        try:
            response = self.rcon_service.save_all()
            self.show_response("World saved", response)
        except Exception as e:
            self.show_error(f"Failed to save world: {e}")
            
    def reload_server(self):
        """Reload server."""
        try:
            response = self.rcon_service.reload_server()
            self.show_response("Server reloaded", response)
        except Exception as e:
            self.show_error(f"Failed to reload server: {e}")
            
    def show_response(self, action, response):
        """Show server response."""
        messagebox.showinfo("Server Response", f"{action}\nServer: {response}")
        
    def show_error(self, error_message):
        """Show error message."""
        messagebox.showerror("Error", error_message)


def main():
    """Main entry point for the application."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        app = MinecraftRCONGUI()
        app.run()
    except Exception as e:
        logger.error(f"Application error: {e}")
        messagebox.showerror("Application Error", f"An error occurred: {e}")


if __name__ == "__main__":
    main()