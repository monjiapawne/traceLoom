import customtkinter as ctk
import tkinter as tk
from PIL import Image
import os
from tkinter import font as tkfont
from tkinter import filedialog
import logging
import json
import os
from controller import run_traceroute

ctk.set_appearance_mode("dark")


class GuiLogHandler(logging.Handler):
    def __init__(self, gui_instance):
        super().__init__()
        self.gui_instance = gui_instance

    def emit(self, record):
        log_entry = self.format(record)
        level = record.levelname
        self.gui_instance.root_window.after(
            0, lambda: self.gui_instance.cli_print(log_entry, level)
        )


class MainUI:
    CONFIG = {
        "base_radius": 15,
        "min_spacing": 60,
        "font_scale_main": 1,
        "font_scale_label": 1,
        "line_color": "#888888",
        "background_color": "#2b2b2b",
        "font_family": "Arial",
        "hop_spacing_multiplier": 10,
        "null_spacing_override": 40,
    }

    HOP_STYLES = {
        "*": {
            "size": 0.7,
            "fill": "#2e2e2e",
            "outline": "#555555",
            "text": "#aaaaaa",
            "ip": "#888888",
            "detail": "#666666",
        },
        "[router]": {
            "size": 1.0,
            "fill": "#2b3a1e",
            "outline": "#a9c84e",
            "text": "#ffffff",
            "ip": "#e3ff6a",
            "detail": "#b6ff00",
        },
        "default": {
            "size": 1.0,
            "fill": "#1c1c1c",
            "outline": "#444444",
            "text": "#ffffff",
            "ip": "#cccccc",
            "detail": "#81ddff",
        },
    }

    def __init__(self) -> None:
        self.root_window = ctk.CTk()
        self.root_window.title("traceLoom")
        self.width = 610
        self.height = 400
        self.root_window.geometry(f"{self.width}x{self.height}")
        self.root_window.minsize(610, 400)
        
        self.current_trace_path = None
        self.nulls_enabled = True

        self.current_tab = "cli"
        self.font_mono = ctk.CTkFont(family="Courier New", size=12)
        self.font_base_small = ctk.CTkFont(size=13, weight="normal")
        self.box_size = 18

        self.root_window.grid_columnconfigure(0, weight=0)
        self.root_window.grid_columnconfigure(1, weight=1)
        self.root_window.grid_rowconfigure(0, weight=1)

        self.sidebar_frame_options = ctk.CTkFrame(self.root_window, width=150, fg_color="#363636")
        self.sidebar_frame_options.grid(row=0, column=0, sticky="ns")

        self.sidebar_frame_root = ctk.CTkFrame(self.sidebar_frame_options, fg_color="transparent")
        self.sidebar_frame_root.pack(fill="both", expand=True, padx=10, pady=10)

        self.sidebar_lbl_enrich_title = ctk.CTkLabel(self.sidebar_frame_root, text="Enrichment")
        self.sidebar_lbl_enrich_title.pack(anchor="w", pady=(0, 5))

        self.sidebar_chk_enrich_mac = ctk.CTkCheckBox(self.sidebar_frame_root, text="MAC", font=self.font_base_small,
                                                      checkbox_height=self.box_size, checkbox_width=self.box_size)
        self.sidebar_chk_enrich_mac.pack(anchor="w", pady=(0, 5))

        self.sidebar_chk_enrich_dns = ctk.CTkCheckBox(self.sidebar_frame_root, text="DNS", font=self.font_base_small,
                                                      checkbox_height=self.box_size, checkbox_width=self.box_size)
        self.sidebar_chk_enrich_dns.pack(anchor="w", pady=(0, 5))

        self.sidebar_chk_enrich_ports = ctk.CTkCheckBox(self.sidebar_frame_root, text="Ports",
                                                        font=self.font_base_small, checkbox_height=self.box_size,
                                                        checkbox_width=self.box_size)
        self.sidebar_chk_enrich_ports.pack(anchor="w", pady=(0, 5))

        self.sidebar_chk_os = ctk.CTkCheckBox(self.sidebar_frame_root, text="OS", font=self.font_base_small,
                                              checkbox_height=self.box_size, checkbox_width=self.box_size)
        self.sidebar_chk_os.pack(anchor="w", pady=(0, 5))

        self.sidebar_lbl_logging_title = ctk.CTkLabel(self.sidebar_frame_root, text="Logging")
        self.sidebar_lbl_logging_title.pack(anchor="w", pady=(0, 5))

        self.sidebar_cb_logging_level = ctk.CTkComboBox(self.sidebar_frame_root,
                                                        values=["debug", "info", "warning", "error"])
        self.sidebar_cb_logging_level.set("info")
        self.sidebar_cb_logging_level.pack(anchor="w", pady=(0, 5))

        self.setup_logging()

        self.sidebar_lbl_target_title = ctk.CTkLabel(self.sidebar_frame_root, text="Target")
        self.sidebar_lbl_target_title.pack(anchor="w", pady=(0, 5))

        self.sidebar_ent_target_value = ctk.CTkEntry(self.sidebar_frame_root, placeholder_text="1.2.3.4")
        self.sidebar_ent_target_value.pack(anchor="w", pady=(0, 5))

        ico_star_1 = ctk.CTkImage(light_image=Image.open(os.path.join("resources", "images", "rocket_d.png")), size=(16, 16))
        self.sidebar_btn_run_trace = ctk.CTkButton(
            self.sidebar_frame_options,
            image=ico_star_1,
            compound='left',
            text="traceroute",
            command=self.run_traceroute,
            width=120,
            height=30,
            corner_radius=20,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#4CAF50",
            hover_color="#66BB6A",
            text_color="white"
        )
        self.sidebar_btn_run_trace.pack(pady=(5, 5), padx=5)

        self.main_frame_root = ctk.CTkFrame(self.root_window, corner_radius=0)
        self.main_frame_root.grid(row=0, column=1, sticky="nsew")

        self.main_frame_tabnav = ctk.CTkFrame(self.main_frame_root, fg_color="transparent")
        self.main_frame_tabnav.pack(fill="x")

        self.main_btn_tab_gui = ctk.CTkButton(self.main_frame_tabnav, text="GUI", command=self.show_tb_gui,
                                              width=80, height=10, corner_radius=0, fg_color="#3B8ED0", hover_color="#2D6897")
        self.main_btn_tab_gui.pack(side="left")

        self.main_btn_tab_cli = ctk.CTkButton(self.main_frame_tabnav, text="CLI", command=self.show_tb_cli,
                                              width=80, height=10, corner_radius=0,
                                              fg_color="#1E5079", text_color="#8C8F91", hover_color="#2D6897")
        self.main_btn_tab_cli.pack(side="left")

        self.main_frame_tabcontainer = ctk.CTkFrame(self.main_frame_root)
        self.main_frame_tabcontainer.pack(fill="both", expand=True)

        # Gui Tab Theme
        self.THEME = {
            "background": "#121212",
            "foreground": "#ffffff",
            "accent": "#00ffff",
            "canvas_bg": "#020513",
            "outline_default": "#444444",
            "outline_selected": "#00ffff",
        }
        
        self.zoom_level = 1.0

        self.tab_gui_frame = ctk.CTkFrame(self.main_frame_tabcontainer, fg_color=self.THEME["background"],
                                          corner_radius=0)
        self.tab_gui_frame.grid_rowconfigure(0, weight=1)
        self.tab_gui_frame.grid_rowconfigure(1, weight=0)
        self.tab_gui_frame.grid_columnconfigure(0, weight=1)
        
        self.selected_hops = set()
        self.hop_oval_map = {}
        self.hop_data = {}

        self.trace_canvas_container = None

        self.tab_gui_controls = ctk.CTkFrame(self.tab_gui_frame, fg_color="transparent")
        self.tab_gui_controls.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        self.tab_gui_controls.grid_columnconfigure(0, weight=1)
        self.tab_gui_controls.grid_columnconfigure(1, weight=1)
        self.tab_gui_controls.grid_columnconfigure(2, weight=1)
        self.tab_gui_controls.grid_columnconfigure(3, weight=1)
        
        ico_import_json = ctk.CTkImage(light_image=Image.open(os.path.join("resources", "images", "arrow_d.png")), size=(16, 16))
        self.tab_gui_btn_import_json = ctk.CTkButton(
            self.tab_gui_controls,
            text="Import JSON",
            compound="left",
            image=ico_import_json,
            width=100,
            height=15,
            hover_color="#4C98D6",
            command=lambda: self.import_trace_file()
        )
        self.tab_gui_btn_import_json.grid(row=0, column=0, sticky="w", padx=(0, 5))
        
        ico_eye = ctk.CTkImage(light_image=Image.open(os.path.join("resources", "images", "eye_d.png")), size=(16, 16))
        self.tab_gui_btn_toggle_null_render = ctk.CTkButton(
            self.tab_gui_controls,
            text="Hide *",
            compound="left",
            image=ico_eye,
            width=100,
            height=15,
            hover_color="#4C98D6",
            command=self.hide_null_hops
        )
        self.tab_gui_btn_toggle_null_render.grid(row=0, column=1, sticky="w", padx=(0, 5))
        
        ico_reset = ctk.CTkImage(light_image=Image.open(os.path.join("resources", "images", "reset_d.png")), size=(16, 16))
        self.tab_gui_btn_reset_zoom = ctk.CTkButton(
            self.tab_gui_controls,
            text="Reset View",
            image=ico_reset,
            compound='left',
            width=100,
            height=15,
            hover_color="#4C98D6",
            command=self.reset_zoom
        )
        self.tab_gui_btn_reset_zoom.grid(row=0, column=2, padx=5)

        ico_stars = ctk.CTkImage(light_image=Image.open(os.path.join("resources", "images", "stars_d.png")), size=(16, 16))
        self.tab_gui_btn_enrich_hops = ctk.CTkButton(
            self.tab_gui_controls,
            text="Enrich Hops",
            image=ico_stars,
            compound="left",
            width=100,
            height=15,
            hover_color="#4C98D6",
            command=lambda: self.enrich_selected_hops()
        )
        self.tab_gui_btn_enrich_hops.grid(row=0, column=3, sticky="e")

        self.tab_cli_frame = ctk.CTkFrame(self.main_frame_tabcontainer, fg_color="#2b2b2b", corner_radius=0)

        self.tab_cli_txt_output = ctk.CTkTextbox(self.tab_cli_frame, font=self.font_mono, fg_color="#000000",
                                                 text_color="#ffffff", scrollbar_button_color="#555555",
                                                 wrap="word", corner_radius=0)
        self.tab_cli_txt_output.pack(fill="both", expand=True, pady=(0, 2))

        self.tab_cli_txt_output.tag_config("DEBUG", foreground="#888888")
        self.tab_cli_txt_output.tag_config("INFO", foreground="#FFFFFF")
        self.tab_cli_txt_output.tag_config("WARNING", foreground="#FFA500")
        self.tab_cli_txt_output.tag_config("ERROR", foreground="#FF5555")
        self.tab_cli_txt_output.tag_config("CRITICAL", foreground="#FF0000", underline=True)

        self.tab_cli_txt_output.insert("end", """  ▄▄▄▄▄▄▄▄   ▄▄▄   ▄▄  ▄▄▄  ▄▄    ▄▄▄▄  ▄▄▄▄   ▄   ▄    
   ██  ▀▄ █ ▐█ ▀█ ▐█ ▌ ▀▄ ▀ ██   ▐█  ▐▌▐█  ▐▌ ██ ▐███  
   ▐█  ▐▀▀▄ ▄█▀▀█ ██ ▄▄▐▀▀ ▄██   ▐█  ▐▌▐█  ▐▌▐█ ▌▐▌▐█ 
   ▐█▌ ▐█ █▌▐█  ▐▌▐███▌▐█▄▄▌▐█▌▐▌▐█▌ ▐▌▐█▌ ▐▌██ ██▌▐█▌
   ▀▀▀  ▀  ▀ ▀  ▀  ▀▀▀  ▀▀▀  ▀▀▀  ▀▀▀▀  ▀▀▀▀ ▀▀    ▀▀▀\n""")
        self.tab_cli_txt_output.configure(state="disabled")

        self.tab_cli_controls = ctk.CTkFrame(self.tab_cli_frame, fg_color="transparent")
        self.tab_cli_controls.pack(pady=(0, 5), anchor="e", padx=(0, 5))

        self.tab_cli_chk_autoclear = ctk.CTkCheckBox(self.tab_cli_controls, text="Auto-clear",
                                                     font=self.font_base_small,
                                                     checkbox_height=self.box_size, checkbox_width=self.box_size)
        self.tab_cli_chk_autoclear.pack(side="left", padx=(0, 5))

        self.tab_cli_btn_clear = ctk.CTkButton(self.tab_cli_controls, text="Clear", command=self.cli_clear)
        self.tab_cli_btn_clear.pack(side="left")
        
        self.show_tb_gui()


    def run(self) -> None:
        self.root_window.mainloop()

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
        log_level = self.sidebar_cb_logging_level.get().upper()
        level = getattr(logging, log_level, logging.INFO)
        logging.getLogger().setLevel(level)
        self.gui_handler.setLevel(level)

    def run_traceroute(self):
        self.update_logging_level()
        if self.tab_cli_chk_autoclear.get():
            self.cli_clear()
        dns_en = self.sidebar_chk_enrich_dns.get()
        mac_en = self.sidebar_chk_enrich_mac.get()
        ports_en = self.sidebar_chk_enrich_ports.get()
        os_en = self.sidebar_chk_os.get()
        log_level = self.sidebar_cb_logging_level.get()
        target = self.sidebar_ent_target_value.get()
        self.cli_print(f"─────── traceroute started to {target} ───────────")
        trace_json = run_traceroute(
            target=target,
            logging_level=log_level,
            dns=dns_en,
            mac=mac_en,
            ports=ports_en,
            os=os_en
        )
        if trace_json:
          self.import_trace_file(file_path=trace_json)
        
    def import_trace_file(self, file_path=None, nulls_enabled:bool = True):
        import os
        import json
        from tkinter import filedialog

        if not file_path:
            file_path = filedialog.askopenfilename(
                title="Select a trace JSON file",
                initialdir=os.getcwd(),
                filetypes=[("JSON files", "*.json")]
            )
            if not file_path:
                return  # User cancelled

        try:
            with open(file_path, "r") as f:
                trace_sample = json.load(f)
            self.current_trace_path = file_path
            self.draw_trace_from_json(trace_sample, nulls_enabled)
            print(f"[INFO] Imported trace file: {file_path}")
        except Exception as e:
            print(f"[ERROR] Failed to load JSON: {e}")

    def get_hop_style(self, ip, details):
        if ip == "*":
            for key, value in details.items():
                k = key.strip().lower()
                v = str(value).strip().upper()
                if k == "mac_address" and v == "LAYER 3":
                    return self.HOP_STYLES["[router]"]
            return self.HOP_STYLES["*"]

        for key, value in details.items():
            k = key.strip().lower()
            v = str(value).strip().upper()
            if (k == "type" and v == "ROUTER") or (k == "mac_address" and v == "LAYER 3"):
                return self.HOP_STYLES["[router]"]

        return self.HOP_STYLES["default"]

    def enrich_selected_hops(self):
        if not self.selected_hops:
            self.cli_print("[ENRICH] No hops selected.", "WARNING")
            return
        self.cli_print("────── Enriching Selected Hops ──────")
        for hop_id in sorted(self.selected_hops):
            hop = self.hop_data.get(hop_id)
            if not hop:
                continue
            ip = hop["ip"]
            if ip != "*":
                self.cli_print(f"[ENRICH] Targeting IP: {ip}", "INFO")
                print(f"[ENRICH] Targeting IP: {ip}", "INFO")

    def draw_circle_with_text(self, canvas, x, y, r, hop_num, ip, details):
        style = self.get_hop_style(ip, details)
        size = style["size"]
        r = int(r * size)
        font_main = ("Segoe UI", int(10 * self.CONFIG["font_scale_main"]), "bold")
        font_label = ("Segoe UI", int(9 * self.CONFIG["font_scale_label"]))
        item_ids = []
        oval_id = canvas.create_oval(x - r, y - r, x + r, y + r, fill=style["fill"],
                                     outline=style["outline"], width=2)
        item_ids.append(oval_id)
        text_id = canvas.create_text(x, y, text=str(hop_num), fill=style["text"], font=font_main)
        item_ids.append(text_id)
        ip_text_id = canvas.create_text(x + r + 10, y, text=ip, anchor="w",
                                        fill=style["ip"], font=font_main)
        item_ids.append(ip_text_id)
        detail_y = y + int(15 * size)
        for key, value in details.items():
            canvas.create_text(x + r + 10, detail_y, text=f"{key}: {value}",
                               anchor="w", fill=style["detail"], font=font_label)
            detail_y += int(13 * size)
        return item_ids, oval_id

    def draw_trace_from_json(self, trace_data, nulls_enabled):
        # Clear old canvas container if it exists
        if self.trace_canvas_container:
            self.trace_canvas_container.destroy()

        # reset state
        self.selected_hops = set()
        self.hop_oval_map = {}

        # layout init
        r = self.CONFIG["base_radius"]
        min_spacing = self.CONFIG["min_spacing"]
        start_x = 20
        start_y = 50

        self.trace_canvas_container = tk.Frame(self.tab_gui_frame, bg=self.THEME["canvas_bg"])
        self.trace_canvas_container.grid(row=0, column=0, sticky="nsew")

        canvas = tk.Canvas(self.trace_canvas_container, bg=self.THEME["canvas_bg"], highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(self.trace_canvas_container, orientation="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.bind("<Configure>", on_configure)

        # hop loop
        nodes = trace_data.get("nodes", {})
        y = start_y
        prev_y = None
        prev_r = None
        for i, hop_key in enumerate(sorted(nodes, key=lambda k: int(k)), start=1):
            node = nodes[hop_key]
            raw_ip = node.get("ip")
            if nulls_enabled and (raw_ip is None or raw_ip == '*'):
                continue
            ip = raw_ip or "*"
            details = {k: v for k, v in node.items() if k != "ip" and v is not None}
            latency_str = node.get("latency", "")
            try:
                latency_ms = float(latency_str.replace("ms", "").strip())
            except:
                latency_ms = 0.0

            style = self.get_hop_style(ip, details)
            spacing = self.CONFIG["null_spacing_override"] if ip == "*" else min_spacing + int(
                latency_ms * self.CONFIG["hop_spacing_multiplier"])
            scaled_r = int(r * style["size"])

            # draw connection line
            if prev_y is not None:
                canvas.create_line(start_x, prev_y + prev_r + 1, start_x, y - scaled_r - 0.5,
                                   fill=self.CONFIG["line_color"], width=7)

            # draw node
            item_ids, oval_id = self.draw_circle_with_text(canvas, start_x, y, r, i, ip, details)

            hop_id = f"hop_{i}"
            self.hop_oval_map[hop_id] = oval_id
            self.hop_data[hop_id] = {"ip": ip, "details": details}

            # selection toggle
            def make_toggle_callback(hop_id, oval_id):
                def toggle(event):
                    if hop_id in self.selected_hops:
                        self.selected_hops.remove(hop_id)
                        canvas.itemconfig(oval_id, outline=self.THEME["outline_default"], width=2)
                    else:
                        self.selected_hops.add(hop_id)
                        canvas.itemconfig(oval_id, outline=self.THEME["outline_selected"], width=4)
                    print(f"[SELECTED]: {sorted(self.selected_hops)}")
                return toggle

            toggle_callback = make_toggle_callback(hop_id, oval_id)

            # bind events
            for item_id in item_ids:
                canvas.tag_bind(item_id, "<Button-1>", toggle_callback)
                canvas.tag_bind(item_id, "<Enter>", lambda e: canvas.config(cursor="hand2"))
                canvas.tag_bind(item_id, "<Leave>", lambda e: canvas.config(cursor=""))

            prev_y = y
            prev_r = scaled_r
            y += spacing

            canvas.update_idletasks()

        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.yview_moveto(0)

        # mouse wheel scroll
        def _on_mousewheel(event):
          bbox = canvas.bbox("all")
          if bbox:
              _, y1, _, y2 = bbox
              content_height = y2 - y1
              if content_height <= canvas.winfo_height():
                  return
          canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        # win scroll
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # linux scroll
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
        canvas.xview_moveto(0)

        def start_drag(event):
            canvas.scan_mark(event.x, event.y)
            canvas.config(cursor="hand2")

        def drag_scroll(event):
            bbox = canvas.bbox("all")
            if bbox:
                _, y1, _, y2 = bbox
                content_height = y2 - y1
                if content_height <= canvas.winfo_height():
                    return
            canvas.scan_dragto(int(canvas.canvasx(0)), event.y, gain=1)

        # Reset to default
        def end_drag(event):
            canvas.config(cursor="")

        canvas.bind("<ButtonPress-1>", start_drag)
        canvas.bind("<B1-Motion>", drag_scroll)
        canvas.bind("<ButtonRelease-1>", end_drag)

        def zoom(event):
            if event.state & 0x0004:  # control key
                scale = 1.1 if event.delta > 0 else 0.9
                new_zoom = self.zoom_level * scale
                if 0.5 <= new_zoom <= 2.0:
                    self.zoom_level = new_zoom
                    canvas.scale("all", 0, 0, scale, scale)
                    canvas.configure(scrollregion=canvas.bbox("all"))
                    
        canvas.bind("<MouseWheel>", zoom)  # win
        canvas.bind("<Control-MouseWheel>", zoom)  # fallback
        canvas.bind("<Control-Button-4>", lambda e: zoom(MockEvent(delta=120, state=0x0004)))  # liunx
        canvas.bind("<Control-Button-5>", lambda e: zoom(MockEvent(delta=-120, state=0x0004)))

    def reset_zoom(self):
        if not self.trace_canvas_container:
            return
        canvas = self.trace_canvas_container.winfo_children()[0]
        if not isinstance(canvas, tk.Canvas):
            return

        scale_factor = 1.0 / self.zoom_level
        self.zoom_level = 1.0

        canvas.scale("all", 0, 0, scale_factor, scale_factor)
        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

        # Reset scroll to top or center if short
        bbox = canvas.bbox("all")
        if bbox:
            x1, y1, x2, y2 = bbox
            content_height = y2 - y1
            canvas_height = canvas.winfo_height()
            if content_height < canvas_height:
                offset = (canvas_height - content_height) / 2
                canvas.yview_moveto(offset / content_height)
            else:
                canvas.yview_moveto(0)
    
    def hide_null_hops(self):
        if not self.current_trace_path:
            self.cli_print("[WARN] No trace file loaded yet.", "WARNING")
            return
        # Toggle state
        self.nulls_enabled = not self.nulls_enabled
        # Redraw with current toggle state
        self.import_trace_file(file_path=self.current_trace_path, nulls_enabled=self.nulls_enabled)


class MockEvent:
    def __init__(self, delta, state):
        self.delta = delta
        self.state = state


window = MainUI()
window.run()