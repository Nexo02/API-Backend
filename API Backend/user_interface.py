# -*- coding: utf-8 -*-
"""
LoreEngine v1.1 - User Interface Layout
Houses visual widgets, collapsible sidebars, and customizable theme hooks.
"""

import os
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageOps


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
        self.avatar_image_cache = {}
        self.current_chat_font_size = 16
        self.show_avatars = True

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
            values=["deepseek/deepseek-chat", "deepseek/deepseek-v4-flash", "deepseek/deepseek-v3.2"]
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

        # Trigger Actions
        self.view_lore_btn = ctk.CTkButton(tab, text="Scan Vector Index", command=lambda: self.simulated_scan())
        self.view_lore_btn.pack(fill="x", pady=(25, 8))
        self.accent_widgets.append((self.view_lore_btn, "button"))

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

        self.memory_extraction_switch = ctk.CTkSwitch(settings_scroll,
                                                      text="Stage 2: Auto-Extract Keywords for Lorebook")
        self.memory_extraction_switch.pack(pady=5, anchor="w")
        self.accent_widgets.append((self.memory_extraction_switch, "switch"))

        # Profile Picture Toggle
        self.show_avatars_switch = ctk.CTkSwitch(settings_scroll, text="Show Character & User Profile Pictures")
        self.show_avatars_switch.pack(pady=5, anchor="w")
        self.accent_widgets.append((self.show_avatars_switch, "switch"))

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

        self.wipe_history_btn = ctk.CTkButton(
            settings_scroll,
            text="Wipe All History & Logs",
            fg_color="#8b1e1e",
            hover_color="#5a1212",
            command=lambda: self.trigger_wipe_maintenance()
        )
        self.wipe_history_btn.pack(fill="x", pady=(5, 10))

        self.save_settings_btn = ctk.CTkButton(
            settings_scroll,
            text="Save Settings",
            command=lambda: self.handle_save_settings()
        )
        self.save_settings_btn.pack(fill="x", pady=(10, 20))
        self.accent_widgets.append((self.save_settings_btn, "button"))

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
            text=" ◀ ",
            width=40,
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
        self.chat_message_rows = []
        self.current_message_body_widget = None
        self.current_chat_message_scroll_index = 0
        self.chat_rendering_batch = False
        self.last_chat_log_width = 0
        self.chat_log._textbox.bind("<Configure>", self._configure_header_tab)
        self.chat_log._textbox.bind("<MouseWheel>", self._on_chat_mousewheel)
        self.chat_log._textbox.bind("<Button-4>", self._on_chat_mousewheel)
        self.chat_log._textbox.bind("<Button-5>", self._on_chat_mousewheel)

        # Configure initial visual tags (these will be scaled dynamically)
        self.chat_log.tag_config("user_tag", foreground="#8fbbf0", font=ctk.CTkFont(weight="bold"))
        self.chat_log.tag_config("bot_tag", foreground="#cfa9f0", font=ctk.CTkFont(weight="bold"))

        # Base Environment Colors/Styles
        self.chat_log.tag_config("system_tag", foreground="#8fcba0", font=ctk.CTkFont(slant="italic"))
        self.chat_log.tag_config("message_separator", foreground="#555a60")
        self.chat_log.tag_config("rp_system_content", foreground="#a0aab0")
        self.chat_log.tag_config("rp_narrative", foreground="#92979d")
        self.chat_log.tag_config("rp_dialogue", foreground="#d9dde3")

        # Overlapping Modifier Styles
        self.chat_log.tag_config("rp_bold", font=ctk.CTkFont(weight="bold"))
        self.chat_log.tag_config("rp_thought", font=ctk.CTkFont(slant="italic"))

        # Message Input Panel
        self.input_row = ctk.CTkFrame(self.chat_pane, fg_color="transparent")
        self.input_row.grid(row=2, column=0, sticky="ew")
        self.input_row.grid_columnconfigure(0, weight=1)

        self.input_min_height = 80
        self.input_max_height = 220
        self.input_resize_job = None
        self.input_field = ctk.CTkTextbox(self.input_row, height=self.input_min_height, wrap="word", font=ctk.CTkFont(size=14))
        self.input_field.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.input_field._textbox.bind("<Return>", self.handle_input_return)
        self.input_field._textbox.bind("<Shift-Return>", self.handle_input_shift_return)
        self.input_field._textbox.bind("<Up>", self.handle_input_up_arrow)  # Up-key shortcut handler
        self.input_field._textbox.bind("<Control-BackSpace>", self.delete_previous_input_word)
        self.input_field._textbox.bind("<KeyRelease>", self.schedule_input_autogrow)
        self.input_field._textbox.bind("<Configure>", self.schedule_input_autogrow)

        self.send_btn = ctk.CTkButton(self.input_row, text="Send Turn", command=lambda: self.handle_chat_sent(), width=100)
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

        self.generate_btn = ctk.CTkButton(self.art_container, text="Regenerate Illustration", fg_color="transparent", border_width=1, command=lambda: self.mock_image_generation())
        self.generate_btn.pack(fill="x", padx=15, pady=(0, 20))
        self.accent_widgets.append((self.generate_btn, "border_button"))

    def toggle_sidebar(self):
        """Collapses or rolls out the left dashboard configuration frame."""
        if self.sidebar_visible:
            self.sidebar_container.grid_forget()
            self.grid_columnconfigure(0, minsize=0, weight=0)
            self.sidebar_toggle_btn.configure(text=" ▶ ")
            self.sidebar_visible = False
        else:
            self.sidebar_container.grid(row=0, column=0, sticky="nsew")
            self.grid_columnconfigure(0, minsize=330, weight=0)
            self.sidebar_toggle_btn.configure(text=" ◀ ")
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
        self.change_accent_palette(self.current_palette)
        self.refresh_message_body_appearance()

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

    def handle_input_return(self, _event=None):
        """Submit on Enter without leaving an extra newline in the input."""
        self.handle_chat_sent()
        return "break"

    def handle_input_shift_return(self, _event=None):
        """Insert a newline when composing multi-line messages."""
        self.input_field._textbox.insert(tk.INSERT, "\n")
        self.schedule_input_autogrow()
        return "break"

    def handle_input_up_arrow(self, _event=None):
        """Pressing Up in an empty input field triggers editing the last user message."""
        current_text = self.input_field.get("1.0", tk.END).strip()
        if not current_text:
            self.handle_edit_last_user_message()
            return "break"
        return None

    def handle_edit_last_user_message(self):
        """Locate the last user turn and fire the edit handler."""
        user_rows = [r for r in self.chat_message_rows if r.get("role") == "user"]
        if user_rows:
            last_user_turn = user_rows[-1]["turn_index"]
            self.handle_edit_message(last_user_turn)

    def delete_previous_input_word(self, _event=None):
        """Delete the word immediately before the cursor."""
        import re

        text_widget = self.input_field._textbox
        before_cursor = text_widget.get("1.0", tk.INSERT)
        match = re.search(r'\s*\S+\s*$', before_cursor)
        if match:
            delete_count = len(match.group(0))
            text_widget.delete(f"insert-{delete_count}c", tk.INSERT)
            self.schedule_input_autogrow()
        return "break"

    def schedule_input_autogrow(self, _event=None):
        """Debounce input height recalculation while typing."""
        if self.input_resize_job is not None:
            try:
                self.after_cancel(self.input_resize_job)
            except Exception:
                pass
        self.input_resize_job = self.after_idle(self.autogrow_input_field)

    def autogrow_input_field(self):
        """Grow the input box with wrapped text lines within fixed min/max bounds."""
        self.input_resize_job = None
        try:
            self.input_field._textbox.update_idletasks()
            display_lines = self.input_field._textbox.count("1.0", "end-1c", "displaylines")[0] or 1
            line_height = max(18, int(self.current_chat_font_size * 1.45))
            target_height = int(display_lines * line_height) + 24
            target_height = max(self.input_min_height, min(self.input_max_height, target_height))
            if int(self.input_field.cget("height")) != target_height:
                self.input_field.configure(height=target_height)
        except Exception:
            pass

    def append_system_msg(self, text):
        """Inserts system feedback cleanly."""
        self.chat_log.configure(state="normal")
        self.chat_log.insert(tk.END, f"\n⚙ [System Info]\n", "system_tag")
        self.chat_log.insert(tk.END, f"{text}\n")
        self.chat_log.configure(state="disabled")
        self.chat_log.see(tk.END)

    def _configure_header_tab(self, _event=None):
        """Keep embedded message rows aligned to the current chat viewport width."""
        width = self.chat_log._textbox.winfo_width()
        if width == self.last_chat_log_width:
            return
        self.last_chat_log_width = width
        self.chat_log._textbox.configure(tabs=(max(160, width - 64),))
        usable_width = max(260, width - 26)
        indent_offset = 12

        for row_data in getattr(self, "chat_message_rows", []):
            try:
                row_data["row"].configure(width=usable_width)
                if row_data["avatar_width"] > 0:
                    right_width = max(160, usable_width - row_data["avatar_width"] - 24)
                else:
                    right_width = max(160, usable_width - indent_offset)
                row_data["right_column"].configure(width=right_width)
                row_data["body"].configure(width=max(160, right_width))
            except Exception:
                pass

    def begin_chat_render(self):
        """Start a bulk chat render without repeated full layout recalculation."""
        self.chat_rendering_batch = True

    def finish_chat_render(self):
        """Finish a bulk chat render and do one final layout pass."""
        self.chat_rendering_batch = False
        self.last_chat_log_width = 0  # Force width update
        self.chat_log._textbox.update_idletasks()
        self._configure_header_tab()

    def _bind_chat_wheel_redirect(self, widget):
        """Make embedded message widgets delegate wheel movement to the outer chat log."""
        widget.bind("<MouseWheel>", self._on_chat_mousewheel)
        widget.bind("<Button-4>", self._on_chat_mousewheel)
        widget.bind("<Button-5>", self._on_chat_mousewheel)

    def _on_chat_mousewheel(self, event):
        """Route wheel movement from embedded message widgets to the outer chat log with smooth pixel scrolling."""
        if getattr(event, "num", None) == 4:
            pixel_delta = -40
        elif getattr(event, "num", None) == 5:
            pixel_delta = 40
        else:
            delta = getattr(event, "delta", 0)
            if abs(delta) >= 120:
                pixel_delta = -int(delta / 120) * 40
            else:
                pixel_delta = -int(delta)

        if pixel_delta != 0:
            self.chat_log._textbox.yview_scroll(pixel_delta, "pixels")
        return "break"

    def clear_chat_message_controls(self):
        """Destroy embedded controls before clearing or rebuilding the Text timeline."""
        self.chat_log.configure(state="normal")
        self.chat_log.delete("1.0", tk.END)

        for button in self.chat_menu_buttons:
            try:
                button.destroy()
            except Exception:
                pass

        self.chat_menu_buttons = []
        self.chat_message_rows = []
        self.last_chat_log_width = 0
        self.current_message_body_tag = None
        self.current_message_body_widget = None
        self.current_chat_message_scroll_index = 0
        self.chat_log.configure(state="disabled")

    def _chat_text_colors(self):
        """Return mode-aware colors for embedded message body text widgets."""
        try:
            chat_background = self.chat_log._textbox.cget("background")
        except Exception:
            chat_background = "#f2f4f7" if ctk.get_appearance_mode() == "Light" else "#1f2328"

        if ctk.get_appearance_mode() == "Light":
            return {
                "background": chat_background,
                "narrative": "#3f4852",
                "dialogue": "#1f252b",
                "system": "#4f5963",
            }

        return {
            "background": chat_background,
            "narrative": "#92979d",
            "dialogue": "#d9dde3",
            "system": "#a0aab0",
        }

    def refresh_message_body_appearance(self):
        """Keep embedded message bodies aligned with current font and chat background."""
        colors = self._chat_text_colors()
        for row_data in getattr(self, "chat_message_rows", []):
            try:
                row_data["body"].configure(
                    bg=colors["background"],
                    fg=colors["narrative"],
                    font=("Segoe UI", self.current_chat_font_size)
                )
            except Exception:
                pass

    def get_avatar_image(self, avatar_path: str, size: int = 128):
        """Load and cache a portrait image with fixed width and ratio-preserved flexible height."""
        if not avatar_path or avatar_path == "None" or not os.path.exists(avatar_path):
            return None

        cache_key = (avatar_path, size)
        if cache_key in self.avatar_image_cache:
            return self.avatar_image_cache[cache_key]

        try:
            image = Image.open(avatar_path).convert("RGBA")
            original_width, original_height = image.size

            if original_width <= 0 or original_height <= 0:
                return None

            target_width = size
            target_height = max(1, int(original_height * (target_width / original_width)))

            image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)

            avatar_image = ctk.CTkImage(
                light_image=image,
                dark_image=image,
                size=(target_width, target_height)
            )
            self.avatar_image_cache[cache_key] = avatar_image
            return avatar_image
        except Exception as error:
            print(f"Error loading avatar image '{avatar_path}': {error}")
            return None

    def append_message_header(self, title, tag, role, turn_index, avatar_path: str = ""):
        """Add a grid-based message row: portrait left (if enabled), header and body right."""
        self.chat_log.configure(state="normal")
        if not self.chat_rendering_batch:
            self._configure_header_tab()

        show_avatar = self.show_avatars and role in ("user", "<user>", "assistant")
        avatar_image = self.get_avatar_image(avatar_path) if show_avatar else None

        usable_width = max(260, self.chat_log._textbox.winfo_width() - 26)
        indent_offset = 12  # Matches system message left margin when avatars are disabled

        row_frame = ctk.CTkFrame(self.chat_log._textbox, fg_color="transparent")

        if avatar_image:
            row_frame.grid_columnconfigure(0, weight=0)
            row_frame.grid_columnconfigure(1, weight=1)

            avatar_width, avatar_height = avatar_image.cget("size")
            image_column = ctk.CTkFrame(row_frame, fg_color="transparent", width=avatar_width + 12)
            image_column.grid(row=0, column=0, sticky="nw", padx=(0, 12), pady=0)
            image_column.grid_propagate(False)

            avatar_label = ctk.CTkLabel(
                image_column,
                image=avatar_image,
                text="",
                width=avatar_width,
                height=avatar_height
            )
            image_column.configure(width=avatar_width + 12, height=avatar_height)
            avatar_label.grid(row=0, column=0, sticky="nw")
            self.chat_menu_buttons.append(avatar_label)

            right_width = max(160, usable_width - avatar_width - 24)
            right_column = ctk.CTkFrame(row_frame, fg_color="transparent", width=right_width)
            right_column.grid(row=0, column=1, sticky="new")
            right_column.grid_columnconfigure(0, weight=1)
        else:
            avatar_width = 0
            row_frame.grid_columnconfigure(0, weight=1)

            # Apply small left indent to align with system messages
            right_width = max(160, usable_width - indent_offset)
            right_column = ctk.CTkFrame(row_frame, fg_color="transparent", width=right_width)
            right_column.grid(row=0, column=0, sticky="ew", padx=(indent_offset, 0))
            right_column.grid_columnconfigure(0, weight=1)

        header_frame = ctk.CTkFrame(right_column, fg_color="transparent", height=26)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 3))
        header_frame.grid_columnconfigure(0, weight=1)

        header_label = ctk.CTkLabel(
            header_frame,
            text=title,
            anchor="w",
            font=ctk.CTkFont(family="Segoe UI", size=self.current_chat_font_size, weight="bold")
        )
        if tag == "user_tag":
            header_label.configure(text_color="#8fbbf0")
        elif tag == "bot_tag":
            header_label.configure(text_color="#cfa9f0")
        elif tag == "system_tag":
            header_label.configure(text_color="#8fcba0")
        header_label.grid(row=0, column=0, sticky="ew")

        menu_button = ctk.CTkButton(
            header_frame,
            text="...",
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
        menu_button.grid(row=0, column=1, sticky="e", padx=(8, 0))
        self.chat_menu_buttons.append(menu_button)

        colors = self._chat_text_colors()
        body_widget = tk.Message(
            right_column,
            text="",
            width=max(160, right_width),
            bd=0,
            highlightthickness=0,
            padx=0,
            pady=0,
            bg=colors["background"],
            fg=colors["narrative"],
            font=("Segoe UI", self.current_chat_font_size),
            anchor="nw",
            justify="left",
            aspect=1000,
        )
        body_widget.grid(row=1, column=0, sticky="ew")

        widgets_to_bind = [row_frame, right_column, header_frame, header_label, menu_button, body_widget]
        if avatar_image:
            widgets_to_bind.extend([image_column, avatar_label])

        for widget in widgets_to_bind:
            self._bind_chat_wheel_redirect(widget)

        window_index = self.chat_log.index("end-1c")
        self.chat_log._textbox.window_create(window_index, window=row_frame, align="top", pady=6)
        row_frame.configure(width=usable_width)
        self.chat_log.insert(f"{window_index}+1c", "\n")

        self.chat_message_rows.append({
            "index": window_index,
            "row": row_frame,
            "right_column": right_column,
            "body": body_widget,
            "avatar_width": avatar_width,
            "turn_index": turn_index,
            "role": role,
            "edit_frame": None,
        })

        self.chat_menu_buttons.extend([row_frame, right_column, header_frame, header_label])
        if avatar_image:
            self.chat_menu_buttons.append(image_column)

        self.current_message_body_widget = body_widget
        self.current_message_body_tag = None
        self.current_message_min_blank_lines = 0
        self.chat_log.configure(state="disabled")

    def append_message_separator(self):
        """Visually separate messages without replacing the text timeline with cards."""
        self.chat_log.configure(state="normal")
        self.chat_log.insert(tk.END, "─" * 30 + "\n", "message_separator")
        self.chat_log.configure(state="disabled")

    def scroll_chat_to_bottom(self):
        """Scroll the chat timeline smoothly to the newest rendered row."""
        if self.chat_message_rows:
            self.current_chat_message_scroll_index = len(self.chat_message_rows) - 1
        self.chat_log._textbox.update_idletasks()
        self.chat_log.see(tk.END)

    def reset_input_field_height(self):
        """Return the input box to its compact height after sending."""
        if self.input_resize_job is not None:
            try:
                self.after_cancel(self.input_resize_job)
            except Exception:
                pass
            self.input_resize_job = None
        self.input_field.configure(height=self.input_min_height)

    def open_message_context_menu(self, button, role, turn_index):
        """Show the role-specific actions beside the selected ellipsis button."""
        menu = tk.Menu(
            self, tearoff=False, background="#34383d", foreground="#d9dde3",
            activebackground="#4b5056", activeforeground="#ffffff", borderwidth=0,
            font=("Segoe UI", 10),
        )

        # Identify if this message is the latest message of its role
        role_rows = [r for r in self.chat_message_rows if r.get("role") == role]
        is_last_for_role = bool(role_rows and role_rows[-1]["turn_index"] == turn_index)

        if role == "assistant":
            if is_last_for_role:
                menu.add_command(label="Edit message", command=lambda: self.handle_edit_message(turn_index))
                menu.add_separator()
            menu.add_command(label="Reroll", command=lambda: self.handle_reroll_message(turn_index))
            menu.add_separator()
            menu.add_command(label="Previous version", command=lambda: self.handle_cycle_reroll(turn_index, -1))
            menu.add_command(label="Next version", command=lambda: self.handle_cycle_reroll(turn_index, 1))
        elif role == "user":
            if is_last_for_role:
                menu.add_command(label="Edit message", command=lambda: self.handle_edit_message(turn_index))
                menu.add_separator()
            menu.add_command(label="Delete this message and later", command=lambda: self.handle_delete_from_message(turn_index))
        else:
            return
        try:
            menu.tk_popup(button.winfo_rootx(), button.winfo_rooty() + button.winfo_height())
        finally:
            menu.grab_release()

    # --- INLINE MESSAGE EDITING CONTROL SUITE ---
    def enable_inline_edit(self, turn_index: int, initial_text: str):
        """Replaces message body with an inline editor frame containing Check (Confirm) and Cross (Cancel) controls."""
        for row_data in self.chat_message_rows:
            if row_data.get("turn_index") == turn_index:
                if row_data.get("edit_frame"):
                    row_data["edit_frame"].destroy()

                # Hide static message display
                row_data["body"].grid_remove()

                right_column = row_data["right_column"]

                edit_frame = ctk.CTkFrame(right_column, fg_color="transparent")
                edit_frame.grid(row=1, column=0, sticky="ew", pady=(4, 0))
                edit_frame.grid_columnconfigure(0, weight=1)

                edit_box = ctk.CTkTextbox(
                    edit_frame,
                    height=200,
                    width=800,
                    wrap="word",
                    font=ctk.CTkFont(family="Segoe UI", size=self.current_chat_font_size)
                )
                edit_box.grid(row=0, column=0, sticky="ew", pady=(0, 6))
                edit_box.insert("1.0", initial_text)

                # Action buttons: Confirm Check (✔) and Cancel Cross (✖)
                btn_frame = ctk.CTkFrame(edit_frame, fg_color="transparent")
                btn_frame.grid(row=1, column=0, sticky="e")

                confirm_btn = ctk.CTkButton(
                    btn_frame,
                    text="✔",
                    width=32,
                    height=26,
                    fg_color="#2e7d32",
                    hover_color="#1b5e20",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    command=lambda idx=turn_index, box=edit_box: self.confirm_inline_edit(idx, box.get("1.0", tk.END).strip())
                )
                confirm_btn.pack(side="left", padx=(0, 6))

                cancel_btn = ctk.CTkButton(
                    btn_frame,
                    text="✖",
                    width=32,
                    height=26,
                    fg_color="#8b1e1e",
                    hover_color="#5a1212",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    command=lambda idx=turn_index: self.cancel_inline_edit(idx)
                )
                cancel_btn.pack(side="left")

                row_data["edit_frame"] = edit_frame
                self.chat_log._textbox.update_idletasks()
                break

    def confirm_inline_edit(self, turn_index: int, new_text: str):
        """Clean up edit mode, restore message view, and trigger controller update callback."""
        self.cancel_inline_edit(turn_index, restore_only=True)
        self.handle_save_edited_message(turn_index, new_text)

    def cancel_inline_edit(self, turn_index: int, restore_only: bool = False):
        """Clean up edit frame and unhide the message body."""
        for row_data in self.chat_message_rows:
            if row_data.get("turn_index") == turn_index:
                if row_data.get("edit_frame"):
                    row_data["edit_frame"].destroy()
                    row_data["edit_frame"] = None
                row_data["body"].grid()
                break
        if not restore_only:
            self.handle_cancel_edit_message(turn_index)

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

        # Automation
        if settings.get("memory_extraction_enabled", False):
            self.memory_extraction_switch.select()
        else:
            self.memory_extraction_switch.deselect()

        self.show_avatars = settings.get("show_avatars", True)
        if self.show_avatars:
            self.show_avatars_switch.select()
        else:
            self.show_avatars_switch.deselect()

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
            "show_avatars": bool(self.show_avatars_switch.get()),  # <-- Added
            "font_size": font_sz
        }

    def update_chat_fonts(self, size: int):
        """Updates the font size of the chat textbox, input text field, and styled tags dynamically."""
        self.current_chat_font_size = size
        font_family = "Segoe UI"
        self.chat_log.configure(font=ctk.CTkFont(family=font_family, size=size))
        self.input_field.configure(font=ctk.CTkFont(family=font_family, size=size))
        try:
            self.chat_log._textbox.configure(font=(font_family, size))
            self.input_field._textbox.configure(font=(font_family, size))
        except Exception:
            pass

        self.chat_log.tag_config("user_tag", font=ctk.CTkFont(family=font_family, size=size, weight="bold"))
        self.chat_log.tag_config("bot_tag", font=ctk.CTkFont(family=font_family, size=size, weight="bold"))
        self.chat_log.tag_config("system_tag", font=ctk.CTkFont(family=font_family, size=size, slant="italic"))
        self.chat_log.tag_config("rp_system_content", font=ctk.CTkFont(family=font_family, size=size))
        self.chat_log.tag_config("rp_narrative", font=ctk.CTkFont(family=font_family, size=size))
        self.chat_log.tag_config("rp_dialogue", font=ctk.CTkFont(family=font_family, size=size))
        self.chat_log.tag_config("rp_bold", font=ctk.CTkFont(family=font_family, size=size, weight="bold"))
        self.chat_log.tag_config("rp_thought", font=ctk.CTkFont(family=font_family, size=size, slant="italic"))
        self.refresh_message_body_appearance()
        self.schedule_input_autogrow()

    def on_font_size_dropdown_changed(self, value: str):
        """Callback to trigger dynamic updates immediately when changed in settings."""
        try:
            self.update_chat_fonts(int(value))
            self.handle_chat_display_refresh()
        except ValueError:
            pass

    def append_roleplay_text(self, text: str, base_env_tag: str = "rp_narrative"):
        """
        Parses roleplay strings hierarchically to allow nested styles.
        Example: "*Karl...* text" inside spoken words keeps the dialogue color but becomes bold.
        """
        import re

        body_widget = getattr(self, "current_message_body_widget", None)
        body_tag = getattr(self, "current_message_body_tag", None) if body_widget is None else ""
        if body_tag is None:
            body_tag = ""
        if body_widget is not None:
            text = text.replace("â€”", " - ").replace("â€“", " - ")
            text = re.sub(r' +', ' ', text)
            body_widget.configure(text=re.sub(r'\*([^*]+)\*', r'\1', text))
            if not self.chat_rendering_batch:
                self._configure_header_tab()
            self.current_message_body_widget = None
            self.current_message_body_tag = None
            self.current_message_min_blank_lines = 0
            return

        target_widget = self.chat_log
        self.chat_log.configure(state="normal")

        # --- TYPOGRAPHY SANITIZATION ---
        text = text.replace("—", " - ").replace("–", " - ")
        text = re.sub(r' +', ' ', text)

        inserted_start = target_widget.index(tk.END)

        # Split text into segments of spoken dialogue ("...") and outside narration
        segments = re.split(r'(\"[^\"]+\")', text)

        for seg in segments:
            if not seg:
                continue

            if seg.startswith('"') and seg.endswith('"'):
                current_env = "rp_dialogue"
            else:
                current_env = base_env_tag

            inline_pattern = re.compile(r'(\*[^*]+\*)|((?<!\w)\'.+?\'(?!\w))')

            last_idx = 0
            for match in inline_pattern.finditer(seg):
                start, end = match.span()

                if start > last_idx:
                    tags = (current_env, body_tag) if body_tag else (current_env,)
                    target_widget.insert(tk.END, seg[last_idx:start], tags)

                bold_chunk, thought_chunk = match.groups()
                if bold_chunk:
                    clean_text = bold_chunk[1:-1]
                    tags = (current_env, "rp_bold", body_tag) if body_tag else (current_env, "rp_bold")
                    target_widget.insert(tk.END, clean_text, tags)
                elif thought_chunk:
                    tags = (current_env, "rp_thought", body_tag) if body_tag else (current_env, "rp_thought")
                    target_widget.insert(tk.END, thought_chunk, tags)

                last_idx = end

            if last_idx < len(seg):
                tags = (current_env, body_tag) if body_tag else (current_env,)
                target_widget.insert(tk.END, seg[last_idx:], tags)

        if body_widget is None:
            self.chat_log.insert(tk.END, "\n", body_tag if body_tag else None)

        inserted_end = target_widget.index(tk.END)

        try:
            start_line = int(str(inserted_start).split(".")[0])
            end_line = int(str(inserted_end).split(".")[0])
            visible_message_lines = max(1, end_line - start_line)

            min_blank_lines = getattr(self, "current_message_min_blank_lines", 1)
            extra_blank_lines = max(0, min_blank_lines - visible_message_lines)

            for _ in range(extra_blank_lines):
                self.chat_log.insert(tk.END, "\n", body_tag if body_tag else None)
        except Exception:
            pass
        self.chat_log.configure(state="disabled")

        if not self.chat_rendering_batch:
            self._configure_header_tab()
        self.current_message_body_widget = None
        self.current_message_body_tag = None
        self.current_message_min_blank_lines = 0

    def handle_edit_message(self, turn_index):
        """Triggered when edit is chosen in header context menu or via Up arrow."""
        for row_data in self.chat_message_rows:
            if row_data.get("turn_index") == turn_index:
                # 1. Extract the current text from the tk.Message body widget
                current_text = row_data["body"].cget("text")

                # 2. Pass that text into your existing inline editor UI
                self.enable_inline_edit(turn_index, current_text)
                break

    def handle_save_edited_message(self, turn_index, edited_text):
        """Triggered when green check (✔) is clicked to commit edits to chatlog file."""
        for row_data in self.chat_message_rows:
            if row_data.get("turn_index") == turn_index:
                # Delete text up to here.
                self.handle_delete_from_message(turn_index)

                # TODO Resend updated user message.
                self.handle_chat_sent(is_edit = True, new_text = edited_text)

                break



    # --- STUB OVERRIDES (TO BE ASSIGNED BY CONTROLLER) ---
    def handle_chat_sent(self, is_edit = False, new_text = None):
        pass

    def handle_reroll_message(self, turn_index):
        pass

    def handle_cycle_reroll(self, turn_index, direction):
        pass

    def handle_delete_from_message(self, turn_index):
        pass

    def handle_cancel_edit_message(self, turn_index):
        pass

    def simulate_manual_summary(self):
        pass

    def simulated_scan(self):
        pass

    def mock_image_generation(self):
        pass

    def trigger_wipe_maintenance(self):
        pass

    def handle_save_settings(self):
        pass

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

    def handle_chat_display_refresh(self):
        pass