import customtkinter as ctk
import tkinter as tk
from tkinter import font as tkfont
import logging
import sys
from controller import run_traceroute

ctk.set_appearance_mode("dark")


class GuiLogHandler(logging.Handler):
  """Custom logging handler that redirects log messages to the GUI"""

  def __init__(self, gui_instance):
    super().__init__()
    self.gui_instance = gui_instance

  def emit(self, record):
    log_entry = self.format(record)
    level = record.levelname
    self.gui_instance.root_window.after(
        0, lambda: self.gui_instance.cli_print(log_entry, level)
    )


class MainUI:  # <level1>_<level2>_<widget_type>_<purpose>
  def __init__(self) -> None:
    self.root_window = ctk.CTk()
    self.root_window.title("traceLoom")
    self.width = 610
    self.height = 400
    self.root_window.geometry(f"{self.width}x{self.height}")
    self.root_window.minsize(610, 400)
    # self.root_window.resizable(False, False)

    self.current_tab = "cli"

    self.font_mono = ctk.CTkFont(family="Courier New", size=12)
    self.font_base_small = ctk.CTkFont(size=13, weight="normal")
    self.box_size = 18

    # Configure grid layout with 2 columns
    self.root_window.grid_columnconfigure(0, weight=0)  # Sidebar
    self.root_window.grid_columnconfigure(1, weight=1)  # Main area
    self.root_window.grid_rowconfigure(0, weight=1)

    # Side nav
    # -------------------------------------------------------------------
    self.sidebar_frame_options = ctk.CTkFrame(
        self.root_window, width=150, fg_color="#363636"
    )
    self.sidebar_frame_options.grid(
        row=0, column=0, sticky="ns", padx=0, pady=0)

    # Side nav options frame
    # -------------------------------------------------------------------
    self.sidebar_frame_root = ctk.CTkFrame(
        self.sidebar_frame_options, fg_color="transparent"
    )
    self.sidebar_frame_root.pack(fill="both", expand=True, padx=10, pady=10)

    # Enrichment
    # ----------
    self.sidebar_lbl_enrich_title = ctk.CTkLabel(
        self.sidebar_frame_root, fg_color="transparent", text="Enrichment"
    )
    self.sidebar_lbl_enrich_title.pack(anchor="w", pady=(0, 5))

    self.sidebar_chk_enrich_mac = ctk.CTkCheckBox(
        self.sidebar_frame_root,
        text="MAC",
        font=self.font_base_small,
        checkbox_height=self.box_size,
        checkbox_width=self.box_size,
    )
    self.sidebar_chk_enrich_mac.pack(anchor="w", pady=(0, 5))

    self.sidebar_chk_enrich_dns = ctk.CTkCheckBox(
        self.sidebar_frame_root,
        text="DNS",
        font=self.font_base_small,
        checkbox_height=self.box_size,
        checkbox_width=self.box_size,
    )
    self.sidebar_chk_enrich_dns.pack(anchor="w", pady=(0, 5))

    self.sidebar_chk_enrich_ports = ctk.CTkCheckBox(
        self.sidebar_frame_root,
        text="Ports",
        font=self.font_base_small,
        checkbox_height=self.box_size,
        checkbox_width=self.box_size,
    )
    self.sidebar_chk_enrich_ports.pack(anchor="w", pady=(0, 5))

    self.sidebar_chk_os = ctk.CTkCheckBox(
        self.sidebar_frame_root,
        text="OS",
        font=self.font_base_small,
        checkbox_height=self.box_size,
        checkbox_width=self.box_size,
    )
    self.sidebar_chk_os.pack(anchor="w", pady=(0, 5))

    # Logging
    # ----------
    self.sidebar_lbl_logging_title = ctk.CTkLabel(
        self.sidebar_frame_root, fg_color="transparent", text="Logging"
    )
    self.sidebar_lbl_logging_title.pack(anchor="w", pady=(0, 5))

    self.sidebar_cb_logging_level = ctk.CTkComboBox(
        self.sidebar_frame_root, values=["debug", "info", "warning", "error"]
    )
    self.sidebar_cb_logging_level.set("info")
    self.sidebar_cb_logging_level.pack(anchor="w", pady=(0, 5))

    # Logging must be initialized early for GUI output
    self.setup_logging()

    # Target
    # ----------
    self.sidebar_lbl_target_title = ctk.CTkLabel(
        self.sidebar_frame_root, fg_color="transparent", text="Target"
    )
    self.sidebar_lbl_target_title.pack(anchor="w", pady=(0, 5))

    self.sidebar_ent_target_value = ctk.CTkEntry(
        self.sidebar_frame_root, placeholder_text="1.2.3.4"
    )
    self.sidebar_ent_target_value.pack(anchor="w", pady=(0, 5))

    # Run Trace
    # ---------
    self.sidebar_btn_run_trace = ctk.CTkButton(
        self.sidebar_frame_options,
        text="run traceroute",
        command=self.run_traceroute,
        fg_color="#76b869",
        hover_color="#86ca79",
    )
    self.sidebar_btn_run_trace.pack(pady=(0, 5))

    # Main content
    # -------------------------------------------------------------------
    self.main_frame_root = ctk.CTkFrame(self.root_window, corner_radius=0)
    self.main_frame_root.grid(row=0, column=1, sticky="nsew")

    self.main_frame_tabnav = ctk.CTkFrame(
        self.main_frame_root, fg_color="transparent"
    )
    self.main_frame_tabnav.pack(fill="x", padx=0, pady=0)

    self.main_btn_tab_gui = ctk.CTkButton(
        self.main_frame_tabnav,
        text="GUI",
        command=self.show_tb_gui,
        width=80,
        height=10,
        corner_radius=0,
        fg_color="#3B8ED0",
    )
    self.main_btn_tab_gui.pack(side="left", padx=0)

    self.main_btn_tab_cli = ctk.CTkButton(
        self.main_frame_tabnav,
        text="CLI",
        command=self.show_tb_cli,
        width=80,
        height=10,
        corner_radius=0,
        fg_color="#1E5079",
        text_color="#8C8F91",
    )
    self.main_btn_tab_cli.pack(side="left", padx=0)

    self.main_frame_tabcontainer = ctk.CTkFrame(self.main_frame_root)
    self.main_frame_tabcontainer.pack(fill="both", expand=True, padx=0, pady=0)

    # GUI tab
    # ---------------
    self.tab_gui_frame = ctk.CTkFrame(
        self.main_frame_tabcontainer,
        fg_color="#2b2b2b",
        corner_radius=0
    )
    self.tab_gui_lbl_placeholder = ctk.CTkLabel(self.tab_gui_frame, text="GUI")
    self.tab_gui_lbl_placeholder.pack(pady=0)
    
    

    # CLI tab
    # ---------------
    self.tab_cli_frame = ctk.CTkFrame(
        self.main_frame_tabcontainer,
        fg_color="#2b2b2b",
        corner_radius=0
    )

    self.tab_cli_txt_output = ctk.CTkTextbox(
        self.tab_cli_frame,
        font=self.font_mono,
        fg_color="#000000",
        text_color="#ffffff",
        scrollbar_button_color="#555555",
        wrap="word",
        corner_radius=0
    )
    self.tab_cli_txt_output.pack(fill="both", expand=True, padx=0, pady=(0, 2))

    self.tab_cli_txt_output.tag_config("DEBUG", foreground="#888888")
    self.tab_cli_txt_output.tag_config("INFO", foreground="#FFFFFF")
    self.tab_cli_txt_output.tag_config("WARNING", foreground="#FFA500")
    self.tab_cli_txt_output.tag_config("ERROR", foreground="#FF5555")
    self.tab_cli_txt_output.tag_config(
        "CRITICAL", foreground="#FF0000", underline=True)

    self.tab_cli_txt_output.insert("end",
"""  ▄▄▄▄▄▄▄▄   ▄▄▄   ▄▄  ▄▄▄  ▄▄    ▄▄▄▄  ▄▄▄▄   ▄   ▄    
   ██  ▀▄ █ ▐█ ▀█ ▐█ ▌ ▀▄ ▀ ██   ▐█  ▐▌▐█  ▐▌ ██ ▐███  
   ▐█  ▐▀▀▄ ▄█▀▀█ ██ ▄▄▐▀▀ ▄██   ▐█  ▐▌▐█  ▐▌▐█ ▌▐▌▐█ 
   ▐█▌ ▐█ █▌▐█  ▐▌▐███▌▐█▄▄▌▐█▌▐▌▐█▌ ▐▌▐█▌ ▐▌██ ██▌▐█▌
   ▀▀▀  ▀  ▀ ▀  ▀  ▀▀▀  ▀▀▀  ▀▀▀  ▀▀▀▀  ▀▀▀▀ ▀▀    ▀▀▀\n""")

    self.tab_cli_txt_output.configure(state="disabled")

    self.tab_cli_controls = ctk.CTkFrame(
        self.tab_cli_frame, fg_color="transparent")
    self.tab_cli_controls.pack(pady=(0, 5), anchor="e", padx=(0, 5))

    self.tab_cli_chk_autoclear = ctk.CTkCheckBox(
        self.tab_cli_controls,
        text="Auto-clear",
        font=self.font_base_small,
        checkbox_height=self.box_size,
        checkbox_width=self.box_size,
    )
    self.tab_cli_chk_autoclear.pack(side="left", padx=(0, 5))

    self.tab_cli_btn_clear = ctk.CTkButton(
        self.tab_cli_controls, text="Clear", command=self.cli_clear
    )
    self.tab_cli_btn_clear.pack(side="left")

    # Show default tab
    self.show_tb_gui()

  # GUI Functions

  def show_tb_gui(self):
    self.tab_cli_frame.pack_forget()
    self.tab_gui_frame.pack(fill="both", expand=True)
    self.current_tab = "gui"

    self.main_btn_tab_gui.configure(fg_color="#3B8ED0", text_color="#FFFFFF")
    self.main_btn_tab_cli.configure(fg_color="#1E5079", text_color="#8C8F91")

  def show_tb_cli(self):
    self.tab_gui_frame.pack_forget()
    self.tab_cli_frame.pack(fill="both", expand=True)
    self.current_tab = "cli"

    self.main_btn_tab_cli.configure(fg_color="#3B8ED0", text_color="#FFFFFF")
    self.main_btn_tab_gui.configure(fg_color="#1E5079", text_color="#8C8F91")

  def cli_print(self, text: str, level: str = "INFO"):
    self.tab_cli_txt_output.configure(state="normal")
    self.tab_cli_txt_output.insert("end", f"{text}\n", level.upper())
    self.tab_cli_txt_output.see("end")
    self.tab_cli_txt_output.configure(state="disabled")

  def cli_clear(self):
    self.tab_cli_txt_output.configure(state="normal")
    self.tab_cli_txt_output.delete("1.0", "end")
    self.tab_cli_txt_output.configure(state="disabled")

  def setup_logging(self):
    """Configure logging to output to GUI"""
    gui_handler = GuiLogHandler(self)
    formatter = logging.Formatter('%(message)s')
    gui_handler.setFormatter(formatter)
    logging.getLogger().addHandler(gui_handler)
    log_level = self.sidebar_cb_logging_level.get().upper()
    level = getattr(logging, log_level, logging.DEBUG)
    logging.getLogger().setLevel(level)
    gui_handler.setLevel(level)
    self.gui_handler = gui_handler

  def update_logging_level(self):
    """Update the logging level based on current combobox selection"""
    log_level = self.sidebar_cb_logging_level.get().upper()
    level = getattr(logging, log_level, logging.INFO)
    logging.getLogger().setLevel(level)
    self.gui_handler.setLevel(level)

  def run_traceroute(self):
    # Add this line to update logging level before running traceroute
    self.update_logging_level()

    if self.tab_cli_chk_autoclear.get():
      self.cli_clear()
    dns_en = self.sidebar_chk_enrich_dns.get()
    mac_en = self.sidebar_chk_enrich_mac.get()
    ports_en = self.sidebar_chk_enrich_ports.get()
    os_en = self.sidebar_chk_os.get()
    log_level = self.sidebar_cb_logging_level.get()
    target = self.sidebar_ent_target_value.get()
    self.cli_print("───────────────────────────────────────────────────────")
    self.cli_print(f"           traceroute started to {target}")
    self.cli_print("───────────────────────────────────────────────────────")
    run_traceroute(
        target=target,
        logging_level=log_level,
        dns=dns_en,
        mac=mac_en,
        ports=ports_en,
        os=os_en
    )

  def run(self) -> None:
    self.root_window.mainloop()


window = MainUI()
window.run()
