import sys, json, subprocess, re, unicodedata, difflib, numpy as np
from faster_whisper import WhisperModel
texto = json.load(open(sys.argv[1]))["texto"][sys.argv[2]]
norm = lambda s: re.sub(r"[^a-z0-9 ]", "", "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")).split()
m = WhisperModel("small", device="cpu", compute_type="int8")
for f in sys.argv[3:]:
    pcm = subprocess.run(["ffmpeg","-v","error","-i",f,"-f","s16le","-ac","1","-ar","16000","-"],capture_output=True,check=True).stdout
    segs,_ = m.transcribe(np.frombuffer(pcm,np.int16).astype(np.float32)/32768, language="pt", beam_size=5)
    t = " ".join(s.text for s in segs); r = difflib.SequenceMatcher(None, norm(texto), norm(t)).ratio()
    print(f"{f.split('/')[-1]}: semelhança {r:.3f} | {t[:110]}")
