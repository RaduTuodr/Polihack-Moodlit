from ask_questions import Siri
from story_generator import generate_story
from story_telling import generate_audio_with_rest
from question_generator import generate_questions

siri = Siri()
generate_questions()
siri.clean_file("./text/answers.txt")
siri.write_prompt()
siri.run()
generate_story()

input_text_file = "./text/story.txt"  # Replace with the path to your text file
output_audio_file = "./audio/english_story.mp3"

try:
    with open(input_text_file, "r", encoding="utf-8") as file:
        text = file.read()
    generate_audio_with_rest(text, output_audio_file)
except FileNotFoundError:
    print(f"Input file '{input_text_file}' not found.")

