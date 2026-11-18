#!/usr/bin/env python3
"""linha_do_tempo.py — linha do tempo GLOBAL de um documentário feito em várias cenas.

Uso: python3 linha_do_tempo.py <pasta_do_projeto>

Espera:
  textos.json            {"ordem": [...], "texto": {cena: "..."}, "pausa_entre_cenas": 1.4}
  narracao/<cena>.mp3    uma narração por cena

Gera:
  narracao_total.wav     todas as narrações em sequência (48 kHz mono), com pausas fixas
  palavras.json          cada palavra com o início REFINADO em tempo global
  cenas.json             início/fim de cada cena (múltiplos exatos de 1 quadro), duração e nº de quadros

Por que refinar: o Whisper às vezes adianta ou atrasa o início da palavra em 50–200 ms.
O refino procura, perto do tempo do Whisper, o vale de energia da voz que antecede a palavra
(a respiração ou a consoante de ataque) e usa o fim desse vale como início real.
"""
import json, subprocess, sys
from pathlib import Path
import numpy as np

FPS = 30
SR = 48000
LEAD_IN = 1.0        # silêncio antes da primeira fala
ANTES_DA_FALA = 0.7  # a cena começa este tanto antes da sua primeira fala
CAUDA = 4.0          # depois da última fala (música final, recuo de câmera)

base = Path(sys.argv[1]).resolve()
T = json.loads((base / "textos.json").read_text(encoding="utf-8"))
ordem, pausa = T["ordem"], float(T.get("pausa_entre_cenas", 1.4))

def ler(arq):
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(arq), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(pcm, np.float32).copy()

def env_db(x, passo=0.01):
    n = int(SR * passo); k = len(x) // n
    r = np.sqrt(np.mean(x[:k * n].reshape(k, n) ** 2, axis=1) + 1e-12)
    return 20 * np.log10(r)

def aparar(x, limiar=-45, margem=0.12):
    e = env_db(x); ativo = np.where(e > limiar)[0]
    a = max(0, int((ativo[0] * 0.01 - margem) * SR)); b = min(len(x), int((ativo[-1] * 0.01 + 0.01 + margem) * SR))
    return x[a:b]

quadro = lambda t: round(t * FPS) / FPS

# 1) narração total
pedacos, inicio_audio, t = [], {}, LEAD_IN
total = [np.zeros(int(LEAD_IN * SR), np.float32)]
provisorias = []
for c in ordem:
    arq = base / "narracao" / f"{c}.mp3"
    if arq.exists():
        x = aparar(ler(arq))
    else:   # ainda sem narração: silêncio com a duração provisória do plano (a cena usa t_prov)
        plano = json.loads((base / "cenas" / c / "plano.json").read_text(encoding="utf-8"))
        x = np.zeros(int((plano.get("dur_prov", 30) - ANTES_DA_FALA - pausa + 0.7) * SR), np.float32); provisorias.append(c)
    t = quadro(t)                       # cada narração começa num quadro exato
    inicio_audio[c] = t
    falta = int(round(t * SR)) - sum(len(p) for p in total)
    if falta > 0: total.append(np.zeros(falta, np.float32))
    total.append(x); pedacos.append((c, x))
    t += len(x) / SR + pausa
tot = np.concatenate(total)
fim_fala = len(tot) / SR
tot = np.concatenate([tot, np.zeros(int(CAUDA * SR), np.float32)])
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ac", "1", "-ar", str(SR), "-i", "-",
                str(base / "narracao_total.wav")], input=tot.tobytes(), check=True)

# 2) limites das cenas
lim = [0.0] + [quadro(inicio_audio[c] - ANTES_DA_FALA) for c in ordem[1:]] + [quadro(fim_fala + CAUDA)]
cenas = {}
for i, c in enumerate(ordem):
    ini, fim = lim[i], lim[i + 1]
    cenas[c] = {"ini": ini, "fim": fim, "dur": round(fim - ini, 6), "quadros": int(round((fim - ini) * FPS)),
                "audio_ini": inicio_audio[c], "estilo": T.get("estilo", {}).get(c, "mesa"), "provisoria": c in provisorias}

# 3) transcrição + refino
from faster_whisper import WhisperModel
modelo = WhisperModel(sys.argv[2] if len(sys.argv) > 2 else "small", device="cpu", compute_type="int8")
palavras = []
for c, x in pedacos:
    if c in provisorias: continue
    x16 = np.interp(np.arange(0, len(x), SR / 16000), np.arange(len(x)), x).astype(np.float32)
    # sem initial_prompt: com o texto como "dica" o Whisper pula o trecho que já está na dica
    segs, _ = modelo.transcribe(x16, language="pt", word_timestamps=True, beam_size=5)
    e = env_db(x); med = np.median(e[e > -45]) if np.any(e > -45) else -30
    for s in segs:
        for w in s.words:
            ini = float(w.start)
            a, b = max(0, int((ini - 0.20) / 0.01)), min(len(e) - 1, int((ini + 0.08) / 0.01))
            refinado = ini
            if b > a:
                j = a + int(np.argmin(e[a:b + 1]))
                if e[j] < med - 12:                     # há um vale claro antes da palavra
                    k = j
                    while k + 1 < len(e) and e[k + 1] < e[j] + 6 and (k - j) < 15: k += 1
                    cand = (k + 1) * 0.01
                    # conservador: no máximo 120 ms de ajuste e nunca atrasar mais que 40 ms
                    # (efeito alguns ms adiantado não se percebe; atrasado, sim)
                    if abs(cand - ini) <= 0.12 and cand - ini <= 0.04: refinado = cand
            palavras.append({"cena": c, "w": w.word.strip(), "ini_whisper": round(inicio_audio[c] + ini, 3),
                             "ini": round(inicio_audio[c] + refinado, 3), "fim": round(inicio_audio[c] + float(w.end), 3)})
    print(f"{c}: {sum(1 for p in palavras if p['cena'] == c)} palavras, cena {cenas[c]['ini']:.2f}–{cenas[c]['fim']:.2f} s")

(base / "palavras.json").write_text(json.dumps(palavras, ensure_ascii=False, indent=0), encoding="utf-8")
(base / "cenas.json").write_text(json.dumps(cenas, ensure_ascii=False, indent=1), encoding="utf-8")
d = [abs(p["ini"] - p["ini_whisper"]) for p in palavras]
if provisorias: print("SEM NARRAÇÃO (tempos provisórios):", ", ".join(provisorias))
print(f"total {lim[-1]:.2f} s; refino mexeu em {sum(1 for v in d if v > 0.02)} de {len(d)} palavras (máx {max(d)*1000:.0f} ms)")
