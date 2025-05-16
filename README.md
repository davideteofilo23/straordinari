# App Straordinari

Applicazione Flask per la gestione delle ore di straordinario con invio PDF, login, firma digitale e Firebase.

## Deploy su Render

1. Crea un nuovo repository su GitHub
2. Carica tutti i file del progetto
3. Vai su https://render.com
4. Clicca "New Web Service" > "Deploy from GitHub"
5. Seleziona il repository
6. Imposta il build command su: `pip install -r requirements.txt`
7. Imposta start command su: `python app.py`
8. Aggiungi la variabile ambiente: `GOOGLE_APPLICATION_CREDENTIALS` con il contenuto di firebase_config.json

Enjoy!