import os
import random
import subprocess
import pygame
import time

import requests

# Define constants
SONGS_FOLDER = "songs"
DOWNLOADS_FOLDER = "downloads"
LANGUAGE_FILES = {
    "ro-RO": "romanian.txt",
    "en-US": "english.txt",
    "fr-FR": "french.txt"
}

# Function to select a random song URL from a language file
def select_random_song(language):
    if language not in LANGUAGE_FILES:
        raise ValueError(f"Unsupported language: {language}")

    filepath = os.path.join(SONGS_FOLDER, LANGUAGE_FILES[language])
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Language file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as file:
        links = [line.strip() for line in file if line.strip()]

    if not links:
        raise ValueError(f"No links found in file: {filepath}")

    return random.choice(links)

# Function to download a YouTube video as an MP3 using yt-dlp
def download_song_from_youtube(url):
    if not os.path.exists(DOWNLOADS_FOLDER):
        os.makedirs(DOWNLOADS_FOLDER)

    output_path = os.path.join(DOWNLOADS_FOLDER, "%(title)s.%(ext)s")
    try:
        command = [
            "yt-dlp",
            "--extract-audio",
            "--audio-format", "mp3",
            "--output", output_path,
            url,
        ]
        subprocess.run(command, check=True)
        # Return the first MP3 file in the downloads folder
        for file in os.listdir(DOWNLOADS_FOLDER):
            if file.endswith(".mp3"):
                return os.path.join(DOWNLOADS_FOLDER, file)
        raise FileNotFoundError("No MP3 file found in the downloads folder.")
    except subprocess.CalledProcessError as e:
        print(f"yt-dlp error: {e}")
        raise Exception("Failed to download the video using yt-dlp.")

# Function to play the downloaded audio file with gradual volume increase
def play_audio_with_fade_in(file_path, fade_duration=5):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.set_volume(0)  # Start with volume 0
    pygame.mixer.music.play()

    # Gradually increase the volume
    for step in range(1, fade_duration * 10 + 1):  # Increment over fade_duration seconds
        volume = step / (fade_duration * 10)  # Scale volume linearly
        pygame.mixer.music.set_volume(volume)
        time.sleep(0.5)  # Wait for 100ms between steps

    # Play the rest of the song at full volume
    while pygame.mixer.music.get_busy():
        time.sleep(1)
    pygame.mixer.quit()

# Main function for testing
if __name__ == "__main__":
    test_language = "ro-RO"
    response = requests.get('http://localhost:5000/api/get-language')
    if response.status_code == 200:
        data = response.json()
        test_language = data.get("azure_voice");
    try:
        print(f"Selecting a random song for language: {test_language}...")
        song_url = select_random_song(test_language)
        print(f"Selected song URL: {song_url}")

        print("Downloading the song...")
        downloaded_file = download_song_from_youtube(song_url)
        print(f"Downloaded file: {downloaded_file}")

        print("Playing the downloaded audio with fade-in effect...")
        play_audio_with_fade_in(downloaded_file, fade_duration=5)
        print("Playback finished.")
    except Exception as e:
        print(f"Error: {e}")
