import os
import shutil
import tempfile
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from flask import Flask, render_template, request, send_file, after_this_request
import yt_dlp

app = Flask(__name__)

def download_song(query, output_dir):
    # If the user pasted a direct URL (http/https), download it directly; otherwise search YouTube
    if query.startswith(('http://', 'https://')):
        search_query = query
    else:
        search_query = f"{query} official audio"

    ydl_opts = {
        'format': 'bestaudio/best',
        'default_search': 'ytsearch1',
        'noplaylist': True,
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'restrictfilenames': True,
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=True)
            if 'entries' in info and info['entries']:
                info = info['entries'][0]
            filename = ydl.prepare_filename(info)
            mp3_path = str(Path(filename).with_suffix('.mp3'))
            return mp3_path if os.path.exists(mp3_path) else None
    except Exception as e:
        print(f"Error downloading '{query}': {e}")
        return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    songs = request.form.getlist('song')
    artists = request.form.getlist('artist')

    song_list = []
    for song, artist in zip(songs, artists):
        song = song.strip()
        artist = artist.strip()
        if song:
            full_query = f"{artist} - {song}" if artist else song
            song_list.append(full_query)

    if not song_list:
        return "Please enter at least one song title.", 400

    temp_dir = tempfile.mkdtemp()

    @after_this_request
    def cleanup(response):
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"Cleanup error: {e}")
        return response

    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(lambda s: download_song(s, temp_dir), song_list))

    downloaded_files = [path for path in results if path is not None]

    if not downloaded_files:
        return "Could not download any of the requested songs.", 500

    if len(downloaded_files) == 1:
        return send_file(
            downloaded_files[0],
            as_attachment=True,
            download_name=os.path.basename(downloaded_files[0])
        )

    zip_path = os.path.join(temp_dir, 'songs_bundle.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in downloaded_files:
            zipf.write(file_path, arcname=os.path.basename(file_path))

    return send_file(
        zip_path,
        as_attachment=True,
        download_name='songs_bundle.zip'
    )

if __name__ == '__main__':
    app.run(debug=True)