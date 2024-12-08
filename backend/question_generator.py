import openai
import requests

from constants import OPENAI_APIKEY


def generate_questions():
    if not OPENAI_APIKEY:
        raise ValueError("API key not found. Please make sure it is set in constants.py.")

    openai.api_key = OPENAI_APIKEY

    language = "ro-RO"
    response = requests.get('http://localhost:5000/api/get-language')
    if response.status_code == 200:
        data = response.json()
        language = data.get("azure_voice");
    input_text = f"generate 4 random questions for a 10 year old kid in order to find out his mood. Try to also consider the date(eventual holiday) when making the questions. Put then on separate lines without numbering them. Also always add this question How was your day?. Use language {language}"

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{
            "role": "user",
            "content": input_text
        }],
        max_tokens=3000,
        temperature=0.9,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

    with open('./text/questions.txt', 'w', encoding='utf-8') as file:
        file.write(response['choices'][0]['message']['content'].strip())


