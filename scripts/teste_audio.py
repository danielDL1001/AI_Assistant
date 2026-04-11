import pyttsx3

engine = pyttsx3.init()

engine.save_to_file("Olá, isso é um teste de áudio", "../audio/reference.wav")
engine.runAndWait()

print("Áudio gerado!")
