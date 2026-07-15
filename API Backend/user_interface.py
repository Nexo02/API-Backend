# -*- coding: utf-8 -*-
"""
LoreEngine v1.1 - User Interface Layout
Houses visual widgets, collapsible sidebars, and customizable theme hooks.
"""

import tkinter as tk
import customtkinter as ctk


# By replacing the CTkTextbox tag_config method with its raw underlying tkinter text method,
# we bypass the "font option forbidden" AttributeError, enabling rich text styles safely!
def patched_tag_config(self, tagName, **kwargs):
    return self._textbox.tag_config(tagName, **kwargs)


ctk.CTkTextbox.tag_config = patched_tag_config

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class OrganizedRoleplayApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Settings
        self.title("LoreEngine v1.1 - Persistence Session Space")
        self.geometry("1250x780")
        self.minsize(950, 650)

        # Dynamic, low-saturation earth-toned cozy palette selections
        self.color_palettes = {
            "Muted Denim": {"accent": "#4a6375", "hover": "#3b4f5e"},  # Comforting desaturated slate blue
            "Sage Leaf": {"accent": "#6b8271", "hover": "#55685a"},  # Calm, dusty organic green
            "Soft Rust": {"accent": "#a27163", "hover": "#855c50"},  # Warm, gentle terracotta clay
            "Dusky Heather": {"accent": "#7d6b82", "hover": "#645568"},  # Cozy, desaturated lavender/purple
            "Warm Oat": {"accent": "#968375", "hover": "#7a6a5e"}  # Earthy, soft brown-gray neutral
        }
        self.current_palette = "Muted Denim"
        self.accent_widgets = []  # Tracks custom colored widgets for live recoloring

        # State managers
        self.sidebar_visible = True
        self.art_panel_visible = True

        # --- CORE GRID STRUCTURE ---
        # Column 0: Collapsible Configuration Sidebar (left)
        # Column 1: Chat Workspace (center)
        # Column 2: Collapsible Scene Art/Image Panel (right)
        self.grid_columnconfigure(0, weight=0, minsize=330)
        self.grid_columnconfigure(1, weight=4)
        self.grid_columnconfigure(2, weight=0, minsize=290)
        self.grid_rowconfigure(0, weight=1)

        # Create GUI regions
        self.create_left_sidebar()
        self.create_center_chat()
        self.create_right_art_panel()

        # Start with art canvas closed by default.
        self.toggle_art_panel()

        self.change_accent_palette("Muted Denim")

    def create_left_sidebar(self):
        """Constructs the sidebar which now houses all configuration and info tabs."""
        self.sidebar_container = ctk.CTkFrame(self, corner_radius=0, width=330)
        self.sidebar_container.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar_container.grid_propagate(False)

        # Sidebar Title
        self.logo_lbl = ctk.CTkLabel(
            self.sidebar_container,
            text="LoreEngine v1.1",
            font=ctk.CTkFont(family="Consolas", size=22, weight="bold")
        )
        self.logo_lbl.pack(padx=15, pady=(20, 10))

        # Nested Configuration Tabview
        self.config_tabs = ctk.CTkTabview(self.sidebar_container)
        self.config_tabs.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.config_tabs.add("Dashboard")
        self.config_tabs.add("Characters")
        self.config_tabs.add("Users")
        self.config_tabs.add("Lorebook")
        self.config_tabs.add("Settings")

        self.setup_dashboard_tab()
        self.setup_characters_tab()
        self.setup_user_tab()
        self.setup_lorebook_tab()
        self.setup_settings_tab()

    def setup_dashboard_tab(self):
        """Sets up the primary dashboard monitoring tab."""
        tab = self.config_tabs.tab("Dashboard")

        # ACTIVE SESSION MANAGER
        session_hdr = ctk.CTkLabel(tab, text="Select Roleplay Session:", font=ctk.CTkFont(weight="bold"))
        session_hdr.pack(fill="x", pady=(5, 2), anchor="w")

        self.session_dropdown = ctk.CTkOptionMenu(
            tab,
            values=["Create a session to begin"],
            command=lambda val: self.handle_session_changed()
        )
        self.session_dropdown.pack(fill="x", pady=(0, 15))
        self.accent_widgets.append((self.session_dropdown, "optionmenu"))

        # Active Model selection
        model_hdr = ctk.CTkLabel(tab, text="Active Narrative Model:", font=ctk.CTkFont(weight="bold"))
        model_hdr.pack(fill="x", pady=(10, 2), anchor="w")

        self.model_dropdown = ctk.CTkOptionMenu(
            tab,
            values=["deepseek/deepseek-chat", "anthropic/claude-3.5-sonnet", "meta-llama/llama-3.1-70b-instruct"]
        )
        self.model_dropdown.pack(fill="x", pady=(0, 15))
        self.accent_widgets.append((self.model_dropdown, "optionmenu"))

        # Monitor metrics
        metrics_hdr = ctk.CTkLabel(tab, text="Memory Hub Stats:", font=ctk.CTkFont(weight="bold"))
        metrics_hdr.pack(fill="x", pady=(10, 5), anchor="w")

        self.token_label = ctk.CTkLabel(tab, text="Active Conversational Window: 0 turns", anchor="w", text_color="gray70")
        self.token_label.pack(fill="x", pady=2)

        self.summary_label = ctk.CTkLabel(tab, text="Stored Epic Summaries: 0", anchor="w", text_color="gray70")
        self.summary_label.pack(fill="x", pady=2)

        self.lore_label = ctk.CTkLabel(tab, text="Vector Lore Entries: 0", anchor="w", text_color="gray70")
        self.lore_label.pack(fill="x", pady=2)

        # Trigger Actions (Updated with dynamic lambda lookup)
        self.view_lore_btn = ctk.CTkButton(tab, text="Scan Vector Index", command=lambda: self.simulated_scan())
        self.view_lore_btn.pack(fill="x", pady=(25, 8))
        self.accent_widgets.append((self.view_lore_btn, "button"))

        # Updated with dynamic lambda lookup
        self.force_summary_btn = ctk.CTkButton(
            tab,
            text="Compress Active Arc",
            fg_color="transparent",
            border_width=1,
            command=lambda: self.simulate_manual_summary()
        )
        self.force_summary_btn.pack(fill="x", pady=5)
        self.accent_widgets.append((self.force_summary_btn, "border_button"))

    def setup_characters_tab(self):
        """Constructs the character catalog profile suite inside the left sidebar."""
        tab = self.config_tabs.tab("Characters")

        scroll_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=2, pady=2)

        # Selection selector
        select_lbl = ctk.CTkLabel(scroll_frame, text="Active Character Profile:", font=ctk.CTkFont(weight="bold"))
        select_lbl.pack(fill="x", pady=(5, 2), anchor="w")

        self.char_dropdown = ctk.CTkOptionMenu(
            scroll_frame,
            values=["New Character..."],
            command=lambda val: self.handle_character_dropdown_changed()
        )
        self.char_dropdown.pack(fill="x", pady=(0, 15))
        self.accent_widgets.append((self.char_dropdown, "optionmenu"))

        # Character fields
        name_lbl = ctk.CTkLabel(scroll_frame, text="Character Name:", font=ctk.CTkFont(size=11, weight="bold"), text_color="gray70")
        name_lbl.pack(fill="x", pady=(5, 2), anchor="w")
        self.char_name_field = ctk.CTkEntry(scroll_frame)
        self.char_name_field.pack(fill="x", pady=(0, 10))

        desc_lbl = ctk.CTkLabel(scroll_frame, text="Character Lore / Description:", font=ctk.CTkFont(size=11, weight="bold"), text_color="gray70")
        desc_lbl.pack(fill="x", pady=(5, 2), anchor="w")
        self.char_desc_field = ctk.CTkTextbox(scroll_frame, height=120, wrap="word", font=ctk.CTkFont(size=12))
        self.char_desc_field.pack(fill="x", pady=(0, 10))

        # Avatar path visualization
        self.avatar_path_lbl = ctk.CTkLabel(scroll_frame, text="Avatar: None", font=ctk.CTkFont(size=10, slant="italic"), text_color="gray50", anchor="w")
        self.avatar_path_lbl.pack(fill="x", pady=2)

        self.avatar_btn = ctk.CTkButton(
            scroll_frame,
            text="Upload Profile Picture",
            fg_color="transparent",
            border_width=1,
            command=lambda: self.handle_avatar_upload()
        )
        self.avatar_btn.pack(fill="x", pady=(2, 12))
        self.accent_widgets.append((self.avatar_btn, "border_button"))

        # Action Buttons
        self.save_char_btn = ctk.CTkButton(
            scroll_frame,
            text="Save Character Profile",
            command=lambda: self.handle_save_character()
        )
        self.save_char_btn.pack(fill="x", pady=5)
        self.accent_widgets.append((self.save_char_btn, "button"))

        self.launch_chat_btn = ctk.CTkButton(
            scroll_frame,
            text="✨ Launch New Chat Session",
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            command=lambda: self.handle_launch_session()
        )
        self.launch_chat_btn.pack(fill="x", pady=(15, 5))

    def setup_user_tab(self):
        """Constructs the user persona profile suite inside the left sidebar."""
        tab = self.config_tabs.tab("Users")

        scroll_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=2, pady=2)

        # Selection selector
        select_lbl = ctk.CTkLabel(scroll_frame, text="Active User Profile:", font=ctk.CTkFont(weight="bold"))
        select_lbl.pack(fill="x", pady=(5, 2), anchor="w")

        self.user_profile_dropdown = ctk.CTkOptionMenu(
            scroll_frame,
            values=["New User..."],
            command=lambda val: self.handle_user_dropdown_changed(val)
        )
        self.user_profile_dropdown.pack(fill="x", pady=(0, 15))
        self.accent_widgets.append((self.user_profile_dropdown, "optionmenu"))

        # Persona fields
        name_lbl = ctk.CTkLabel(scroll_frame, text="User Name:", font=ctk.CTkFont(size=11, weight="bold"), text_color="gray70")
        name_lbl.pack(fill="x", pady=(5, 2), anchor="w")
        self.user_name_field = ctk.CTkEntry(scroll_frame)
        self.user_name_field.pack(fill="x", pady=(0, 10))

        desc_lbl = ctk.CTkLabel(scroll_frame, text="User Persona / Notes:", font=ctk.CTkFont(size=11, weight="bold"), text_color="gray70")
        desc_lbl.pack(fill="x", pady=(5, 2), anchor="w")
        self.user_desc_field = ctk.CTkTextbox(scroll_frame, height=120, wrap="word", font=ctk.CTkFont(size=12))
        self.user_desc_field.pack(fill="x", pady=(0, 10))

        # Avatar path visualization
        self.user_avatar_path_lbl = ctk.CTkLabel(scroll_frame, text="Avatar: None", font=ctk.CTkFont(size=10, slant="italic"), text_color="gray50", anchor="w")
        self.user_avatar_path_lbl.pack(fill="x", pady=2)

        self.user_avatar_btn = ctk.CTkButton(
            scroll_frame,
            text="Upload User Picture",
            fg_color="transparent",
            border_width=1,
            command=lambda: self.handle_user_avatar_upload()
        )
        self.user_avatar_btn.pack(fill="x", pady=(2, 12))
        self.accent_widgets.append((self.user_avatar_btn, "border_button"))

        # Action Buttons
        self.save_user_btn = ctk.CTkButton(
            scroll_frame,
            text="Save User Profile",
            command=lambda: self.handle_save_user()
        )
        self.save_user_btn.pack(fill="x", pady=5)
        self.accent_widgets.append((self.save_user_btn, "button"))

    def setup_lorebook_tab(self):
        """Builds the active scrollable workspace database inside the left sidebar."""
        tab = self.config_tabs.tab("Lorebook")

        lbl = ctk.CTkLabel(tab, text="Dynamic Memory Book (RAG Cache):", font=ctk.CTkFont(weight="bold", size=12))
        lbl.pack(fill="x", pady=(5, 5), anchor="w")

        self.lore_editor = ctk.CTkTextbox(tab, font=ctk.CTkFont(family="Consolas", size=11), wrap="word")
        self.lore_editor.pack(fill="both", expand=True, pady=5)

    def setup_settings_tab(self):
        """Constructs API setup frame, theme controls, and toggles with advanced settings."""
        tab = self.config_tabs.tab("Settings")

        # Wrap everything in a scrollable frame so we can scale parameters infinitely
        settings_scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        settings_scroll.pack(fill="both", expand=True, padx=2, pady=2)

        # Skin Selectors
        theme_hdr = ctk.CTkLabel(settings_scroll, text="Workspace Skin Theme:", font=ctk.CTkFont(weight="bold"))
        theme_hdr.pack(fill="x", pady=(5, 2), anchor="w")

        self.palette_dropdown = ctk.CTkOptionMenu(
            settings_scroll,
            values=list(self.color_palettes.keys()),
            command=self.change_accent_palette
        )
        self.palette_dropdown.pack(fill="x", pady=(0, 10))
        self.accent_widgets.append((self.palette_dropdown, "optionmenu"))

        self.mode_dropdown = ctk.CTkOptionMenu(
            settings_scroll,
            values=["Dark", "Light"],
            command=self.change_appearance_mode
        )
        self.mode_dropdown.pack(fill="x", pady=(0, 15))
        self.accent_widgets.append((self.mode_dropdown, "optionmenu"))

        # OpenRouter Key Integration API
        api_hdr = ctk.CTkLabel(settings_scroll, text="OpenRouter Integration:", font=ctk.CTkFont(weight="bold"))
        api_hdr.pack(fill="x", pady=(10, 2), anchor="w")

        self.api_key_field = ctk.CTkEntry(settings_scroll)
        self.api_key_field.pack(fill="x", pady=(0, 5))
        self.api_key_field.bind("<FocusIn>", self.clear_api_warning)

        self.show_api_toggle = ctk.CTkCheckBox(settings_scroll, text="Reveal API Key", command=self.toggle_api_visibility)
        self.show_api_toggle.pack(pady=5, anchor="w")
        self.accent_widgets.append((self.show_api_toggle, "checkbox"))

        # --- ADVANCED NARRATIVE ENGINE PARAMETERS ---
        generation_hdr = ctk.CTkLabel(settings_scroll, text="Engine Parameters:", font=ctk.CTkFont(weight="bold", size=13))
        generation_hdr.pack(fill="x", pady=(15, 5), anchor="w")

        # Global System/System context Prompt
        prompt_hdr = ctk.CTkLabel(settings_scroll, text="Global Prompt (System Instructions):", font=ctk.CTkFont(size=11, weight="bold"), text_color="gray70")
        prompt_hdr.pack(fill="x", pady=(5, 2), anchor="w")

        self.global_prompt_box = ctk.CTkTextbox(settings_scroll, height=90, wrap="word", font=ctk.CTkFont(family="Consolas", size=11))
        self.global_prompt_box.pack(fill="x", pady=(0, 10))

        # Temperature parameter with live numeric readout label
        temp_frame = ctk.CTkFrame(settings_scroll, fg_color="transparent")
        temp_frame.pack(fill="x", pady=(5, 0))

        self.temp_lbl = ctk.CTkLabel(temp_frame, text="Temperature: 0.85", font=ctk.CTkFont(size=11, weight="bold"), text_color="gray70")
        self.temp_lbl.pack(side="left")

        self.temp_slider = ctk.CTkSlider(settings_scroll, from_=0, to=2, number_of_steps=40, command=self.update_temp_label)
        self.temp_slider.pack(fill="x", pady=(0, 12))
        self.accent_widgets.append((self.temp_slider, "switch"))

        # Max Generation Tokens
        max_tokens_hdr = ctk.CTkLabel(settings_scroll, text="Max Generation Output (Tokens):", font=ctk.CTkFont(size=11, weight="bold"), text_color="gray70")
        max_tokens_hdr.pack(fill="x", pady=(5, 2), anchor="w")
        self.max_tokens_field = ctk.CTkEntry(settings_scroll)
        self.max_tokens_field.pack(fill="x", pady=(0, 12))

        # Max Context Buffer Size
        context_hdr = ctk.CTkLabel(settings_scroll, text="Context Window Limit (Tokens):", font=ctk.CTkFont(size=11, weight="bold"), text_color="gray70")
        context_hdr.pack(fill="x", pady=(5, 2), anchor="w")
        self.context_field = ctk.CTkEntry(settings_scroll)
        self.context_field.pack(fill="x", pady=(0, 15))

        # --- AUTOMATION SWITCH HUB ---
        auto_hdr = ctk.CTkLabel(settings_scroll, text="AI Memory Automation:", font=ctk.CTkFont(weight="bold"))
        auto_hdr.pack(fill="x", pady=(15, 2), anchor="w")

        self.memory_extraction_switch = ctk.CTkSwitch(settings_scroll, text="Stage 2: Auto-Extract Keywords for Lorebook")
        self.memory_extraction_switch.pack(pady=5, anchor="w")
        self.accent_widgets.append((self.memory_extraction_switch, "switch"))

        # --- FONT SETTINGS ---
        font_hdr = ctk.CTkLabel(settings_scroll, text="Typography Settings:", font=ctk.CTkFont(weight="bold"))
        font_hdr.pack(fill="x", pady=(15, 2), anchor="w")

        font_size_lbl = ctk.CTkLabel(settings_scroll, text="Chat Font Size:", font=ctk.CTkFont(size=11, weight="bold"), text_color="gray70")
        font_size_lbl.pack(fill="x", pady=(5, 2), anchor="w")

        self.font_size_dropdown = ctk.CTkOptionMenu(
            settings_scroll,
            values=["12", "13", "14", "16", "18", "20", "22", "24"],
            command=self.on_font_size_dropdown_changed
        )
        self.font_size_dropdown.pack(fill="x", pady=(0, 15))
        self.accent_widgets.append((self.font_size_dropdown, "optionmenu"))

        # --- MAINTENANCE HUB ---
        maint_hdr = ctk.CTkLabel(settings_scroll, text="Maintenance Tools:", font=ctk.CTkFont(weight="bold", size=13), text_color="#d9534f")
        maint_hdr.pack(fill="x", pady=(20, 5), anchor="w")

        # Updated with dynamic lambda lookup
        self.wipe_history_btn = ctk.CTkButton(
            settings_scroll,
            text="Wipe All History & Logs",
            fg_color="#8b1e1e",
            hover_color="#5a1212",
            command=lambda: self.trigger_wipe_maintenance()
        )
        self.wipe_history_btn.pack(fill="x", pady=(5, 10))

    def update_temp_label(self, value):
        """Dynamic slider callback to visually output temperature increments."""
        self.temp_lbl.configure(text=f"Temperature: {float(value):.2f}")

    def create_center_chat(self):
        """Constructs the primary chat workspace panel."""
        self.chat_pane = ctk.CTkFrame(self, fg_color="transparent")
        self.chat_pane.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.chat_pane.grid_rowconfigure(0, weight=0)  # Header
        self.chat_pane.grid_rowconfigure(1, weight=1)  # Log
        self.chat_pane.grid_rowconfigure(2, weight=0)  # Inputs
        self.chat_pane.grid_columnconfigure(0, weight=1)

        # Control Header Bar (Collapsible sidebar triggers & art toggles)
        self.header_bar = ctk.CTkFrame(self.chat_pane, height=45, corner_radius=8)
        self.header_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.header_bar.pack_propagate(False)

        # Sidebar Collapse Toggle
        self.sidebar_toggle_btn = ctk.CTkButton(
            self.header_bar,
            text="◀ Config",
            width=80,
            height=30,
            command=self.toggle_sidebar
        )
        self.sidebar_toggle_btn.pack(side="left", padx=8, pady=7)
        self.accent_widgets.append((self.sidebar_toggle_btn, "button"))

        self.active_user_lbl = ctk.CTkLabel(
            self.header_bar,
            text="Active User:",
            font=ctk.CTkFont(weight="bold")
        )
        self.active_user_lbl.pack(side="left", padx=(4, 6), pady=7)

        self.active_user_dropdown = ctk.CTkOptionMenu(
            self.header_bar,
            values=["New User..."],
            width=170,
            command=lambda val: self.handle_user_dropdown_changed(val)
        )
        self.active_user_dropdown.pack(side="left", padx=(0, 12), pady=7)
        self.accent_widgets.append((self.active_user_dropdown, "optionmenu"))

        # Scene Art Toggle Button
        self.art_toggle_btn = ctk.CTkButton(
            self.header_bar,
            text="Art Canvas",
            width=100,
            height=30,
            command=self.toggle_art_panel
        )
        self.art_toggle_btn.pack(side="right", padx=8, pady=7)
        self.accent_widgets.append((self.art_toggle_btn, "button"))

        # Chat Log Box
        self.chat_log = ctk.CTkTextbox(self.chat_pane, font=ctk.CTkFont(size=14), wrap="word")
        self.chat_log.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        self.chat_log.configure(state="disabled")
        self.chat_menu_buttons = []
        self.chat_log._textbox.bind("<Configure>", self._configure_header_tab)

        # Configure initial visual tags (these will be scaled dynamically)
        self.chat_log.tag_config("user_tag", foreground="#8fbbf0", font=ctk.CTkFont(weight="bold"))
        self.chat_log.tag_config("bot_tag", foreground="#cfa9f0", font=ctk.CTkFont(weight="bold"))
        
        # Base Environment Colors/Styles
        self.chat_log.tag_config("system_tag", foreground="#8fcba0", font=ctk.CTkFont(slant="italic"))
        self.chat_log.tag_config("message_separator", foreground="#555a60")
        self.chat_log.tag_config("rp_system_content", foreground="#a0aab0") # Explicitly controlled system content color
        self.chat_log.tag_config("rp_narrative", foreground="#92979d")       # Action/Description base color
        self.chat_log.tag_config("rp_dialogue", foreground="#d9dde3")        # Spoken text base color

        # Overlapping Modifier Styles (Only modify font attributes, leaving colors intact!)
        self.chat_log.tag_config("rp_bold", font=ctk.CTkFont(weight="bold"))
        self.chat_log.tag_config("rp_thought", font=ctk.CTkFont(slant="italic"))

        # Message Input Panel
        self.input_row = ctk.CTkFrame(self.chat_pane, fg_color="transparent")
        self.input_row.grid(row=2, column=0, sticky="ew")
        self.input_row.grid_columnconfigure(0, weight=1)

        self.input_field = ctk.CTkTextbox(self.input_row, height=80, wrap="word", font=ctk.CTkFont(size=14))
        self.input_field.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.input_field.bind("<Control-Return>", lambda event: self.handle_chat_sent())

        # Updated with dynamic lambda lookup
        self.send_btn = ctk.CTkButton(self.input_row, text="Send Turn\n(Ctrl+Enter)", command=lambda: self.handle_chat_sent(), width=100)
        self.send_btn.grid(row=0, column=1, sticky="nsew")
        self.accent_widgets.append((self.send_btn, "button"))

    def create_right_art_panel(self):
        """Constructs the collapsible panel on the right designed to house scene imagery placeholders."""
        self.art_container = ctk.CTkFrame(self, corner_radius=0, width=290)
        self.art_container.grid(row=0, column=2, sticky="nsew", padx=0, pady=0)
        self.art_container.grid_propagate(False)

        # Header Title
        self.art_hdr = ctk.CTkLabel(
            self.art_container,
            text="Active Scene Illustration",
            font=ctk.CTkFont(weight="bold", size=14)
        )
        self.art_hdr.pack(pady=(20, 10))

        # Divider
        self.art_divider = ctk.CTkFrame(self.art_container, height=2, fg_color="gray30")
        self.art_divider.pack(fill="x", padx=15, pady=(0, 15))

        # Canvas/Mock Image box frame
        self.art_canvas = ctk.CTkFrame(self.art_container, fg_color="gray20", border_width=2, border_color="gray40")
        self.art_canvas.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Mock graphic indicator
        self.canvas_label = ctk.CTkLabel(
            self.art_canvas,
            text="[ SCENE ART CANVAS ]\n\n(Future local SD / DALL-E\nImage Pipeline Viewport)",
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color="gray50"
        )
        self.canvas_label.pack(expand=True)

        # Updated with dynamic lambda lookup
        self.generate_btn = ctk.CTkButton(self.art_container, text="Regenerate Illustration", fg_color="transparent", border_width=1, command=lambda: self.mock_image_generation())
        self.generate_btn.pack(fill="x", padx=15, pady=(0, 20))
        self.accent_widgets.append((self.generate_btn, "border_button"))

    def toggle_sidebar(self):
        """Collapses or rolls out the left dashboard configuration frame."""
        if self.sidebar_visible:
            self.sidebar_container.grid_forget()
            self.grid_columnconfigure(0, minsize=0, weight=0)
            self.sidebar_toggle_btn.configure(text="Config ▶")
            self.sidebar_visible = False
        else:
            self.sidebar_container.grid(row=0, column=0, sticky="nsew")
            self.grid_columnconfigure(0, minsize=330, weight=0)
            self.sidebar_toggle_btn.configure(text="◀ Config")
            self.sidebar_visible = True

    def toggle_art_panel(self):
        """Collapses or rolls out the right Scene Art viewport."""
        if self.art_panel_visible:
            self.art_container.grid_forget()
            self.grid_columnconfigure(2, minsize=0, weight=0)
            self.art_toggle_btn.configure(text="Art Canvas [Off]")
            self.art_panel_visible = False
        else:
            self.art_container.grid(row=0, column=2, sticky="nsew")
            self.grid_columnconfigure(2, minsize=290, weight=0)
            self.art_toggle_btn.configure(text="Art Canvas")
            self.art_panel_visible = True

    def change_accent_palette(self, selected_palette):
        """Updates elements matching selected color palettes across active widgets."""
        self.current_palette = selected_palette
        colors = self.color_palettes[selected_palette]

        mode = ctk.get_appearance_mode()
        if mode == "Light":
            unselected_tab = "#d9dbdf"
            unselected_hover = "#c7ccd2"
            tab_fg = "#cfd3d8"
            tab_text = "#2a2f36"
        else:
            unselected_tab = "#2a3139"
            unselected_hover = "#343d47"
            tab_fg = "#232930"
            tab_text = "#d9dde3"

        # Keep selected tab styling aligned with the current app palette.
        try:
            self.config_tabs.configure(
                segmented_button_fg_color=tab_fg,
                segmented_button_selected_color=colors["accent"],
                segmented_button_selected_hover_color=colors["hover"],
                segmented_button_unselected_color=unselected_tab,
                segmented_button_unselected_hover_color=unselected_hover,
                text_color=tab_text
            )
        except Exception:
            pass

        for widget, widget_type in self.accent_widgets:
            try:
                if widget_type == "button":
                    widget.configure(fg_color=colors["accent"], hover_color=colors["hover"])
                elif widget_type == "border_button":
                    widget.configure(border_color=colors["accent"], text_color=colors["accent"])
                elif widget_type == "optionmenu":
                    widget.configure(fg_color=colors["accent"], button_color=colors["accent"], button_hover_color=colors["hover"])
                elif widget_type == "switch":
                    widget.configure(progress_color=colors["accent"])
                elif widget_type == "checkbox":
                    widget.configure(fg_color=colors["accent"])
            except Exception:
                pass

    def change_appearance_mode(self, new_mode):
        """Changes the UI color mode."""
        ctk.set_appearance_mode(new_mode)
        # Refresh mode-aware palette values such as tab backgrounds and text contrast.
        self.change_accent_palette(self.current_palette)

    def clear_api_warning(self, event):
        """Automatically wipes the default warning when you click the input field to paste a key."""
        if self.api_key_field.get() == "No API key file found, please insert your own.":
            self.api_key_field.delete(0, tk.END)
            self.api_key_field.configure(show="*")

    def toggle_api_visibility(self):
        """Toggles OpenRouter secret key input character masking."""
        if self.api_key_field.cget("show") == "*":
            self.api_key_field.configure(show="")
        else:
            self.api_key_field.configure(show="*")

    def append_system_msg(self, text):
        """Inserts system feedback cleanly."""
        self.chat_log.configure(state="normal")
        self.chat_log.insert(tk.END, f"\n⚙ [System Info]\n", "system_tag")
        self.chat_log.insert(tk.END, f"{text}\n")
        self.chat_log.configure(state="disabled")
        self.chat_log.see(tk.END)

    def _configure_header_tab(self, _event=None):
        """Place embedded ellipsis controls at the right edge of message headers."""
        width = self.chat_log._textbox.winfo_width()
        self.chat_log._textbox.configure(tabs=(max(160, width - 44),))

    def clear_chat_message_controls(self):
        """Destroy embedded buttons before clearing or rebuilding the Text timeline."""
        for button in self.chat_menu_buttons:
            button.destroy()
        self.chat_menu_buttons = []

    def append_message_header(self, title, tag, role, turn_index):
        """Add a compact header with a minimal ellipsis menu trigger."""
        self._configure_header_tab()
        self.chat_log.insert(tk.END, f"\n{title}", tag)
        self.chat_log.insert(tk.END, "\t")
        menu_button = ctk.CTkButton(
            self.chat_log._textbox,
            text="•••",
            width=26,
            height=20,
            corner_radius=10,
            fg_color="transparent",
            hover_color="#4b5056",
            text_color="#969ba1",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda current_role=role, index=turn_index: self.open_message_context_menu(
                menu_button, current_role, index
            ),
        )
        self.chat_log._textbox.window_create(tk.END, window=menu_button, align="center")
        self.chat_menu_buttons.append(menu_button)
        self.chat_log.insert(tk.END, "\n")

    def append_message_separator(self):
        """Visually separate messages without replacing the text timeline with cards."""
        self.chat_log.insert(tk.END, "─" * 96 + "\n", "message_separator")

    def open_message_context_menu(self, button, role, turn_index):
        """Show the role-specific actions beside the selected ellipsis button."""
        menu = tk.Menu(
            self, tearoff=False, background="#34383d", foreground="#d9dde3",
            activebackground="#4b5056", activeforeground="#ffffff", borderwidth=0,
            font=("Segoe UI", 10),
        )
        if role == "assistant":
            menu.add_command(label="Reroll", command=lambda: self.handle_reroll_message(turn_index))
            menu.add_separator()
            menu.add_command(label="Previous version", command=lambda: self.handle_cycle_reroll(turn_index, -1))
            menu.add_command(label="Next version", command=lambda: self.handle_cycle_reroll(turn_index, 1))
        elif role == "user":
            menu.add_command(label="Delete this message and later", command=lambda: self.handle_delete_from_message(turn_index))
        else:
            return
        try:
            menu.tk_popup(button.winfo_rootx(), button.winfo_rooty() + button.winfo_height())
        finally:
            menu.grab_release()

    def load_settings_into_ui(self, settings: dict):
        """Safely populates UI forms with settings loaded by main.py controllers."""
        self.palette_dropdown.set(settings.get("theme", "Muted Denim"))
        self.change_accent_palette(settings.get("theme", "Muted Denim"))
        self.mode_dropdown.set(settings.get("theme_mode", "Dark"))
        self.change_appearance_mode(settings.get("theme_mode", "Dark"))

        # API Key
        key = settings.get("api_key", "").strip()
        self.api_key_field.delete(0, tk.END)
        if key:
            self.api_key_field.configure(show="*")
            self.api_key_field.insert(0, key)
        else:
            self.api_key_field.configure(show="")
            self.api_key_field.insert(0, "No API key file found, please insert your own.")

        # Engine Params
        self.model_dropdown.set(settings.get("model", "deepseek/deepseek-chat"))

        self.global_prompt_box.delete("1.0", tk.END)
        self.global_prompt_box.insert("1.0", settings.get("system_prompt", ""))

        self.temp_slider.set(settings.get("temperature", 0.85))
        self.update_temp_label(settings.get("temperature", 0.85))

        self.max_tokens_field.delete(0, tk.END)
        self.max_tokens_field.insert(0, str(settings.get("max_tokens", 1024)))

        self.context_field.delete(0, tk.END)
        self.context_field.insert(0, str(settings.get("context_size", 8000)))

        # Automation (Cleaned of auto-summarize and auto-vectorize)
        if settings.get("memory_extraction_enabled", False):
            self.memory_extraction_switch.select()
        else:
            self.memory_extraction_switch.deselect()

        # Dynamic Font Initialization
        font_sz = settings.get("font_size", 14)
        self.font_size_dropdown.set(str(font_sz))
        self.update_chat_fonts(font_sz)

    def get_current_ui_settings(self) -> dict:
        api_key_raw = self.api_key_field.get().strip()
        if api_key_raw == "No API key file found, please insert your own.":
            api_key_raw = ""

        try:
            temp_val = float(self.temp_slider.get())
        except ValueError:
            temp_val = 0.85

        try:
            max_t = int(self.max_tokens_field.get().strip())
        except ValueError:
            max_t = 1024

        try:
            ctx_s = int(self.context_field.get().strip())
        except ValueError:
            ctx_s = 8000

        try:
            font_sz = int(self.font_size_dropdown.get())
        except ValueError:
            font_sz = 14

        return {
            "theme": self.palette_dropdown.get(),
            "theme_mode": self.mode_dropdown.get(),
            "api_key": api_key_raw,
            "model": self.model_dropdown.get(),
            "system_prompt": self.global_prompt_box.get("1.0", tk.END).strip(),
            "temperature": temp_val,
            "max_tokens": max_t,
            "context_size": ctx_s,
            "memory_extraction_enabled": bool(self.memory_extraction_switch.get()),
            "font_size": font_sz
        }
    
    def update_chat_fonts(self, size: int):
        """Updates the font size of the chat textbox, input text field, and styled tags dynamically."""
        font_family = "Segoe UI"
        self.chat_log.configure(font=ctk.CTkFont(family=font_family, size=size))
        self.input_field.configure(font=ctk.CTkFont(family=font_family, size=size))
        
        self.chat_log.tag_config("user_tag", font=ctk.CTkFont(family=font_family, size=size, weight="bold"))
        self.chat_log.tag_config("bot_tag", font=ctk.CTkFont(family=font_family, size=size, weight="bold"))
        self.chat_log.tag_config("system_tag", font=ctk.CTkFont(family=font_family, size=size, slant="italic"))
        self.chat_log.tag_config("rp_system_content", font=ctk.CTkFont(family=font_family, size=size))
        self.chat_log.tag_config("rp_narrative", font=ctk.CTkFont(family=font_family, size=size))
        self.chat_log.tag_config("rp_dialogue", font=ctk.CTkFont(family=font_family, size=size))
        self.chat_log.tag_config("rp_bold", font=ctk.CTkFont(family=font_family, size=size, weight="bold"))
        self.chat_log.tag_config("rp_thought", font=ctk.CTkFont(family=font_family, size=size, slant="italic"))

    def on_font_size_dropdown_changed(self, value: str):
        """Callback to trigger dynamic updates immediately when changed in settings."""
        try:
            self.update_chat_fonts(int(value))
        except ValueError:
            pass

    def append_roleplay_text(self, text: str, base_env_tag: str = "rp_narrative"):
        """
        Parses roleplay strings hierarchically to allow nested styles.
        Example: "*Karl...* text" inside spoken words keeps the dialogue color but becomes bold.
        """
        import re

        # --- TYPOGRAPHY SANITIZATION ---
        # Replace long em-dashes (—) and en-dashes (–) with a clean spaced hyphen
        text = text.replace("—", " - ").replace("–", " - ")
        # Optional: Collapse any accidental double spaces created by the replacement
        text = re.sub(r' +', ' ', text)

        # Split text into segments of spoken dialogue ("...") and outside narration
        # Using capturing parenthesis so the split tokens are preserved in the list
        segments = re.split(r'(\"[^\"]+\")', text)

        for seg in segments:
            if not seg:
                continue

            # Determine baseline environment tag for this chunk
            if seg.startswith('"') and seg.endswith('"'):
                current_env = "rp_dialogue"
            else:
                current_env = base_env_tag

            # Now parse inline formatting modifiers (*bold* and 'thoughts') within this environment
            # Inline pattern captures bold blocks or single quote blocks (avoiding word contractions)
            inline_pattern = re.compile(r'(\*[^*]+\*)|((?<!\w)\'.+?\'(?!\w))')
            
            last_idx = 0
            for match in inline_pattern.finditer(seg):
                start, end = match.span()

                # Text before the modifier inherits the base environment behavior
                if start > last_idx:
                    self.chat_log.insert(tk.END, seg[last_idx:start], current_env)

                bold_chunk, thought_chunk = match.groups()
                if bold_chunk:
                    # Strip asterisks; combine base color with bold modifier tags
                    clean_text = bold_chunk[1:-1]
                    self.chat_log.insert(tk.END, clean_text, (current_env, "rp_bold"))
                elif thought_chunk:
                    # Keep single quotes; combine base color with thought style tags
                    self.chat_log.insert(tk.END, thought_chunk, (current_env, "rp_thought"))

                last_idx = end

                # Append any remaining text left over in this segment
            if last_idx < len(seg):
                self.chat_log.insert(tk.END, seg[last_idx:], current_env)

        self.chat_log.insert(tk.END, "\n")

    # --- STUB OVERRIDES (TO BE ASSIGNED BY MAIN.PY ORCHESTRATORS) ---
    def handle_chat_sent(self):
        pass

    def handle_reroll_message(self, turn_index):
        pass

    def handle_cycle_reroll(self, turn_index, direction):
        pass

    def handle_delete_from_message(self, turn_index):
        pass

    def simulate_manual_summary(self):
        pass

    def simulated_scan(self):
        pass

    def mock_image_generation(self):
        pass

    def trigger_wipe_maintenance(self):
        pass

    # NEW BINDING HOOKS
    def handle_character_dropdown_changed(self):
        pass

    def handle_avatar_upload(self):
        pass

    def handle_save_character(self):
        pass

    def handle_user_dropdown_changed(self, value=None):
        pass

    def handle_user_avatar_upload(self):
        pass

    def handle_save_user(self):
        pass

    def handle_launch_session(self):
        pass

    def handle_session_changed(self):
        pass
