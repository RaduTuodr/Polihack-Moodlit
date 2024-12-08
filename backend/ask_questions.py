import os
import wave
import pyaudio
import pygame
import requests
import speech_recognition as sr
import html

class Siri:
    def __init__(self):
        LANGUAGE_VOICE_MAP = {
            "ro-RO": "ro-RO-AlinaNeural",
            "en-US": "en-US-JennyNeural",
            "fr-FR": "fr-FR-DeniseNeural"
         }
        self.language = "ro-RO"
        response = requests.get('http://localhost:5000/api/get-language')
        if response.status_code == 200:
            data = response.json()
            self.language = data.get("azure_voice")
        self.azure_voice = LANGUAGE_VOICE_MAP.get(self.language)

        self.p = pyaudio.PyAudio()
        self.recognizer = sr.Recognizer()
        self.speech_key = "Efh2rUhSSRqbMRJN2L3eMxvgrEdOfP42Jhb7YWj41m4md90PgYEQJQQJ99ALACPV0roXJ3w3AAAYACOGpKpl"  # Replace with your Azure Speech key
        self.service_region = "germanywestcentral"  # Replace with your Azure region

    def play_sound(self, file):
        pygame.mixer.init()
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.quit()

    def azure_tts(self, text, output_file):

        """Use Azure Text-to-Speech to generate speech."""
        endpoint = f"https://{self.service_region}.tts.speech.microsoft.com/cognitiveservices/v1"

        headers = {
            "Ocp-Apim-Subscription-Key": self.speech_key,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-24khz-160kbitrate-mono-mp3"
        }

        # SSML content for the voice synthesis
        ssml = f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{self.language}">
          <voice name="{self.azure_voice}">
            <prosody rate="0%" pitch="0%">
              {html.escape(text)}
            </prosody>
          </voice>
        </speak>
        """

        response = requests.post(endpoint, headers=headers, data=ssml.encode("utf-8"))
        if response.status_code == 200:
            with open(output_file, "wb") as audio_file:
                audio_file.write(response.content)
        else:
            raise Exception(f"Azure TTS Error: {response.status_code} - {response.text}")

    def speech_to_text(self, file):
        with sr.AudioFile(file) as source:
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.record(source)
        try:
            text = self.recognizer.recognize_google(audio, language=self.language)
            return text
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand the audio."
        except sr.RequestError as e:
            return f"Could not request results from Google Web Speech API; {e}"

    def write_file(self, question, audio_answer_file):
        with open("./text/answers.txt", "a", encoding="utf-8") as g:
            g.write(question + ": \n")
            g.write("     ")
            text_answer = self.speech_to_text(audio_answer_file)
            g.write(text_answer + "\n\n")

    def clean_file(self, file):
        with open(file, "w") as g:
            pass

    def record_audio(self):
        stream = self.p.open(format=pyaudio.paInt16,
                             channels=1,
                             rate=44100,
                             input=True,
                             frames_per_buffer=1024)
        print("Recording...")
        frames = []
        for i in range(0, int(44100 / 1024 * 5)):
            data = stream.read(1024)
            frames.append(data)
        print("Recording finished")
        stream.stop_stream()
        stream.close()
        with wave.open("./audio/output.wav", "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(frames))

    def run(self):
        questions_file = "./text/questions.txt"  # Replace with your questions file path
        with open(questions_file, "r", encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                question = line.strip()
                print(f"Asking: {question}")

                # Use Azure TTS to generate the question
                self.azure_tts(question, "./audio/questions.mp3")
                self.play_sound("./audio/questions.mp3")

                self.record_audio()
                self.write_file(question, "./audio/output.wav")

    def write_prompt(self):
        with open("./text/answers.txt", "w", encoding="utf-8") as file:
            file.write(
                "Bazat pe urmatoarele intrebari si raspunsuri, scrie-mi o poveste de adormit pentru copii care"
                + f" sa se potriveasca cu starea copilului in limba {self.language} \n"
            )
