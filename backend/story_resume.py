import requests

def story_resume():
    language = "ro-RO"
    response = requests.get('http://localhost:5000/api/get-language')
    if response.status_code == 200:
        data = response.json()
        language = data.get("azure_voice")
    PHRASE_MAP = {
        "ro-RO": "Vrei să continui povestea de ieri?",
        "en-EN": "Do you want to continue the story from last night?",
        "fr-FR": "Voulez-vous continuer l'histoire d'hier soir ?"
    }
    phrase = PHRASE_MAP.get(language)
    with open("./text/questions.txt", "w", encoding = 'utf-8') as g:
        g.write(phrase)