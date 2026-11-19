# Batch Song Downloader (v1)

A lightweight local web application built with **Python**, **Flask**, **yt-dlp**, and **FFmpeg** that searches for songs in batch, converts them to 192kbps MP3s in parallel, and bundles them into a downloadable ZIP archive.

## Features
- Batch input for up to 8 tracks with separate Song and Artist fields
- Supports both text search queries and direct media URLs
- Parallel audio extraction and MP3 conversion using multithreading
- Automatic single-MP3 or multi-track `.zip` packaging with auto-cleanup

## Setup & Run
1. Install **Python 3.10+** and **FFmpeg** (added to system PATH).
2. Create and activate a virtual environment:
   `python -m venv venv`
3. Install dependencies:
   `python -m pip install -r requirements.txt`
4. Start the server:
   `python app.py` and open `http://127.0.0.1:5000`