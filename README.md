# MY LAB — YOUTUBE EDITION

A desktop-based media downloading workspace built with Python. Designed with a modern dark interface, MY LAB combines video previews, download customization, queue management and download history into one application.

## Overview

**MY LAB — YOUTUBE EDITION** is a Python desktop application that allows users to fetch video information, configure download preferences and manage video or audio downloads through a dedicated graphical interface.

Built using CustomTkinter and yt-dlp, the application focuses on a clean user experience with a structured workspace and persistent settings.

## Features

- **Modern GUI:** Dark-themed interface with a custom color palette and typography.
- **Video Information:** Fetch video titles, channel details, duration, view count and thumbnails.
- **Multiple Formats:** Download videos in MP4 or extract audio in MP3.
- **Quality Selection:** Choose from 360p, 480p, 720p, 1080p, 1440p, 2160p or best available.
- **Subtitle Support:** Option to download English subtitles.
- **Queue Manager:** Add multiple videos and process them sequentially.
- **Download Progress:** Monitor download percentage, speed and estimated time remaining.
- **Download History:** Keep track of previously completed downloads.
- **Custom Download Location:** Choose where downloaded media is stored.
- **Persistent Settings:** Save preferences using JSON-based storage.
- **Quick Download:** Start the download workflow directly from the dashboard.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| CustomTkinter | Desktop GUI |
| yt-dlp | Media information and downloading |
| Pillow (PIL) | Thumbnail image processing |
| Threading | Background download operations |
| JSON | Settings and download history |
| Tkinter | File dialogs and message boxes |

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/USERNAME/REPOSITORY.git
```

### 2. Install dependencies

```bash
pip install customtkinter pillow yt-dlp
```

### 3. Install FFmpeg

FFmpeg is required for audio extraction and certain video merging operations.

Download it from:
https://ffmpeg.org/download.html

Make sure FFmpeg is accessible through your system PATH.

### 4. Run the application

Open the Python file in Python IDLE or your preferred Python IDE and run the module.

## Application Sections

| Section | Description |
|---|---|
| Dashboard | Download statistics, quick download and recent activity |
| New Download | Video URL, preview and download configuration |
| Queue Manager | Manage pending downloads and monitor progress |
| History | View completed download records |
| Settings | Configure download directory and preferences |

## Storage

The application automatically creates its data directory inside the user's Downloads folder:

```text
Downloads/
└── MY LAB YouTube Edition/
    ├── history.json
    └── settings.json
```

Downloaded media is saved to the selected download directory.

## Design

The interface uses a Midnight Navy-inspired theme with violet and cyan accents.

- Midnight Navy
- Violet
- Cyan
- Ivory
- Coral

The application also supports custom font selection when preferred fonts are installed on the system.

## Future Improvements

- Pause and resume downloads.
- Download cancellation controls.
- Improved playlist management.
- Download speed optimization.
- Batch URL importing.
- More detailed download analytics.
- Application packaging into a standalone Windows executable.

## Disclaimer

This project is intended for educational and personal use.

Users are responsible for complying with applicable copyright laws, platform terms of service and content ownership requirements. Only download content you have permission to access and save.

## Author

**Prateesraj K**

Electronics and Communication Engineering Student  
Interested in Python, software development, automation and hardware-software projects.

GitHub: [@prateesraj](https://github.com/prateesraj)

---

*Built with Python. Designed as MY LAB.*
