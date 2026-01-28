import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import time

def check_microphone():
    print("=== Diagnostic Microphone ===")
    
    # 1. Lister les périphériques
    print("\nPériphériques d'entrée détectés :")
    devices = sd.query_devices()
    default_input = sd.default.device[0]
    
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            mark = "*" if i == default_input else " "
            print(f"[{mark}] ID {i}: {dev['name']} (Channels: {dev['max_input_channels']})")
    
    print(f"\nPériphérique par défaut utilisé : ID {default_input} ({devices[default_input]['name']})")
    
    # Log host API info
    dev_info = devices[default_input]
    print(f"Host API: {dev_info['hostapi']} (0=MME, 3=WASAPI sur Windows)")
    print(f"Default Sample Rate: {dev_info['default_samplerate']}")
    
    # 2. Test d'enregistrement
    duration = 5  # secondes
    fs = 16000
    print(f"\nEnregistrement de test de {duration} secondes...")
    print("PARLEZ MAINTENANT ! (A haute voix)")
    
    try:
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        
        # Barre de progression
        for i in range(duration):
            print(f".", end="", flush=True)
            time.sleep(1)
        
        sd.wait()
        print("\nEnregistrement terminé.")
        
        # 3. Analyse du signal
        # Convertir en float pour analyse
        data_float = recording.flatten().astype(np.float32) / 32768.0
        
        rms = np.sqrt(np.mean(data_float**2))
        peak = np.max(np.abs(data_float))
        db = 20 * np.log10(rms) if rms > 0 else -999
        
        print(f"\nRésultats d'analyse :")
        print(f"- Volume moyen (RMS) : {rms:.4f}")
        print(f"- Volume pic (Peak) : {peak:.4f}")
        print(f"- Niveau dB estimé : {db:.1f} dB")
        
        if peak == 0:
            print("\n❌ SILENCE ABSOLU DÉTECTÉ. Le micro n'envoie aucune donnée.")
        elif peak < 0.01:
            print("\n⚠️ NIVEAU TRÈS FAIBLE. Whisper aura du mal à entendre.")
        elif peak > 0.9:
            print("\n⚠️ SATURATION POSSIBLE. Vous parlez trop fort ou gain trop élevé.")
        else:
            print("\n✅ NIVEAU SIGNAL OK.")
            
        # 4. Sauvegarde
        filename = "tools/test_mic.wav"
        wav.write(filename, fs, recording)
        print(f"\nFichier audio sauvegardé : {filename}")
        print("Veuillez l'écouter avec votre lecteur audio pour vérifier la qualité.")
        
    except Exception as e:
        print(f"\n❌ ERREUR lors de l'enregistrement : {e}")    
    # 4. Test avec InputStream (comme dans l'app)
    print("\n=== Test avec InputStream (mode callback) ===")
    print("Enregistrement de 3 secondes...")
    print("PARLEZ MAINTENANT !")
    
    buffer = []
    
    def callback(indata, frames, time_info, status):
        if status:
            print(f"Status: {status}")
        peak = np.max(np.abs(indata))
        if peak > 10:
            print(f"Peak in callback: {peak}")
        buffer.append(indata.copy())
    
    try:
        stream = sd.InputStream(
            device=default_input,
            samplerate=fs,
            channels=1,
            dtype='int16',
            blocksize=4096,
            callback=callback
        )
        stream.start()
        time.sleep(3)
        stream.stop()
        stream.close()
        
        if buffer:
            recording2 = np.concatenate(buffer, axis=0)
            peak2 = np.max(np.abs(recording2.flatten().astype(np.float32) / 32768.0))
            print(f"InputStream Peak: {peak2:.4f}")
        else:
            print("❌ Aucune donnée dans le buffer InputStream")
    except Exception as e:
        print(f"❌ Erreur InputStream: {e}")
if __name__ == "__main__":
    check_microphone()
