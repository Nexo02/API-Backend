# -*- coding: utf-8 -*-
"""
LoreEngine v1.2 - Controller & Session Memory Orchestrator
Responsible for loading configurations, tracking active sessions, managing
the local character catalogs, and binding visual interfaces securely.
"""

import os
import re
import json
import datetime
import threading
import tkinter as tk
from tkinter import filedialog
from typing import List, Dict, Any

from user_interface import OrganizedRoleplayApp
from api_client import OpenRouterClient


class PersistentDbManager:
    """
    Manages base initialization pathways, settings layout serialization,
    character catalogues, and dynamic chat sessions.
    """

    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.settings_file = os.path.join(self.base_dir, "settings.json")
        self.characters_file = os.path.join(self.base_dir, "characters.json")
        self.users_file = os.path.join(self.base_dir, "users.json")
        self.chats_dir = os.path.join(self.base_dir, "chats")

        # Dynamically build session directory folder if missing
        if not os.path.exists(self.chats_dir):
            os.makedirs(self.chats_dir)

    def get_default_settings(self) -> dict:
        return {
            "theme": "Muted Denim",
            "theme_mode": "Dark",
            "api_key": "",
            "model": "deepseek/deepseek-chat",
            "system_prompt": "You are a helpful and accurate Assistant. Help develop code, work out problems, answer questions, and provide information.",
            "temperature": 0.85,
            "max_tokens": 1024,
            "context_size": 8000,
            "max_context_messages": 20,
            "font_size": 14,
            "memory_extraction_enabled": False,
            "show_avatars": False
        }

    def load_settings(self) -> dict:
        if not os.path.exists(self.settings_file):
            defaults = self.get_default_settings()
            self.save_settings(defaults)
            return defaults
        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return self.get_default_settings()

    def save_settings(self, data: dict):
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving settings: {e}")

    # --- CHARACTER DATABASE OPERATIONS ---
    def load_characters(self) -> dict:
        if not os.path.exists(self.characters_file):
            defaults = {}  # Start completely empty from the beginning as requested
            self.save_characters(defaults)
            return defaults
        try:
            with open(self.characters_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def load_users(self) -> dict:
        if not os.path.exists(self.users_file):
            defaults = {}  # Start completely empty from the beginning as requested
            self.save_users(defaults)
            return defaults
        try:
            with open(self.users_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def save_characters(self, data: dict):
        try:
            with open(self.characters_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving characters: {e}")

    def save_users(self, data: dict):
        try:
            with open(self.users_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving users: {e}")

    # --- DYNAMIC CHAT SESSION BUILDERS ---
    def load_session_history(self, filename: str) -> list:
        filepath = os.path.join(self.chats_dir, filename)
        if not os.path.exists(filepath):
            return []  # Empty timeline from the beginning
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def save_session_history(self, filename: str, history: list):
        filepath = os.path.join(self.chats_dir, filename)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving session logs: {e}")

    def load_session_lore(self, filename: str) -> dict:
        # Swap extension safely to build the lore equivalent file
        lore_file = filename.replace("_history.json", "_lorebook.json")
        filepath = os.path.join(self.chats_dir, lore_file)
        if not os.path.exists(filepath):
            return {}  # Empty lorebook from the beginning
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def save_session_lore(self, filename: str, lore: dict):
        lore_file = filename.replace("_history.json", "_lorebook.json")
        filepath = os.path.join(self.chats_dir, lore_file)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(lore, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving lorebook: {e}")


class SessionMemoryManager:
    """
    Manages active, isolated, running memory state arrays for the currently selected chat session.
    """

    def __init__(self):
        self.active_filename = ""
        self.active_turns: List[Dict[str, str]] = []
        self.lorebook_db: Dict[str, str] = {}
        self.episodic_logs: List[str] = []
        self.short_term_keyword_cache: List[Dict[str, str]] = []

    def set_active_session(self, filename: str, history: list, lorebook: dict):
        self.active_filename = filename
        self.active_turns = history
        self.lorebook_db = lorebook
        self.episodic_logs = []  # Extract from history summary signals if present

    def add_message(self, role: str, content: str):
        if not self.active_filename:
            return
        self.active_turns.append({"role": role, "content": content})

    def add_user_message(self, content: str, user_name: str):
        if not self.active_filename:
            return
        self.active_turns.append({"role": "<user>", "name": user_name, "content": content})

    def scan_lorebook(self, text: str) -> List[str]:
        matched_context = []
        text_lower = text.lower()
        for key, description in self.lorebook_db.items():
            pattern = r'\b' + re.escape(key.lower()) + r'\b'
            if re.search(pattern, text_lower):
                matched_context.append(f"[*] Lorebook ({key.upper()}): {description}")
        return matched_context

    def get_recent_context(self, max_messages: int = 20) -> List[Dict[str, str]]:
        """
        Returns the last N user/assistant turns for context injection.
        Excludes system messages and only counts actual conversation turns.
        """
        conversation_turns = [
            turn for turn in self.active_turns
            if turn.get("role") in ("user", "<user>", "assistant")
        ]
        return conversation_turns[-max_messages:] if max_messages > 0 else []

    # def build_keyword_context_lines(self, max_items: int = 20) -> List[str]:
    #     """
    #     Converts the active lorebook into a compact list of context lines.
    #
    #     This is intended for temporary prompt injection so the model can "see"
    #     the most relevant short-form memory without needing to ingest the full lorebook.
    #
    #     Args:
    #         max_items: Maximum number of lorebook entries to include.
    #
    #     Returns:
    #         A list of formatted lines ready to be appended to a system/context prompt.
    #     """
    #     if not self.lorebook_db:
    #         return []
    #
    #     lines = []
    #     for index, (name, description) in enumerate(self.lorebook_db.items()):
    #         if index >= max_items:
    #             break
    #         lines.append(f"- {name}: {description}")
    #     return lines

    def build_temporary_context_block(self, reference_text: str = "", max_keywords: int = 20) -> str:
        """
        Builds a compact temporary memory block from the active lorebook.

        This is useful for prompt injection because it preserves the current topic
        state without sending the entire permanent lorebook every turn.

        Args:
            max_keywords: Maximum number of entries to include in the temporary block.

        Returns:
            A multi-line string suitable for a system prompt.
        """
        reference_text_lower = reference_text.lower().strip()
        matched_entries: List[Dict[str, str]] = []

        if reference_text_lower:
            for name, description in self.lorebook_db.items():
                pattern = r'\b' + re.escape(name.lower()) + r'\b'
                if re.search(pattern, reference_text_lower):
                    matched_entries.append({"name": name, "description": description})

        if not matched_entries:
            matched_entries = [
                {"name": name, "description": description}
                for name, description in list(self.lorebook_db.items())[:max_keywords]
            ]
        else:
            matched_entries = matched_entries[:max_keywords]

        self.short_term_keyword_cache = matched_entries

        if not matched_entries:
            return ""

        lines = ["Temporary Context Memory:"]
        for entry in matched_entries:
            lines.append(f"- {entry['name']}: {entry['description']}")

        return "\n".join(lines)


class RoleplayOrchestrator:
    """
    Main Controller running coordination of data streams, file systems, and interface bindings.
    """

    def __init__(self):
        self.db = PersistentDbManager()
        self.memory = SessionMemoryManager()
        self.session_display_to_file: Dict[str, str] = {}
        self.session_file_to_display: Dict[str, str] = {}

        # --- BOT NAME & REROLL STATE TRACKERS ---
        self.active_bot_name = "Bot"
        self.reroll_cache: List[str] = []
        self.reroll_index: int = -1
        # ----------------------------------------

        self.characters = self.db.load_characters()
        self.users = self.db.load_users()
        self.selected_avatar_path = ""  # Buffer for currently loaded image reference
        self.selected_user_avatar_path = ""
        self.active_user_name = "New User..."

        self.app = OrganizedRoleplayApp()

        # Load setup variables
        self.global_settings = self.db.load_settings()
        self.app.load_settings_into_ui(self.global_settings)
        self.active_user_name = self.global_settings.get("active_user", self.active_user_name)

        # Bind interface hooks
        self.bind_ui_callbacks()

        # Build catalogs
        self.rebuild_character_dropdown()
        self.rebuild_user_dropdown()
        self.rebuild_session_dropdown()

        session_was_loaded = False
        # If a session exists and is selected in the dashboard, load it immediately.
        selected_session = self.app.session_dropdown.get()
        if selected_session and "No active sessions" not in selected_session and "No sessions available" not in selected_session:
            self.on_session_loaded()
            session_was_loaded = True

        # Shutdown safety routine
        self.app.protocol("WM_DELETE_WINDOW", self.on_close_save_routine)

        if not session_was_loaded:
            self.app.append_system_msg(
                "LoreEngine v1.2 Active Session Controller initialized.\n"
                "Go to the 'Characters' tab to create a character and launch a chat!"
            )

    def bind_ui_callbacks(self):
        self.app.handle_chat_sent = self.on_chat_sent
        self.app.simulate_manual_summary = self.on_force_summary
        self.app.simulated_scan = self.on_lore_scan
        self.app.mock_image_generation = self.on_image_generation
        self.app.trigger_wipe_maintenance = self.on_wipe_maintenance
        self.app.handle_reroll_message = self.trigger_reroll
        self.app.handle_cycle_reroll = self.cycle_reroll
        self.app.handle_delete_from_message = self.delete_from_message
        self.app.handle_save_settings = self.on_settings_saved
        self.app.handle_chat_display_refresh = self.render_active_memory_to_ui

        # Character/Session system hooks
        self.app.handle_character_dropdown_changed = self.on_character_changed
        self.app.handle_avatar_upload = self.on_avatar_uploaded
        self.app.handle_save_character = self.on_character_saved
        self.app.handle_user_dropdown_changed = self.on_user_changed
        self.app.handle_user_avatar_upload = self.on_user_avatar_uploaded
        self.app.handle_save_user = self.on_user_saved
        self.app.handle_launch_session = self.on_session_launched
        self.app.handle_session_changed = self.on_session_loaded

    # ==========================================
    # FILE LISTING & DROPDOWN SYNC ENGINE
    # ==========================================
    def rebuild_character_dropdown(self):
        names = list(self.characters.keys())
        menu_items = ["New Character..."] + names
        self.app.char_dropdown.configure(values=menu_items)
        self.app.char_dropdown.set("New Character...")

    def rebuild_user_dropdown(self):
        names = list(self.users.keys())
        menu_items = ["New User..."] + names
        self.app.user_profile_dropdown.configure(values=menu_items)
        self.app.active_user_dropdown.configure(values=menu_items)

        if self.active_user_name in names:
            self.app.user_profile_dropdown.set(self.active_user_name)
            self.app.active_user_dropdown.set(self.active_user_name)
        else:
            self.app.user_profile_dropdown.set("New User...")
            self.app.active_user_dropdown.set("New User...")
            self.active_user_name = "New User..."

    def rebuild_session_dropdown(self):
        """Looks inside the chats/ folder and builds list of history files."""
        self.session_display_to_file = {}
        self.session_file_to_display = {}

        if not os.path.exists(self.db.chats_dir):
            self.app.session_dropdown.configure(values=["No sessions available"])
            self.app.session_dropdown.set("No sessions available")
            return

        all_files = os.listdir(self.db.chats_dir)
        chat_sessions = [f for f in all_files if f.endswith("_history.json")]

        # Most recently touched sessions first so the latest conversation stays on top.
        chat_sessions.sort(
            key=lambda name: os.path.getmtime(os.path.join(self.db.chats_dir, name)),
            reverse=True
        )

        if not chat_sessions:
            self.app.session_dropdown.configure(values=["No active sessions"])
            self.app.session_dropdown.set("No active sessions")
        else:
            display_items = []
            for filename in chat_sessions:
                label = self._build_session_display_label(filename)
                if label in self.session_display_to_file:
                    # Keep labels unique when metadata is identical for multiple sessions.
                    counter = 2
                    unique_label = f"{label} ({counter})"
                    while unique_label in self.session_display_to_file:
                        counter += 1
                        unique_label = f"{label} ({counter})"
                    label = unique_label

                self.session_display_to_file[label] = filename
                self.session_file_to_display[filename] = label
                display_items.append(label)

            self.app.session_dropdown.configure(values=display_items)
            if self.memory.active_filename in self.session_file_to_display:
                self.app.session_dropdown.set(self.session_file_to_display[self.memory.active_filename])
            else:
                self.app.session_dropdown.set(display_items[0])

    def _build_session_display_label(self, filename: str) -> str:
        base_name = filename.replace("_history.json", "")

        # Expected format: Character_YYYYMMDD_HHMMSS_history.json
        match = re.match(r"^(?P<char>.+?)_(?P<date>\d{8})_(?P<time>\d{6})$", base_name)
        if match:
            char_name = match.group("char")
            started_raw = f"{match.group('date')}_{match.group('time')}"
            try:
                started = datetime.datetime.strptime(started_raw, "%Y%m%d_%H%M%S").strftime("%Y-%m-%d %H:%M")
            except ValueError:
                started = "unknown"
        else:
            char_name = base_name
            started = "unknown"

        history = self.db.load_session_history(filename)
        chat_count = sum(1 for turn in history if turn.get("role") in ("user", "<user>", "assistant"))

        filepath = os.path.join(self.db.chats_dir, filename)
        try:
            last_chat = datetime.datetime.fromtimestamp(os.path.getmtime(filepath)).strftime("%Y-%m-%d %H:%M")
        except OSError:
            last_chat = started

        return f"{char_name} | last: {last_chat} | chats: {chat_count}"

    # ==========================================
    # CHARACTER AND SESSION MANAGEMENT
    # ==========================================
    def on_character_changed(self):
        selected_name = self.app.char_dropdown.get()
        if selected_name == "New Character...":
            self.app.char_name_field.delete(0, tk.END)
            self.app.char_desc_field.delete("1.0", tk.END)
            self.app.avatar_path_lbl.configure(text="Avatar: None")
            self.selected_avatar_path = ""
        else:
            profile = self.characters.get(selected_name, {})
            self.app.char_name_field.delete(0, tk.END)
            self.app.char_name_field.insert(0, selected_name)

            self.app.char_desc_field.delete("1.0", tk.END)
            self.app.char_desc_field.insert("1.0", profile.get("description", ""))

            avatar = profile.get("avatar", "None")
            self.app.avatar_path_lbl.configure(text=f"Avatar: {os.path.basename(avatar)}")
            self.selected_avatar_path = avatar

    def on_user_changed(self, value: str | None = None):
        selected_name = value if value is not None else self.app.active_user_dropdown.get()
        if selected_name == "New User...":
            self.app.user_name_field.delete(0, tk.END)
            self.app.user_desc_field.delete("1.0", tk.END)
            self.app.user_avatar_path_lbl.configure(text="Avatar: None")
            self.selected_user_avatar_path = ""
            self.active_user_name = "New User..."
        else:
            profile = self.users.get(selected_name, {})
            self.app.user_name_field.delete(0, tk.END)
            self.app.user_name_field.insert(0, selected_name)

            self.app.user_desc_field.delete("1.0", tk.END)
            self.app.user_desc_field.insert("1.0", profile.get("description", ""))

            avatar = profile.get("avatar", "None")
            self.app.user_avatar_path_lbl.configure(text=f"Avatar: {os.path.basename(avatar)}")
            self.selected_user_avatar_path = avatar
            self.active_user_name = selected_name

        self.app.user_profile_dropdown.set(selected_name)
        self.app.active_user_dropdown.set(selected_name)

        current_ui_state = self.app.get_current_ui_settings()
        current_ui_state["active_user"] = self.active_user_name
        self.db.save_settings(current_ui_state)

    def on_user_avatar_uploaded(self):
        file_path = filedialog.askopenfilename(
            title="Select User Avatar",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if file_path:
            self.selected_user_avatar_path = file_path
            self.app.user_avatar_path_lbl.configure(text=f"Avatar: {os.path.basename(file_path)}")

    def on_avatar_uploaded(self):
        file_path = filedialog.askopenfilename(
            title="Select Profile Avatar",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if file_path:
            self.selected_avatar_path = file_path
            self.app.avatar_path_lbl.configure(text=f"Avatar: {os.path.basename(file_path)}")

    def on_character_saved(self):
        name = self.app.char_name_field.get().strip()
        description = self.app.char_desc_field.get("1.0", tk.END).strip()

        if not name:
            self.app.append_system_msg("Error: Character Name field is required to save.")
            return

        self.characters[name] = {
            "description": description,
            "avatar": self.selected_avatar_path
        }
        self.db.save_characters(self.characters)
        self.rebuild_character_dropdown()
        self.app.char_dropdown.set(name)
        self.app.append_system_msg(f"Character Profile for '{name}' saved successfully.")

    def on_user_saved(self):
        name = self.app.user_name_field.get().strip()
        description = self.app.user_desc_field.get("1.0", tk.END).strip()

        if not name:
            self.app.append_system_msg("Error: User Name field is required to save.")
            return

        self.users[name] = {
            "description": description,
            "avatar": self.selected_user_avatar_path
        }
        self.db.save_users(self.users)
        self.rebuild_user_dropdown()
        self.app.user_profile_dropdown.set(name)
        self.app.active_user_dropdown.set(name)
        self.active_user_name = name
        current_ui_state = self.app.get_current_ui_settings()
        current_ui_state["active_user"] = self.active_user_name
        self.db.save_settings(current_ui_state)
        self.app.append_system_msg(f"User Profile for '{name}' saved successfully.")

    def on_session_launched(self):
        """Creates a completely fresh session using character descriptions."""
        selected_name = self.app.char_dropdown.get()
        if selected_name == "New Character...":
            self.app.append_system_msg("Please select or save a character before starting a chat.")
            return

        # Build a safe timestamp-based unique filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_char_name = re.sub(r'[^a-zA-Z0-9]', '', selected_name)
        session_filename = f"{safe_char_name}_{timestamp}_history.json"

        # Initialize clean empty lore and history databases (starting with empty memory)
        profile_desc = self.characters.get(selected_name, {}).get("description", "")

        # Inject character description as the default system prompt starter context if desired
        system_starting_prompt = f"Roleplay Session with {selected_name}. Character description: {profile_desc}"

        initial_history = [{"role": "system", "content": system_starting_prompt}]
        initial_lore = {}  # Fresh, clean, empty lorebook as preferred

        # Commit to physical disk immediately
        self.db.save_session_history(session_filename, initial_history)
        self.db.save_session_lore(session_filename, initial_lore)

        # Set running state memory references
        self.memory.set_active_session(session_filename, initial_history, initial_lore)

        self.rebuild_session_dropdown()
        if session_filename in self.session_file_to_display:
            self.app.session_dropdown.set(self.session_file_to_display[session_filename])
        self.on_session_loaded()

        self.app.append_system_msg(f"New persistent chat canvas initiated with '{selected_name}'.")

    def on_session_loaded(self):
        """Loads selected file logs from dropdown into visual interface."""
        selected_value = self.app.session_dropdown.get()
        if not selected_value or "sessions" in selected_value:
            return

        # Lock in the current in-memory timeline before switching sessions.
        self.commit_active_session_history()

        self.active_bot_name = selected_value.split("|")[0].split("(")[0].strip()

        selected_file = self.session_display_to_file.get(selected_value, selected_value)

        # Load from physical storage
        history = self.db.load_session_history(selected_file)
        lorebook = self.db.load_session_lore(selected_file)

        self.memory.set_active_session(selected_file, history, lorebook)

        # Render the newly loaded memory to screen!
        self.render_active_memory_to_ui()

        # Draw corresponding lore database to Editor panel
        self.rebuild_lorebook_editor_text()
        self.update_sidebar_counters()

    # ==========================================
    # CORE REBUILDERS & COUNTERS
    # ==========================================
    def rebuild_lorebook_editor_text(self):
        self.app.lore_editor.configure(state="normal")
        self.app.lore_editor.delete("1.0", tk.END)

        header = (
            "=========================================\n"
            "         ACTIVE VECTOR SHEETS (LIVE)     \n"
            "=========================================\n\n"
        )
        self.app.lore_editor.insert(tk.END, header)

        if not self.memory.lorebook_db:
            self.app.lore_editor.insert(tk.END, "[*] Lorebook is currently empty. Facts will auto-compile here during gameplay!")
        else:
            for key, desc in self.memory.lorebook_db.items():
                self.app.lore_editor.insert(tk.END, f"[*] {key.upper()}\n - {desc}\n\n")

        self.app.lore_editor.see(tk.END)

    def update_sidebar_counters(self):
        self.app.token_label.configure(text=f"Active Conversational Window: {len(self.memory.active_turns)} turns")
        self.app.lore_label.configure(text=f"Vector Lorebook Nodes: {len(self.memory.lorebook_db)}")
        self.app.summary_label.configure(text=f"Stored Epic Summaries: {len(self.memory.episodic_logs)}")

    def commit_active_session_history(self):
        """Persist the currently selected in-memory chat timeline to disk."""
        if not self.memory.active_filename:
            return
        self.db.save_session_history(self.memory.active_filename, self.memory.active_turns)

    def get_character_avatar_path(self, character_name: str) -> str:
        """Returns the avatar path for the active character, including safe filename fallback matching."""
        if character_name in self.characters:
            return self.characters.get(character_name, {}).get("avatar", "")

        normalized_character_name = re.sub(r'[^a-zA-Z0-9]', '', character_name).lower()
        for saved_name, profile in self.characters.items():
            normalized_saved_name = re.sub(r'[^a-zA-Z0-9]', '', saved_name).lower()
            if normalized_saved_name == normalized_character_name:
                return profile.get("avatar", "")

        return ""

    def get_user_avatar_path(self, user_name: str) -> str:
        """Returns the avatar path for the displayed user speaker."""
        if user_name in self.users:
            return self.users.get(user_name, {}).get("avatar", "")

        if self.active_user_name in self.users:
            return self.users.get(self.active_user_name, {}).get("avatar", "")

        return ""

    def build_chat_messages(self, user_message: str) -> List[Dict[str, str]]:
        """
        Builds the structured message list for a roleplay completion.
        """
        messages: List[Dict[str, str]] = []

        # 1. Global System Prompt
        system_prompt = self.global_settings.get("system_prompt", "")
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        char_profile = self.characters.get(self.active_bot_name, {}).get("description", "")
        if char_profile:
            messages.append({
                "role": "system",
                "content": f"You are playing the role of {self.active_bot_name}.\nCharacter Description:\n{char_profile}"
            })

        user_profile = self.users.get(self.active_user_name, {}).get("description", "")
        if user_profile and self.active_user_name != "New User...":
            messages.append({
                "role": "system",
                "content": f"The user you are interacting with is {self.active_user_name}.\nUser Description/Persona:\n{user_profile}"
            })

        # 2. Formatting Rules
        formatting_context = (
            "Roleplay formatting rules:\n"
            "- Do not write the Characters or Users names in your responses, but use 'I' and 'You'\n"
            "- Use double quotes (\"...\") for spoken dialogue.\n"
            "- Use single quotes ('...') for internal thoughts/monologue.\n"
            "- Use single asterisks (*...*) for bolding important text.\n"
            "- Write all actions, descriptions, and narration as plain, unformatted text (no asterisks, no quotes).\n"
            "Strictly follow these rules and adapt output to align with the user's formatting style."
        )
        messages.append({"role": "system", "content": formatting_context})

        max_context_messages = int(self.global_settings.get("max_context_messages", 10))
        recent_context = self.memory.get_recent_context(max_messages=max_context_messages)

        # --- FIX: STRIP UNWANTED TRAILING MESSAGES ---
        # 1. If rerolling, recent_context ends with the old assistant reply. Strip it so the model never sees it!
        if recent_context and recent_context[-1].get("role") == "assistant":
            recent_context = recent_context[:-1]

        # 2. Strip the matching user turn so it isn't duplicated when final_user_msg is added at the end
        if (
                recent_context
                and recent_context[-1].get("role") in ("user", "<user>")
                and recent_context[-1].get("content", "") == user_message
        ):
            recent_context = recent_context[:-1]

        context_text_parts = [turn.get("content", "") for turn in recent_context]
        context_text_parts.append(user_message)
        temporary_context = self.memory.build_temporary_context_block(
            reference_text="\n".join(context_text_parts),
            max_keywords=min(20, max_context_messages * 2)
        )
        if temporary_context:
            messages.append({"role": "system", "content": temporary_context})

        # --- NEW: EXPLICITLY TAG CHAT HISTORY WITH NAMES ---
        for turn in recent_context:
            role = turn.get("role", "user")
            speaker = turn.get("name", "")

            if role == "<user>":
                role = "user"
            if role not in ("user", "assistant", "system"):
                role = "user"

            content = turn.get("content", "")
            if content:
                # Prefixing the name makes it explicitly clear who is speaking
                if role == "user":
                    display_name = speaker if speaker else self.active_user_name
                    if display_name != "New User...":
                        content = f"[{display_name}]: {content}"

                messages.append({"role": role, "content": content})

        # 3. Tag the final, current user message
        final_user_name = self.active_user_name
        if final_user_name != "New User...":
            final_user_msg = f"[{final_user_name}]: {user_message}"
        else:
            final_user_msg = user_message

        messages.append({"role": "user", "content": final_user_msg})
        return messages

    def _build_roleplay_response(self, user_message: str) -> str:
        """
        Sends the memory-aware chat payload to OpenRouter and returns the reply.

        This is the main roleplay inference path and should be used instead of the
        temporary placeholder response once API data flow is enabled.
        """
        api_key = self.global_settings.get("api_key", "")
        if not api_key.strip():
            return "Error: Missing valid API Key. Please update your Settings tab with an OpenRouter Key."

        client = OpenRouterClient(api_key)
        messages = self.build_chat_messages(user_message=user_message)

        return client.generate_chat_completion(
            messages=messages,
            model=self.global_settings.get("model", "deepseek/deepseek-chat"),
            temperature=float(self.global_settings.get("temperature", 0.85)),
            max_tokens=int(self.global_settings.get("max_tokens", 1024))
        )

    def _build_extraction_prompt(self, user_message: str, recent_context: List[Dict[str, str]],
                                 existing_keywords: List[str], last_bot_message: str = "") -> str:
        """
        Builds a high-precision extraction prompt focused ONLY on long-term persistent lore,
        filtering out temporary dialogue and minor scene actions.
        """
        context_str = ""
        for turn in recent_context:
            role = "User" if turn.get("role") in ("user", "<user>") else "Bot"
            content = turn.get("content", "")
            context_str += f"{role}: {content}\n"

        existing_keywords_str = "\n".join(
            [f"- {key}" for key in existing_keywords]) if existing_keywords else "None"

        return f"""You are an elite lore keeper. Extract ONLY high-value, persistent information from this conversation context.

RECENT CONVERSATION:
{context_str}

CURRENT USER MESSAGE:
{user_message}

EXISTING LOREBOOK KEYWORDS:
{existing_keywords_str}

=== WHAT TO IGNORE (TRIVIAL FLUFF) ===
- Temporary physical actions or poses (e.g., "sitting down", "nodding", "walking to the window").
- Transient emotional states or temporary moods (e.g., "is angry right now", "smiled").
- Conversational fluff, greetings, or short-term dialogue responses.

=== WHAT TO EXTRACT (MEANINGFUL CONTEXT & LORE) ===
Extract facts that provide helpful long-term context or mark story progression:
1. Significant plot progression, major decisions, or key events.
2. Character developments, personal revelations, backstories, traits, or established preferences.
3. Notable shifts in relationships, promises made, or agreements reached between characters.
4. Important items, artifacts, locations, factions, or key terms introduced or acquired.

=== MERGING & FORMATTING RULES ===
1. If new information relates to an item in "EXISTING LOREBOOK KEYWORDS", reuse that EXACT entity name (e.g., "Karl") so the system can merge the details seamlessly.
2. Focus entity names on specific Nouns, Character Names, Locations, or Concepts.
3. If no noteworthy or memorable facts occurred in this exchange, return an empty "keywords" list: [].
4. Keep each description to ONE concise, factual sentence.

Return ONLY valid JSON:
{{
    "keywords": [
        {{"name": "EntityName", "description": "One concise sentence describing the meaningful fact, trait, or event."}}
    ]
}}
"""

    def _parse_extracted_keywords(self, response_text: str) -> List[Dict[str, str]]:
        """
        Parses the extraction model response and returns normalized keyword entries.

        The parser is intentionally defensive: it accepts extra text around the JSON
        object, but still validates the structure before returning anything.
        """
        try:
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            if json_start == -1 or json_end <= json_start:
                print("[Memory] No JSON found in extraction response")
                return []

            parsed = json.loads(response_text[json_start:json_end])
            keywords = parsed.get("keywords", [])
            if not isinstance(keywords, list):
                print(f"[Memory] Invalid keywords format in response: {type(keywords)}")
                return []

            valid_keywords = []
            for keyword in keywords:
                if isinstance(keyword, dict) and "name" in keyword and "description" in keyword:
                    valid_keywords.append({
                        "name": str(keyword["name"]).strip(),
                        "description": str(keyword["description"]).strip()
                    })
                else:
                    print(f"[Memory] Skipping malformed keyword entry: {keyword}")

            return valid_keywords
        except json.JSONDecodeError as error:
            print(f"[Memory] JSON parse error in keyword extraction: {error}")
            return []
        except Exception as error:
            print(f"[Memory] Unexpected error parsing keywords: {error}")
            return []

    def _merge_keywords_into_lorebook(self, new_keywords: List[Dict[str, str]]) -> int:
        """
        Adds newly extracted keywords to the active session lorebook.
        If a keyword already exists, an API call consolidates both entries
        to ensure old information is preserved and expanded instead of lost.
        """
        if not new_keywords:
            return 0

        # Build a case-insensitive map of existing keys pointing to their actual casing
        existing_keys_lower = {key.lower(): key for key in self.memory.lorebook_db.keys()}
        added_count = 0
        updated_count = 0

        api_key = self.global_settings.get("api_key", "").strip()

        for keyword in new_keywords:
            name = keyword.get("name", "").strip()
            description = keyword.get("description", "").strip()

            if not name or not description:
                print(f"[Memory] Skipping incomplete keyword: {keyword}")
                continue

            # Check if this keyword is a duplicate (double keyword found)
            if name.lower() in existing_keys_lower:
                actual_key = existing_keys_lower[name.lower()]
                old_description = self.memory.lorebook_db[actual_key]
                
                # Skip if the description is an identical match to prevent infinite API redundancy
                if old_description.strip().lower() == description.strip().lower():
                    continue

                if not api_key:
                    print(f"[Memory] Cannot merge duplicate '{actual_key}': Missing API Key.")
                    continue

                print(f"[Memory] Duplicate found for '{actual_key}'. Requesting summary consolidation...")
                
                # Ask the API to merge both entries together
                merged_description = self._consolidate_double_keyword(
                    api_key=api_key,
                    keyword=actual_key,
                    old_desc=old_description,
                    new_desc=description
                )
                
                self.memory.lorebook_db[actual_key] = merged_description
                updated_count += 1
                print(f"[Memory] Successfully updated duplicate keyword: '{actual_key}'")
                continue

            # If it's completely new, insert it normally
            self.memory.lorebook_db[name] = description
            added_count += 1
            print(f"[Memory] Added new keyword: '{name}'")

        # Refresh the UI sheets immediately if changes occurred
        if added_count > 0 or updated_count > 0:
            self.db.save_session_lore(self.memory.active_filename, self.memory.lorebook_db)
            # Use self.app.after safely to sync UI redraws back to the main thread
            self.app.after(0, self.rebuild_lorebook_editor_text)
            self.app.after(0, self.update_sidebar_counters)

        return added_count + updated_count

    def _consolidate_double_keyword(self, api_key: str, keyword: str, old_desc: str, new_desc: str) -> str:
        """
        Sends a targeted prompt to the API comparing two duplicate descriptions,
        returning a combined summary that retains all previous facts while adding new context.
        """
        try:
            client = OpenRouterClient(api_key)
            
            consolidation_prompt = f"""You are a precise lore database maintenance system. 
We have uncovered new information about an existing lorebook entity. Combine both entries into a single cohesive, unified description.

ENTITY NAME: {keyword}

EXISTING MEMORY:
{old_desc}

NEW UPDATED OBSERVATION:
{new_desc}

CRITICAL RULES:
1. Do NOT lose or omit any historical data or facts from the 'EXISTING MEMORY'.
2. Seamlessly blend, merge, and expand it with the 'NEW UPDATED OBSERVATION'.
3. Do not repeat facts if they overlap.
4. Keep the final response short and cohesive (maximum 2-3 sentences).
5. Output ONLY the raw consolidated text description. Do not wrap in JSON, markdown formatting, or include any intro/outro pleasantries.
"""

            response = client.generate_completion(
                prompt=consolidation_prompt,
                model=self.global_settings.get("model", "deepseek/deepseek-chat"),
                system_prompt="You are an accurate lorebook consolidation engine. Output raw text descriptions only.",
                temperature=0.15, # Kept low for deterministic factual tracking
                max_tokens=250
            )
            
            clean_result = response.strip()
            # Safety net in case the model returns empty or errors out
            return clean_result if clean_result else f"{old_desc} {new_desc}"
            
        except Exception as e:
            print(f"[Memory] Error during double keyword consolidation: {e}")
            return f"{old_desc} {new_desc}" # Fallback layout: preserve both manually

    def extract_keywords_async(self, user_message: str) -> None:
        """
        Runs Stage 2 extraction on a background thread.
        Provides existing keywords to the prompt to prevent duplicate entries.
        """
        try:
            if not self.global_settings.get("memory_extraction_enabled", False):
                print("[Memory] Memory extraction skipped: setting is disabled")
                return

            api_key = self.global_settings.get("api_key", "")
            if not api_key.strip():
                print("[Memory] Memory extraction disabled: no API key")
                return

            recent_context = self.memory.get_recent_context(max_messages=10)

            # The current user message was already added to memory before this thread starts.
            # Keep it only in CURRENT USER MESSAGE, not duplicated inside RECENT CONVERSATION.
            if (
                    recent_context
                    and recent_context[-1].get("role") in ("user", "<user>")
                    and recent_context[-1].get("content", "") == user_message
            ):
                recent_context = recent_context[:-1]

            last_bot_message = ""
            for turn in reversed(recent_context):
                if turn.get("role") == "assistant":
                    last_bot_message = turn.get("content", "")
                    break

            # Grab current lorebook keys to feed to the API
            existing_keys = list(self.memory.lorebook_db.keys())

            # Pass the existing keys and last bot reply into the prompt builder
            extraction_prompt = self._build_extraction_prompt(
                user_message=user_message,
                recent_context=recent_context,
                existing_keywords=existing_keys,
                last_bot_message=last_bot_message
            )

            client = OpenRouterClient(api_key)
            print("[Memory] Starting keyword extraction...")
            response = client.generate_completion(
                prompt=extraction_prompt,
                model=self.global_settings.get("model", "deepseek/deepseek-chat"),
                system_prompt="You are a precise entity extraction system. Return only valid JSON.",
                temperature=0.15,
                max_tokens=500
            )

            extracted_keywords = self._parse_extracted_keywords(response)
            print(f"[Memory] Parsed {len(extracted_keywords)} keywords from extraction")

            added_count = self._merge_keywords_into_lorebook(extracted_keywords)
            print(f"[Memory] Keyword extraction complete: {added_count} entries processed")
        except Exception as error:
            print(f"[Memory] Error in keyword extraction: {error}")


    # ==========================================
    # ACTION DELEGATES (WORKERS)
    # ==========================================
    # ==========================================
    # ACTION DELEGATES & REROLL ENGINE
    # ==========================================
    def on_chat_sent(self, is_edit = False, new_text = None):
        if not self.memory.active_filename:
            self.app.append_system_msg("Please create and launch a Character Chat Session first.")
            return
        if is_edit:
            user_input = new_text
        else:
            user_input = self.app.input_field.get("1.0", tk.END).strip()
        if not user_input:
            return

        # 1. COMMIT LAST TURN ON NEW SEND
        # Before we append a new user message, we permanently save the last assistant reroll select
        if not is_edit: self.db.save_session_history(self.memory.active_filename, self.memory.active_turns)

        self.app.input_field.delete("1.0", tk.END)
        self.app.reset_input_field_height()

        active_user = self.active_user_name if self.active_user_name != "New User..." else "You"

        # 2. CLEAR REROLL STATE FOR NEW TURN
        self.reroll_cache = []
        self.reroll_index = -1

        self.memory.add_user_message(user_input, active_user)
        self.render_turn_to_ui(len(self.memory.active_turns) - 1, self.memory.active_turns[-1])
        self.app.scroll_chat_to_bottom()
        # We save the user's message to disk immediately
        self.db.save_session_history(self.memory.active_filename, self.memory.active_turns)
        
        self.update_sidebar_counters()
        self.rebuild_session_dropdown()

        # STAGE 2: Trigger async keyword extraction if enabled
        threading.Thread(target=self.extract_keywords_async, args=(user_input,), daemon=True).start()

        # Dispatch generation thread
        threading.Thread(target=self._async_chat_placeholder, args=(user_input,), daemon=True).start()

    def _async_chat_placeholder(self, prompt: str):
        """Background worker that gets the response from the API."""
        bot_response = self._build_roleplay_response(prompt)
        self.app.after(0, lambda: self._handle_response_printing(bot_response))

    def _handle_response_printing(self, text: str):
        """Handles showing the response, pushing to the cache, and deferring disk saving."""
        # 1. Automatically strip leading prefixes like "Sam:", "[Sam]:", "Sam: Answer", or "Answer:"
        prefix_pattern = rf"^(\[{re.escape(self.active_bot_name)}\]:?\s*|{re.escape(self.active_bot_name)}:\s*(Answer:?)?\s*|Answer:\s*)"
        text = re.sub(prefix_pattern, "", text, flags=re.IGNORECASE).strip()

        # 2. Clean up typography
        text = text.replace("—", " - ").replace("–", " - ")

        # Store in reroll cache
        self.reroll_cache.append(text)
        self.reroll_index = len(self.reroll_cache) - 1

        # If we are overwriting an existing temporary turn, pop it first
        replacing_last_assistant = False
        if self.memory.active_turns and self.memory.active_turns[-1].get("role") == "assistant":
            self.memory.active_turns.pop()
            replacing_last_assistant = True

        # Add to the in-memory state so the UI can render it
        self.memory.add_message("assistant", text)

        # Persist the currently selected assistant response immediately.
        self.commit_active_session_history()

        if replacing_last_assistant:
            self.render_active_memory_to_ui()
        else:
            # Append the new assistant turn without rebuilding the whole chat timeline.
            self.render_turn_to_ui(len(self.memory.active_turns) - 1, self.memory.active_turns[-1])
            self.app.scroll_chat_to_bottom()

        self.update_sidebar_counters()
        self.rebuild_session_dropdown()

    def render_turn_to_ui(self, turn_index: int, turn: dict):
        """Append a single memory turn to the chat timeline."""
        role = turn.get("role", "system")
        content = turn.get("content", "")
        speaker = turn.get("name") or turn.get("speaker") or self.active_user_name
        bot = self.active_bot_name

        user_avatar_path = self.get_user_avatar_path(speaker)
        bot_avatar_path = self.get_character_avatar_path(bot)

        self.app.append_message_separator()
        if role in ("user", "<user>"):
            self.app.append_message_header(
                f"User: {speaker}",
                "user_tag",
                "user",
                turn_index,
                avatar_path=user_avatar_path
            )
        elif role == "assistant":
            self.app.append_message_header(
                f"Bot: {bot}",
                "bot_tag",
                "assistant",
                turn_index,
                avatar_path=bot_avatar_path
            )
        elif role == "system":
            self.app.append_message_header("System Info", "system_tag", "system", turn_index)

        self.app.append_roleplay_text(content)

    def render_active_memory_to_ui(self):
        """Renders the current in-memory active turns directly to the screen without reloading from disk."""
        self.app.clear_chat_message_controls()
        self.app.begin_chat_render()
        try:
            for turn_index, turn in enumerate(self.memory.active_turns):
                self.render_turn_to_ui(turn_index, turn)
        finally:
            self.app.finish_chat_render()

        self.app.scroll_chat_to_bottom()

    def trigger_reroll(self, turn_index=None):
        """Initiates a reroll of the last assistant turn, discarding it from disk and fetching a new response."""
        if not self.memory.active_turns:
            return

        if turn_index is None:
            turn_index = len(self.memory.active_turns) - 1
        if turn_index != len(self.memory.active_turns) - 1:
            self.app.append_system_msg("Only the latest assistant reply can be rerolled.")
            return

        # Ensure the last message is actually from the assistant
        if self.memory.active_turns[turn_index].get("role") != "assistant":
            self.app.append_system_msg("Cannot reroll: The last message was not sent by the assistant.")
            return

        # Find the last user message to prompt the API with
        last_user_message = ""
        for turn in reversed(self.memory.active_turns[:turn_index]):
            if turn.get("role") in ("user", "<user>"):
                last_user_message = turn.get("content", "")
                break

        if not last_user_message:
            self.app.append_system_msg("Cannot reroll: No preceding user prompt found.")
            return

        self.app.append_system_msg("Generating alternative response...")
        threading.Thread(target=self._async_chat_placeholder, args=(last_user_message,), daemon=True).start()

    def cycle_reroll(self, turn_index: int, direction: int):
        """Cycles between cached rerolls (direction can be -1 for Prev, 1 for Next)."""
        if turn_index != len(self.memory.active_turns) - 1:
            self.app.append_system_msg("Only the latest assistant reply has selectable versions.")
            return
        if not self.reroll_cache or len(self.reroll_cache) <= 1:
            self.app.append_system_msg("No alternative rerolls available to switch between.")
            return

        new_index = self.reroll_index + direction
        if 0 <= new_index < len(self.reroll_cache):
            self.reroll_index = new_index
            selected_text = self.reroll_cache[self.reroll_index]

            # Update in-memory state
            if self.memory.active_turns and self.memory.active_turns[-1].get("role") == "assistant":
                self.memory.active_turns[-1]["content"] = selected_text

            # Persist whichever reroll version is currently selected.
            self.commit_active_session_history()

            # Render from live memory
            self.render_active_memory_to_ui()
            self.app.append_system_msg(f"Switched to variation {self.reroll_index + 1}/{len(self.reroll_cache)}")
        else:
            self.app.append_system_msg("Reached end of alternative variations.")

    def delete_from_message(self, turn_index: int):
        """Delete a selected user message and every later message in the session."""
        if turn_index < 0 or turn_index >= len(self.memory.active_turns):
            return
        if self.memory.active_turns[turn_index].get("role") not in ("user", "<user>"):
            self.app.append_system_msg("Only user messages can rewind the conversation.")
            return

        self.memory.active_turns = self.memory.active_turns[:turn_index]
        self.reroll_cache = []
        self.reroll_index = -1
        self.db.save_session_history(self.memory.active_filename, self.memory.active_turns)
        self.render_active_memory_to_ui()

    def on_force_summary(self):
        self.app.append_system_msg("Manual summary integration worker called.")

    def on_lore_scan(self):
        self.app.append_system_msg(f"Active session lore entries: {list(self.memory.lorebook_db.keys())}")

    def on_image_generation(self):
        self.app.append_system_msg("Scene art prompt requested.")

    # ==========================================
    # SELECTIVE SESSION MAINTENANCE
    # ==========================================
    def on_wipe_maintenance(self):
        """Clears ONLY the active chat session history and lore without reset of settings or other files."""
        if not self.memory.active_filename:
            self.app.append_system_msg("No session currently loaded to wipe.")
            return

        # Wipe current history logs back to starting system metadata anchor turn
        initial_history = [{"role": "system", "content": "Session data wiped. Timeline reset."}]
        initial_lore = {}  # Completely flush lore nodes

        self.db.save_session_history(self.memory.active_filename, initial_history)
        self.db.save_session_lore(self.memory.active_filename, initial_lore)

        # Update memory states
        self.memory.set_active_session(self.memory.active_filename, initial_history, initial_lore)

        # Redraw layout views
        self.on_session_loaded()
        self.app.append_system_msg("Active session chatlogs and lorebook flushed. Application global configuration kept.")

    def on_close_save_routine(self):
        print("Closing application. Saving settings map...")
        current_ui_state = self.app.get_current_ui_settings()
        current_ui_state["active_user"] = self.active_user_name
        self.db.save_settings(current_ui_state)
        self.app.destroy()

    def delete_last_message(self):
        """Deletes the absolute last message (from screen and file) to step back in time."""
        if not self.memory.active_turns:
            self.app.append_system_msg("No messages left to delete.")
            return

        # Pop the last turn
        removed_turn = self.memory.active_turns.pop()
        role = removed_turn.get("role", "system")
        content_preview = removed_turn.get("content", "")[:30]

        # Reset reroll status since the timeline has altered
        self.reroll_cache = []
        self.reroll_index = -1

        # Commit deletion to persistent storage immediately
        self.db.save_session_history(self.memory.active_filename, self.memory.active_turns)

        # Redraw screen directly from active memory state
        self.render_active_memory_to_ui()
        self.app.append_system_msg(f"Deleted last {role} message: '{content_preview}...'")

    def on_settings_saved(self):
        """Persist current settings from the Settings tab without closing the app."""
        current_ui_state = self.app.get_current_ui_settings()
        current_ui_state["active_user"] = self.active_user_name
        self.db.save_settings(current_ui_state)
        self.global_settings = current_ui_state

        # Sync state and redraw active memory immediately
        self.app.show_avatars = current_ui_state.get("show_avatars", True)
        self.render_active_memory_to_ui()

        self.app.append_system_msg("Settings saved successfully.")



if __name__ == "__main__":
    orchestrator = RoleplayOrchestrator()
    orchestrator.app.mainloop()
