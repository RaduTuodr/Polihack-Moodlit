import openai

from constants import OPENAI_APIKEY


def generate_story():
    if not OPENAI_APIKEY:
        raise ValueError("API key not found. Please make sure it is set in constants.py.")

    openai.api_key = OPENAI_APIKEY

    with open('./text/answers.txt', 'r', encoding='utf-8') as file:
        input_text = file.read()

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{
            "role": "user",
            "content": input_text + "\nScrie-mi o poveste de adormit"
        }],
        max_tokens=3000,
        temperature=0.9,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

    with open('./text/story.txt', 'w', encoding='utf-8') as file:
        file.write(response['choices'][0]['message']['content'].strip())


