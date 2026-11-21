
import customtkinter as ctk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox
from PIL import Image
from io import BytesIO
from datetime import datetime
import yt_dlp
import threading
import urllib.request
import json
import os
import time


# ==========================================================
# MY LAB - YOUTUBE EDITION
# ==========================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


# ---------------- COLORS ----------------

BG = "#10131C"
SIDEBAR = "#141824"
PANEL = "#1A2030"
CARD = "#202638"
CARD_HOVER = "#293249"

VIOLET = "#8B7CFF"
VIOLET_HOVER = "#A397FF"

CYAN = "#54C8D8"
CYAN_HOVER = "#75DCE8"

IVORY = "#F0F1F6"
MUTED = "#A9B4CC"
GREY = "#68738A"

CORAL = "#E68C83"
GREEN = "#64D6A0"
RED = "#EF7474"

BORDER = "#30384A"
INPUT = "#181E2B"


# ---------------- FONT SYSTEM ----------------

def get_font(preferred, installed, fallback="Segoe UI"):
    lookup = {name.lower(): name for name in installed}

    for name in preferred:
        if name.lower() in lookup:
            return lookup[name.lower()]

    return fallback


# ---------------- DATA STORAGE ----------------

APP_DIR = os.path.join(
    os.path.expanduser("~"),
    "Downloads",
    "MY LAB YouTube Edition"
)

os.makedirs(APP_DIR, exist_ok=True)

HISTORY_FILE = os.path.join(APP_DIR, "history.json")
SETTINGS_FILE = os.path.join(APP_DIR, "settings.json")

DEFAULT_SETTINGS = {
    "folder": os.path.join(
        os.path.expanduser("~"), "Downloads"
    ),
    "format": "MP4 Video",
    "quality": "1080p",
    "subtitles": False,
    "playlist": False
}


def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as error:
        print("Save error:", error)


# ==========================================================
# APPLICATION
# ==========================================================

