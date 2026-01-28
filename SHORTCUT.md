# Whisper Dictation - Créer un raccourci de lancement

## 📌 Méthode 1 : Raccourci simple sur le bureau (recommandé)

### Option A : Avec le script VBScript (pas de console visible)

1. **Clique droit** sur `launch.vbs` dans l'explorateur
2. **Envoyer vers** → **Bureau (créer un raccourci)**
3. Renomme le raccourci en `Whisper Dictation`
4. **(Optionnel)** Change l'icône du raccourci :
   - Clique droit sur le raccourci → **Propriétés**
   - **Avancé** → Coche "Exécuter en tant que fenêtre réduite"

### Option B : Avec PowerShell (console visible mais nettoyable)

1. **Clique droit** sur `run.ps1` → **Envoyer vers** → **Bureau**
2. Renomme-le en `Whisper Dictation`

## 🚀 Utilisation

**Double-clic** sur le raccourci pour :
1. Lancer l'application silencieusement
2. Une petite fenêtre verte apparaît
3. Appuie sur **Alt+W** pour enregistrer
4. Relâche pour transcrire
5. Le texte nettoyé se colle dans ton clipboard

## ❌ Fermer l'application

Trois façons :
- **Clique** sur le bouton **"Fermer (Q)"** dans la fenêtre
- Appuie sur **Q**
- Appuie sur **Échap**

## ⚙️ Configuration avancée

### Cacher complètement la console avec raccourci

Si tu veux un raccourci qui cache totalement le terminal :

1. **Clique droit** sur le bureau → **Nouveau** → **Raccourci**
2. Localisation : `wscript.exe "F:\src\whisper-dictation\launch.vbs"`
3. Nom : `Whisper Dictation`
4. Clique sur le raccourci → **Propriétés**
5. **Avancé** → Coche **"Exécuter en tant que fenêtre réduite"**

Ou avec PowerShell (caché) :

Localisation : 
```
powershell.exe -WindowStyle Hidden -Command "cd 'F:\src\whisper-dictation'; .\run.ps1"
```

## 📝 Notes

- Le raccourci doit pointer vers le répertoire du projet (`F:\src\whisper-dictation`)
- Les variables d'environnement sont automatiquement configurées
- La clé API OpenAI est lue du fichier `.env`

Voilà ! C'est maintenant aussi simple qu'un double-clic ! 🎯
