import json, sys
from faster_whisper import WhisperModel
audio, out = sys.argv[1], sys.argv[2]
m = WhisperModel("small", device="cpu", compute_type="int8")
import subprocess, numpy as np
pcm = subprocess.run(["ffmpeg","-v","error","-i",audio,"-f","s16le","-ac","1","-ar","16000","-"],capture_output=True,check=True).stdout
audio_np = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
segs, _ = m.transcribe(audio_np, language="pt", word_timestamps=True, beam_size=5)
words = [{"w": w.word.strip(), "ini": round(w.start, 3), "fim": round(w.end, 3)} for s in segs for w in s.words]
json.dump(words, open(out, "w"), ensure_ascii=False, indent=1)
print(" ".join(f'{x["w"]}@{x["ini"]}' for x in words))
