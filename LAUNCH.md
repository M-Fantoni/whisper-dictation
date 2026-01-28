# Whisper Dictation - Lancer l'application

Il y a plusieurs façons de lancer l'application sans passer par VS Code.

## 1. **Méthode simple : Double-clic (Windows)**

Crée un raccourci sur le bureau :
1. Clique droit sur `run.bat` → Envoyer vers → Bureau (créer un raccourci)
2. Double-clic sur le raccourci pour lancer l'app

**Raccourci clavier** : Alt+W pour démarrer/arrêter l'enregistrement

## 2. **Méthode PowerShell (Windows recommandé)**

Ouvre PowerShell et exécute :
```powershell
cd F:\src\whisper-dictation
.\run.ps1
```

Ou crée un raccourci clavier :
- Clique droit sur `run.ps1` → Propriétés
- **Raccourci** → Clique sur "Paramètres" 
- Attribue une touche de raccourci (ex: Ctrl+Alt+D)

## 3. **Invite de commande (Windows)**

Ouvre CMD et exécute :
```cmd
F:\src\whisper-dictation\run.bat
```

## 4. **Terminal PowerShell avancé (avec logs)**

Pour voir les logs en temps réel :
```powershell
cd F:\src\whisper-dictation
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = $pwd
python src/main.py -v
```

## Configuration

Avant de lancer, assure-toi que :

✅ `.env` est configuré correctement :
```env
TEXT_CLEANER_BACKEND=openai
OPENAI_API_KEY=sk-proj-...  # Ta clé API OpenAI
```

✅ Ollama est en arrière-plan (si tu l'utilises) :
```powershell
ollama serve
```

## Dépannage

**"ModuleNotFoundError: No module named 'X'"**
```powershell
cd F:\src\whisper-dictation
.venv\Scripts\pip install -r requirements.txt
```

**"OpenAI API key not found"**
- Ajoute ta clé API dans `.env`
- Redémarre l'app

**"Ollama not available"**
- Lance `ollama serve` dans un autre terminal
- Ou change `TEXT_CLEANER_BACKEND=disabled` dans `.env`

## Usage

1. Lance l'app avec un des scripts ci-dessus
2. Appuie sur **Alt+W** et parle (max 5 minutes)
3. Relâche **Alt+W** pour arrêter l'enregistrement
4. L'app transcrit, nettoie et colle le texte automatiquement

Profite ! 🚀