class MyLab(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("MY LAB | YOUTUBE EDITION")
        self.geometry("1280x850")
        self.minsize(1000, 680)
        self.configure(fg_color=BG)

        installed_fonts = tkfont.families(root=self)

        global FONT_BRAND, FONT_TITLE
        global FONT_SECTION, FONT_BODY, FONT_MONO

        FONT_BRAND = get_font(
            ["Newblack", "New Black"],
            installed_fonts
        )

        FONT_TITLE = get_font(
            ["Monigue"],
            installed_fonts
        )

        FONT_SECTION = get_font(
            ["Gothif"],
            installed_fonts
        )

        FONT_BODY = get_font(
            ["Segoe UI", "Arial"],
            installed_fonts
        )

        FONT_MONO = get_font(
            ["Consolas", "Courier New"],
            installed_fonts
        )

        self.settings = load_json(
            SETTINGS_FILE,
            DEFAULT_SETTINGS.copy()
        )

        self.history = load_json(
            HISTORY_FILE,
            []
        )

        self.queue = []

        self.current_info = None
        self.thumbnail_image = None

        self.downloading = False
        self.fetching = False
        self.active_title = ""

        self.folder = ctk.StringVar(
            value=self.settings.get(
                "folder",
                DEFAULT_SETTINGS["folder"]
            )
        )

        self.format_var = ctk.StringVar(
            value=self.settings.get("format", "MP4 Video")
        )

        self.quality_var = ctk.StringVar(
            value=self.settings.get("quality", "1080p")
        )

        self.subtitle_var = ctk.BooleanVar(
            value=self.settings.get("subtitles", False)
        )

        self.playlist_var = ctk.BooleanVar(
            value=self.settings.get("playlist", False)
        )

        self.build_layout()
        self.show_page("Dashboard")

    # ======================================================
    # BASE LAYOUT
    # ======================================================

    def build_layout(self):

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # SIDEBAR

        self.sidebar = ctk.CTkFrame(
            self,
            width=225,
            fg_color=SIDEBAR,
            corner_radius=0
        )

        self.sidebar.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.sidebar.grid_propagate(False)

        ctk.CTkLabel(
            self.sidebar,
            text="MY LAB",
            font=(FONT_BRAND, 31, "bold"),
            text_color=IVORY
        ).pack(
            anchor="w",
            padx=23,
            pady=(32, 0)
        )

        ctk.CTkLabel(
            self.sidebar,
            text="YOUTUBE EDITION",
            font=(FONT_MONO, 10, "bold"),
            text_color=VIOLET
        ).pack(
            anchor="w",
            padx=26,
            pady=(4, 28)
        )

        self.sidebar_line()

        ctk.CTkLabel(
            self.sidebar,
            text="WORKSPACE",
            font=(FONT_MONO, 9, "bold"),
            text_color=GREY
        ).pack(
            anchor="w",
            padx=22,
            pady=(22, 10)
        )

        self.nav_buttons = {}

        navigation = [
            ("Dashboard", "01"),
            ("New Download", "02"),
            ("Queue Manager", "03"),
            ("History", "04"),
            ("Settings", "05")
        ]

        for name, number in navigation:

            btn = ctk.CTkButton(
                self.sidebar,
                text=f"{number}     {name}",
                height=46,
                corner_radius=8,
                anchor="w",
                fg_color="transparent",
                hover_color=CARD_HOVER,
                text_color=MUTED,
                font=(FONT_BODY, 12),
                command=lambda n=name: self.show_page(n)
            )

            btn.pack(
                fill="x",
                padx=12,
                pady=4
            )

            self.nav_buttons[name] = btn

        spacer = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )

        spacer.pack(fill="both", expand=True)

        self.sidebar_line()

        ctk.CTkLabel(
            self.sidebar,
            text="PERSONAL MEDIA WORKSPACE",
            font=(FONT_MONO, 8),
            text_color=GREY
        ).pack(
            anchor="w",
            padx=20,
            pady=(15, 5)
        )

        ctk.CTkLabel(
            self.sidebar,
            text="VERSION 2.0",
            font=(FONT_MONO, 10, "bold"),
            text_color=CYAN
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 24)
        )

        # MAIN CONTAINER

        self.main = ctk.CTkFrame(
            self,
            fg_color=BG,
            corner_radius=0
        )

        self.main.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        self.main.grid_rowconfigure(1, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        # TOP HEADER

        self.header = ctk.CTkFrame(
            self.main,
            height=80,
            fg_color=BG,
            corner_radius=0
        )

        self.header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=27,
            pady=(12, 0)
        )

        self.header.grid_propagate(False)

        self.page_title = ctk.CTkLabel(
            self.header,
            text="Dashboard",
            font=(FONT_TITLE, 27, "bold"),
            text_color=IVORY
        )

        self.page_title.pack(
            side="left",
            anchor="center"
        )

        self.system_status = ctk.CTkLabel(
            self.header,
            text="SYSTEM READY",
            font=(FONT_MONO, 9, "bold"),
            text_color=GREEN
        )

        self.system_status.pack(
            side="right",
            anchor="center"
        )

        # PAGE AREA

        self.page_area = ctk.CTkFrame(
            self.main,
            fg_color=BG,
            corner_radius=0
        )

        self.page_area.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=27,
            pady=(0, 20)
        )

        self.page_area.grid_rowconfigure(0, weight=1)
        self.page_area.grid_columnconfigure(0, weight=1)

    def sidebar_line(self):

        ctk.CTkFrame(
            self.sidebar,
            height=1,
            fg_color=BORDER
        ).pack(
            fill="x",
            padx=20,
            pady=7
        )

    # ======================================================
    # REUSABLE UI COMPONENTS
    # ======================================================

    def clear_page(self):

        for widget in self.page_area.winfo_children():
            widget.destroy()

    def scroll_page(self):

        scroll = ctk.CTkScrollableFrame(
            self.page_area,
            fg_color=BG,
            corner_radius=0,
            scrollbar_button_color=GREY,
            scrollbar_button_hover_color=VIOLET
        )

        scroll.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        return scroll

    def section(self, parent, title, subtitle=None):

        block = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )

        block.pack(
            fill="x",
            pady=(17, 9)
        )

        ctk.CTkLabel(
            block,
            text=title,
            font=(FONT_SECTION, 16, "bold"),
            text_color=IVORY
        ).pack(anchor="w")

        if subtitle:
            ctk.CTkLabel(
                block,
                text=subtitle,
                font=(FONT_BODY, 10),
                text_color=MUTED
            ).pack(
                anchor="w",
                pady=(3, 0)
            )

    def card(self, parent, color=CARD):

        return ctk.CTkFrame(
            parent,
            fg_color=color,
            corner_radius=12,
            border_width=1,
            border_color=BORDER
        )

    def action_button(
        self,
        parent,
        text,
        command,
        color=VIOLET,
        hover=VIOLET_HOVER,
        text_color=IVORY,
        height=44
    ):

        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            height=height,
            corner_radius=8,
            fg_color=color,
            hover_color=hover,
            text_color=text_color,
            font=(FONT_BODY, 11, "bold")
        )

    def show_page(self, name):

        self.clear_page()

        for nav_name, btn in self.nav_buttons.items():

            if nav_name == name:
                btn.configure(
                    fg_color="#302B4C",
                    text_color=IVORY
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=MUTED
                )

        self.page_title.configure(text=name)

        if name == "Dashboard":
            self.dashboard_page()

        elif name == "New Download":
            self.download_page()

        elif name == "Queue Manager":
            self.queue_page()

        elif name == "History":
            self.history_page()

        elif name == "Settings":
            self.settings_page()

    # ======================================================
    # DASHBOARD
    # ======================================================

    def dashboard_page(self):

        page = self.scroll_page()

        self.section(
            page,
            "YOUR MEDIA WORKSPACE",
            "Manage your video downloads in one place."
        )

        # STATISTICS

        stats = ctk.CTkFrame(
            page,
            fg_color="transparent"
        )

        stats.pack(fill="x", pady=5)

        stats.grid_columnconfigure(
            (0, 1, 2),
            weight=1
        )

        values = [
            ("TOTAL DOWNLOADS", len(self.history), VIOLET),
            ("COMPLETED", len(self.history), GREEN),
            ("IN QUEUE", len(self.queue), CYAN)
        ]

        for i, (title, value, accent) in enumerate(values):

            box = self.card(stats)

            box.grid(
                row=0,
                column=i,
                sticky="ew",
                padx=5
            )

            ctk.CTkLabel(
                box,
                text=title,
                font=(FONT_MONO, 9, "bold"),
                text_color=accent
            ).pack(
                anchor="w",
                padx=15,
                pady=(15, 5)
            )

            ctk.CTkLabel(
                box,
                text=str(value),
                font=(FONT_TITLE, 27, "bold"),
                text_color=IVORY
            ).pack(
                anchor="w",
                padx=15
            )

            ctk.CTkLabel(
                box,
                text="MY LAB LIBRARY",
                font=(FONT_BODY, 9),
                text_color=GREY
            ).pack(
                anchor="w",
                padx=15,
                pady=(3, 14)
            )

        # QUICK DOWNLOAD

        self.section(
            page,
            "QUICK DOWNLOAD",
            "Paste a video link to begin."
        )

        quick = self.card(page)
        quick.pack(fill="x", pady=5)

        ctk.CTkLabel(
            quick,
            text="VIDEO SOURCE",
            font=(FONT_MONO, 9, "bold"),
            text_color=CYAN
        ).pack(
            anchor="w",
            padx=17,
            pady=(17, 7)
        )

        self.quick_url = ctk.CTkEntry(
            quick,
            height=46,
            placeholder_text="Paste your YouTube URL...",
            fg_color=INPUT,
            border_color=BORDER,
            text_color=IVORY,
            font=(FONT_BODY, 11)
        )

        self.quick_url.pack(
            fill="x",
            padx=17,
            pady=(0, 12)
        )

        self.action_button(
            quick,
            "OPEN VIDEO STUDIO",
            self.open_quick_download,
            color=VIOLET
        ).pack(
            fill="x",
            padx=17,
            pady=(0, 17)
        )

        # RECENT HISTORY

        self.section(page, "RECENT ACTIVITY")

        recent = self.card(page)
        recent.pack(fill="x", pady=(0, 20))

        self.recent_box = ctk.CTkTextbox(
            recent,
            height=170,
            fg_color="transparent",
            text_color=IVORY,
            font=(FONT_BODY, 10),
            border_width=0
        )

        self.recent_box.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=10
        )

        self.refresh_recent()

    def refresh_recent(self):

        if not hasattr(self, "recent_box"):
            return

        self.recent_box.configure(state="normal")
        self.recent_box.delete("1.0", "end")

        if not self.history:

            self.recent_box.insert(
                "end",
                "\n  No downloads yet."
            )

        else:

            for item in self.history[:8]:

                self.recent_box.insert(
                    "end",
                    f"\n  {item.get('title', 'Unknown')}\n"
                    f"  {item.get('format', '')} | "
                    f"{item.get('date', '')}\n"
                )

        self.recent_box.configure(state="disabled")

    def open_quick_download(self):

        url = self.quick_url.get().strip()

        if not url:
            messagebox.showwarning(
                "URL required",
                "Paste a video URL first."
            )
            return

        self.show_page("New Download")
        self.url_entry.insert(0, url)

    # ======================================================
    # DOWNLOAD STUDIO
    # ======================================================

    def download_page(self):

        page = self.scroll_page()

        self.section(
            page,
            "VIDEO STUDIO",
            "Preview, configure and download your selected video."
        )

        # URL INPUT

        source = self.card(page)
        source.pack(fill="x", pady=5)

        ctk.CTkLabel(
            source,
            text="VIDEO URL",
            font=(FONT_MONO, 9, "bold"),
            text_color=CYAN
        ).pack(
            anchor="w",
            padx=15,
            pady=(15, 7)
        )

        self.url_entry = ctk.CTkEntry(
            source,
            height=45,
            placeholder_text="https://www.youtube.com/watch?v=...",
            fg_color=INPUT,
            border_color=BORDER,
            font=(FONT_BODY, 11)
        )

        self.url_entry.pack(
            fill="x",
            padx=15,
            pady=(0, 10)
        )

        self.action_button(
            source,
            "FETCH VIDEO DETAILS",
            self.fetch_video,
            color=CARD_HOVER,
            hover=BORDER
        ).pack(
            anchor="e",
            padx=15,
            pady=(0, 15)
        )

        # TWO COLUMN LAYOUT

        columns = ctk.CTkFrame(
            page,
            fg_color="transparent"
        )

        columns.pack(fill="x", pady=10)

        columns.grid_columnconfigure(0, weight=3)
        columns.grid_columnconfigure(1, weight=2)

        # LEFT VIDEO PREVIEW

        preview_card = self.card(columns)

        preview_card.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 7)
        )

        ctk.CTkLabel(
            preview_card,
            text="01 / VIDEO PREVIEW",
            font=(FONT_MONO, 9, "bold"),
            text_color=VIOLET
        ).pack(
            anchor="w",
            padx=15,
            pady=(15, 10)
        )

        self.thumbnail_label = ctk.CTkLabel(
            preview_card,
            text="VIDEO PREVIEW",
            fg_color="#111522",
            text_color=GREY,
            font=(FONT_MONO, 10),
            height=195
        )

        self.thumbnail_label.pack(
            fill="x",
            padx=12,
            pady=5
        )

        self.video_title = ctk.CTkLabel(
            preview_card,
            text="Your video title will appear here",
            font=(FONT_TITLE, 18, "bold"),
            text_color=IVORY,
            wraplength=460,
            justify="left"
        )

        self.video_title.pack(
            anchor="w",
            padx=15,
            pady=(12, 5)
        )

        self.video_details = ctk.CTkLabel(
            preview_card,
            text="Channel information\nDuration and views",
            font=(FONT_BODY, 10),
            text_color=MUTED,
            justify="left"
        )

        self.video_details.pack(
            anchor="w",
            padx=15,
            pady=(0, 17)
        )

        # RIGHT CONFIGURATION

        config = self.card(columns)

        config.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(7, 0)
        )

        ctk.CTkLabel(
            config,
            text="02 / CONFIGURATION",
            font=(FONT_MONO, 9, "bold"),
            text_color=CYAN
        ).pack(
            anchor="w",
            padx=15,
            pady=(15, 15)
        )

        ctk.CTkLabel(
            config,
            text="FORMAT",
            font=(FONT_MONO, 9, "bold"),
            text_color=MUTED
        ).pack(anchor="w", padx=15)

        ctk.CTkOptionMenu(
            config,
            variable=self.format_var,
            values=["MP4 Video", "MP3 Audio"],
            fg_color=INPUT,
            button_color=VIOLET,
            button_hover_color=VIOLET_HOVER,
            text_color=IVORY
        ).pack(
            fill="x",
            padx=15,
            pady=(6, 17)
        )

        ctk.CTkLabel(
            config,
            text="QUALITY",
            font=(FONT_MONO, 9, "bold"),
            text_color=MUTED
        ).pack(anchor="w", padx=15)

        ctk.CTkOptionMenu(
            config,
            variable=self.quality_var,
            values=[
                "Best Available",
                "2160p",
                "1440p",
                "1080p",
                "720p",
                "480p",
                "360p"
            ],
            fg_color=INPUT,
            button_color=CYAN,
            button_hover_color=CYAN_HOVER,
            text_color=IVORY
        ).pack(
            fill="x",
            padx=15,
            pady=(6, 17)
        )

        ctk.CTkCheckBox(
            config,
            text="English subtitles",
            variable=self.subtitle_var,
            fg_color=VIOLET,
            hover_color=VIOLET_HOVER,
            text_color=IVORY,
            font=(FONT_BODY, 10)
        ).pack(
            anchor="w",
            padx=15,
            pady=8
        )

        ctk.CTkCheckBox(
            config,
            text="Allow playlist",
            variable=self.playlist_var,
            fg_color=CYAN,
            hover_color=CYAN_HOVER,
            text_color=IVORY,
            font=(FONT_BODY, 10)
        ).pack(
            anchor="w",
            padx=15,
            pady=8
        )

        # SAVE LOCATION

        self.section(page, "03 / SAVE LOCATION")

        location = self.card(page)
        location.pack(fill="x", pady=5)

        row = ctk.CTkFrame(
            location,
            fg_color="transparent"
        )

        row.pack(
            fill="x",
            padx=13,
            pady=13
        )

        ctk.CTkEntry(
            row,
            textvariable=self.folder,
            height=42,
            fg_color=INPUT,
            border_color=BORDER,
            font=(FONT_MONO, 9)
        ).pack(
            side="left",
            fill="x",
            expand=True
        )

        ctk.CTkButton(
            row,
            text="BROWSE",
            width=95,
            height=42,
            fg_color=CARD_HOVER,
            hover_color=BORDER,
            text_color=IVORY,
            command=self.choose_folder
        ).pack(
            side="right",
            padx=(8, 0)
        )

        # DOWNLOAD BUTTONS

        self.section(
            page,
            "04 / DOWNLOAD ACTIONS",
            "Start immediately or add the video to your queue."
        )

        actions = ctk.CTkFrame(
            page,
            fg_color="transparent"
        )

        actions.pack(fill="x", pady=5)

        actions.grid_columnconfigure((0, 1), weight=1)

        self.action_button(
            actions,
            "DOWNLOAD NOW",
            self.download_now,
            color=VIOLET,
            hover=VIOLET_HOVER,
            height=50
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 6)
        )

        self.action_button(
            actions,
            "ADD TO QUEUE",
            self.add_to_queue,
            color="#27394C",
            hover="#36516C",
            height=50
        ).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(6, 0)
        )

        self.download_status = ctk.CTkLabel(
            page,
            text="READY",
            font=(FONT_MONO, 10, "bold"),
            text_color=GREEN
        )

        self.download_status.pack(
            anchor="w",
            pady=(12, 25)
        )

    # ======================================================
    # FETCH VIDEO DETAILS
    # ======================================================

    def fetch_video(self):

        url = self.url_entry.get().strip()

        if not url.startswith(("https://", "http://")):
            messagebox.showwarning(
                "Invalid URL",
                "Enter a valid video URL."
            )
            return

        if self.fetching:
            return

        self.fetching = True

        self.video_title.configure(
            text="Fetching video information..."
        )

        threading.Thread(
            target=self.fetch_worker,
            args=(url,),
            daemon=True
        ).start()

    def fetch_worker(self, url):

        try:

            options = {
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,
                "noplaylist": True
            }

            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(
                    url,
                    download=False
                )

            thumbnail = None

            if info.get("thumbnail"):

                try:

                    request = urllib.request.Request(
                        info["thumbnail"],
                        headers={"User-Agent": "Mozilla/5.0"}
                    )

                    with urllib.request.urlopen(
                        request,
                        timeout=20
                    ) as response:

                        thumbnail = Image.open(
                            BytesIO(response.read())
                        ).convert("RGB")

                except Exception:
                    pass

            self.after(
                0,
                lambda: self.display_video(info, thumbnail)
            )

        except Exception as error:

            self.after(
                0,
                lambda e=str(error): self.fetch_error(e)
            )

        finally:
            self.fetching = False

    def display_video(self, info, thumbnail):

        self.current_info = info

        self.video_title.configure(
            text=info.get("title", "Unknown video")
        )

        duration = info.get("duration")

        duration_text = (
            time.strftime("%H:%M:%S", time.gmtime(duration))
            if duration else "Unknown"
        )

        channel = info.get(
            "channel",
            info.get("uploader", "Unknown channel")
        )

        views = info.get("view_count")

        views_text = (
            f"{views:,} views"
            if views else "Views unavailable"
        )

        self.video_details.configure(
            text=(
                f"{channel}\n"
                f"Duration: {duration_text}\n"
                f"{views_text}"
            )
        )

        if thumbnail:

            thumbnail.thumbnail((700, 390))

            self.thumbnail_image = ctk.CTkImage(
                light_image=thumbnail,
                dark_image=thumbnail,
                size=thumbnail.size
            )

            self.thumbnail_label.configure(
                image=self.thumbnail_image,
                text=""
            )

        self.download_status.configure(
            text="VIDEO INFORMATION LOADED",
            text_color=GREEN
        )

    def fetch_error(self, error):

        self.video_title.configure(
            text="Unable to fetch video information"
        )

        self.download_status.configure(
            text="VIDEO INFORMATION ERROR",
            text_color=RED
        )

        messagebox.showerror(
            "Video information error",
            error[:1200]
        )

    # ======================================================
    # QUEUE
    # ======================================================

    def create_item(self):

        url = self.url_entry.get().strip()

        if not url.startswith(("https://", "http://")):
            messagebox.showwarning(
                "URL required",
                "Enter a valid video URL."
            )
            return None

        title = (
            self.current_info.get("title", "Video")
            if self.current_info else "Video"
        )

        return {
            "url": url,
            "title": title,
            "format": self.format_var.get(),
            "quality": self.quality_var.get(),
            "subtitles": self.subtitle_var.get(),
            "playlist": self.playlist_var.get(),
            "folder": self.folder.get()
        }

    def add_to_queue(self):

        item = self.create_item()

        if not item:
            return

        self.queue.append(item)

        self.download_status.configure(
            text="ADDED TO QUEUE",
            text_color=CYAN
        )

        messagebox.showinfo(
            "MY LAB",
            "Video added to the queue."
        )

    def download_now(self):

        item = self.create_item()

        if not item:
            return

        if self.downloading:

            messagebox.showwarning(
                "Download active",
                "A download is already running. Add this video to the queue."
            )

            return

        self.queue.append(item)

        self.show_page("Queue Manager")
        self.start_queue()

    # ======================================================
    # QUEUE PAGE
    # ======================================================

    def queue_page(self):

        page = self.scroll_page()

        self.section(
            page,
            "DOWNLOAD QUEUE",
            "Manage pending downloads and monitor progress."
        )

        self.queue_box = ctk.CTkTextbox(
            page,
            height=310,
            fg_color=CARD,
            text_color=IVORY,
            font=(FONT_MONO, 10),
            border_color=BORDER,
            border_width=1
        )

        self.queue_box.pack(fill="x", pady=10)

        self.section(page, "DOWNLOAD PROGRESS")

        self.queue_progress = ctk.CTkProgressBar(
            page,
            height=10,
            fg_color=CARD,
            progress_color=VIOLET
        )

        self.queue_progress.pack(fill="x", pady=8)
        self.queue_progress.set(0)

        self.progress_label = ctk.CTkLabel(
            page,
            text="READY",
            font=(FONT_MONO, 10, "bold"),
            text_color=CYAN
        )

        self.progress_label.pack(anchor="w", pady=5)

        self.speed_label = ctk.CTkLabel(
            page,
            text="Speed: -- MB/s     ETA: --",
            font=(FONT_MONO, 9),
            text_color=MUTED
        )

        self.speed_label.pack(anchor="w", pady=5)

        buttons = ctk.CTkFrame(
            page,
            fg_color="transparent"
        )

        buttons.pack(fill="x", pady=18)

        buttons.grid_columnconfigure((0, 1), weight=1)

        self.action_button(
            buttons,
            "START QUEUE",
            self.start_queue
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 5)
        )

        self.action_button(
            buttons,
            "CLEAR QUEUE",
            self.clear_queue,
            color="#3A2630",
            hover="#543440"
        ).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(5, 0)
        )

        self.refresh_queue()

    def refresh_queue(self):

        if not hasattr(self, "queue_box"):
            return

        self.queue_box.configure(state="normal")
        self.queue_box.delete("1.0", "end")

        if not self.queue:

            self.queue_box.insert(
                "end",
                "\n  YOUR QUEUE IS EMPTY\n\n"
                "  Add a video from the Video Studio."
            )

        else:

            for i, item in enumerate(self.queue, 1):

                self.queue_box.insert(
                    "end",
                    f"\n  {i:02d}  {item['title']}\n"
                    f"      {item['format']} | {item['quality']}\n"
                    f"      {item['url']}\n"
                    f"      SAVE: {item['folder']}\n"
                )

        self.queue_box.configure(state="disabled")

    def clear_queue(self):

        if self.downloading:
            messagebox.showwarning(
                "Download active",
                "Wait for the current download to finish."
            )
            return

        self.queue.clear()
        self.refresh_queue()

    # ======================================================
    # DOWNLOAD ENGINE
    # ======================================================

    def start_queue(self):

        if self.downloading:
            return

        if not self.queue:
            messagebox.showinfo(
                "Queue empty",
                "Add a video before starting."
            )
            return

        self.downloading = True

        self.system_status.configure(
            text="DOWNLOAD ACTIVE",
            text_color=VIOLET
        )

        threading.Thread(
            target=self.process_queue,
            daemon=True
        ).start()

    def process_queue(self):

        while self.queue:

            item = self.queue.pop(0)

            self.after(0, self.refresh_queue)

            self.after(
                0,
                lambda t=item["title"]: self.set_progress_text(
                    "DOWNLOADING: " + t[:55]
                )
            )

            try:

                self.download_item(item)

                record = {
                    "title": item["title"],
                    "url": item["url"],
                    "date": datetime.now().strftime(
                        "%d %b %Y - %I:%M %p"
                    ),
                    "format": item["format"],
                    "quality": item["quality"]
                }

                self.history.insert(0, record)
                save_json(HISTORY_FILE, self.history)

                self.after(
                    0,
                    lambda: self.set_progress_text(
                        "DOWNLOAD COMPLETED"
                    )
                )

            except Exception as error:

                self.after(
                    0,
                    lambda e=str(error): messagebox.showerror(
                        "Download failed",
                        e[:1200]
                    )
                )

        self.downloading = False

        self.after(
            0,
            lambda: self.system_status.configure(
                text="SYSTEM READY",
                text_color=GREEN
            )
        )

        self.after(
            0,
            lambda: self.set_progress_text("QUEUE COMPLETED")
        )

        self.after(0, self.refresh_queue)

    def download_item(self, item):

        folder = item["folder"]
        os.makedirs(folder, exist_ok=True)

        options = {
            "outtmpl": os.path.join(
                folder,
                "%(title)s.%(ext)s"
            ),
            "quiet": True,
            "no_warnings": True,
            "windowsfilenames": True,
            "noplaylist": not item["playlist"],
            "progress_hooks": [self.progress_hook]
        }

        if item["format"] == "MP3 Audio":

            options["format"] = "bestaudio/best"

            options["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192"
            }]

        else:

            quality = item["quality"]

            height_filter = ""

            if quality != "Best Available":
                height = int(quality.replace("p", ""))
                height_filter = f"[height<={height}]"

            # Prefer H.264 video + AAC audio.
            # Avoid Opus when selecting MP4 output.

            options["format"] = (
                f"bv*[ext=mp4][vcodec^=avc1]{height_filter}"
                f"+ba[ext=m4a][acodec^=mp4a]/"
                f"b[ext=mp4][vcodec^=avc1][acodec^=mp4a]"
            )

            options["merge_output_format"] = "mp4"

        if item["subtitles"]:

            options.update({
                "writesubtitles": True,
                "writeautomaticsub": True,
                "subtitleslangs": ["en"],
                "subtitlesformat": "srt"
            })

        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([item["url"]])

    def progress_hook(self, data):

        if data["status"] == "downloading":

            downloaded = data.get("downloaded_bytes", 0)

            total = (
                data.get("total_bytes")
                or data.get("total_bytes_estimate")
            )

            percent = downloaded / total if total else 0

            speed = data.get("speed")
            eta = data.get("eta")

            speed_text = (
                f"{speed / 1024 / 1024:.2f} MB/s"
                if speed else "-- MB/s"
            )

            eta_text = (
                f"{eta}s" if eta is not None else "Calculating"
            )

            self.after(
                0,
                lambda p=percent, s=speed_text, e=eta_text:
                self.update_progress(p, s, e)
            )

        elif data["status"] == "finished":

            self.after(
                0,
                lambda: self.set_progress_text(
                    "MERGING VIDEO AND AUDIO"
                )
            )

    def set_progress_text(self, text):

        if hasattr(self, "progress_label"):
            self.progress_label.configure(text=text)

    def update_progress(self, percent, speed, eta):

        if hasattr(self, "queue_progress"):
            self.queue_progress.set(
                max(0, min(1, percent))
            )

        if hasattr(self, "progress_label"):
            self.progress_label.configure(
                text=f"{percent * 100:.1f}% COMPLETE"
            )

        if hasattr(self, "speed_label"):
            self.speed_label.configure(
                text=f"Speed: {speed}     ETA: {eta}"
            )

    # ======================================================
    # HISTORY
    # ======================================================

    def history_page(self):

        page = self.scroll_page()

        self.section(
            page,
            "DOWNLOAD HISTORY",
            "Your completed video downloads."
        )

        box = self.card(page)
        box.pack(fill="x", pady=5)

        history_text = ctk.CTkTextbox(
            box,
            height=400,
            fg_color="transparent",
            text_color=IVORY,
            font=(FONT_BODY, 10),
            border_width=0
        )

        history_text.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=12
        )

        if not self.history:

            history_text.insert(
                "end",
                "\n  No downloads available yet."
            )

        else:

            for i, item in enumerate(self.history, 1):

                history_text.insert(
                    "end",
                    f"\n  {i:02d}  {item.get('title', 'Unknown')}\n"
                    f"      {item.get('format', '')} | "
                    f"{item.get('quality', '')}\n"
                    f"      {item.get('date', '')}\n"
                    f"      {item.get('url', '')}\n"
                )

        history_text.configure(state="disabled")

        self.action_button(
            page,
            "CLEAR HISTORY",
            self.clear_history,
            color="#3A2630",
            hover="#543440"
        ).pack(
            anchor="e",
            pady=12
        )

    def clear_history(self):

        if not messagebox.askyesno(
            "Clear history",
            "Delete all download history?"
        ):
            return

        self.history.clear()
        save_json(HISTORY_FILE, self.history)
        self.show_page("History")

    # ======================================================
    # SETTINGS
    # ======================================================

    def choose_folder(self):

        folder = filedialog.askdirectory(
            initialdir=self.folder.get()
        )

        if folder:
            self.folder.set(folder)

    def settings_page(self):

        page = self.scroll_page()

        self.section(
            page,
            "APPLICATION SETTINGS",
            "Manage your workspace and download preferences."
        )

        settings_card = self.card(page)
        settings_card.pack(fill="x", pady=5)

        ctk.CTkLabel(
            settings_card,
            text="DOWNLOAD DIRECTORY",
            font=(FONT_MONO, 9, "bold"),
            text_color=CYAN
        ).pack(
            anchor="w",
            padx=17,
            pady=(17, 8)
        )

        ctk.CTkEntry(
            settings_card,
            textvariable=self.folder,
            height=43,
            fg_color=INPUT,
            border_color=BORDER,
            font=(FONT_MONO, 10)
        ).pack(
            fill="x",
            padx=17
        )

        self.action_button(
            settings_card,
            "CHANGE LOCATION",
            self.choose_folder,
            color=CARD_HOVER,
            hover=BORDER
        ).pack(
            anchor="e",
            padx=17,
            pady=12
        )

        ctk.CTkFrame(
            settings_card,
            height=1,
            fg_color=BORDER
        ).pack(
            fill="x",
            padx=17,
            pady=8
        )

        ctk.CTkLabel(
            settings_card,
            text="APPLICATION IDENTITY",
            font=(FONT_MONO, 9, "bold"),
            text_color=VIOLET
        ).pack(
            anchor="w",
            padx=17,
            pady=(8, 5)
        )

        ctk.CTkLabel(
            settings_card,
            text="MY LAB — YOUTUBE EDITION",
            font=(FONT_TITLE, 20, "bold"),
            text_color=IVORY
        ).pack(
            anchor="w",
            padx=17,
            pady=(0, 5)
        )

        ctk.CTkLabel(
            settings_card,
            text="Midnight Navy / Violet / Cyan / Ivory / Coral",
            font=(FONT_BODY, 10),
            text_color=MUTED
        ).pack(
            anchor="w",
            padx=17,
            pady=(0, 18)
        )

        self.action_button(
            page,
            "SAVE SETTINGS",
            self.save_settings,
            color=VIOLET
        ).pack(
            fill="x",
            pady=15
        )

    def save_settings(self):

        self.settings = {
            "folder": self.folder.get(),
            "format": self.format_var.get(),
            "quality": self.quality_var.get(),
            "subtitles": self.subtitle_var.get(),
            "playlist": self.playlist_var.get()
        }

        save_json(SETTINGS_FILE, self.settings)

        messagebox.showinfo(
            "MY LAB",
            "Settings saved successfully."
        )


# ==========================================================
# START APPLICATION
# ==========================================================

if __name__ == "__main__":

    app = MyLab()
    app.mainloop()
