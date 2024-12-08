import os
from time import sleep

import requests
import subprocess




def generate_audio_with_rest(input_text, output_file):
    # Azure Speech Service configuration
    LANGUAGE_VOICE_MAP = {
      "ro-RO": "ro-RO-AlinaNeural",
      "en-US": "en-US-JennyNeural",
      "fr-FR": "fr-FR-DeniseNeural"
    }
    language = "ro-RO"
    response = requests.get('http://localhost:5000/api/get-language')
    if response.status_code == 200:
      data = response.json()
      language = data.get("azure_voice");
    voice = LANGUAGE_VOICE_MAP.get(language)
    speech_key = "Efh2rUhSSRqbMRJN2L3eMxvgrEdOfP42Jhb7YWj41m4md90PgYEQJQQJ99ALACPV0roXJ3w3AAAYACOGpKpl"  # Replace with your Azure key
    service_region = "germanywestcentral"  # Replace with your Azure region (e.g., eastus, germanywestcentral)
    endpoint = f"https://{service_region}.tts.speech.microsoft.com/cognitiveservices/v1"

    # Set headers for REST API request
    headers = {
        "Ocp-Apim-Subscription-Key": speech_key,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "audio-24khz-160kbitrate-mono-mp3"  # High-quality audio
    }

    # Define SSML for a warm male voice in English with a slower rate
    ssml = f"""
    <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
      <voice name="{voice}">
        <prosody rate="-15%" pitch="default">
          {input_text}
        </prosody>z
      </voice>
    </speak>
    """

    # Send POST request to Azure Speech API
    response = requests.post(endpoint, headers=headers, data=ssml.encode("utf-8"))

    if response.status_code == 200:
        # Save the audio content to a file
        with open(output_file, "wb") as audio_file:
            audio_file.write(response.content)
        print(f"Audio content saved to '{output_file}'")

        #print('ddd')
        #sleep(5)
    else:
        print(f"Error: {response.status_code}")
        print(f"Details: {response.text}")
