#!/usr/bin/env python3
"""Monta o vídeo "O dólar sobe. Quem paga a conta?" a partir dos clipes, falas e trilha.

Gera em saida/:
  video_final.mp4      vídeo com textos, narração, trilha e impacto
  video_sem_texto.mp4  mesmo corte sem textos (para editar no CapCut)
  narracao.wav, trilha.wav  faixas separadas, já no tempo do vídeo
"""
import subprocess, os, json

AQUI = os.path.dirname(os.path.abspath(__file__))
FONTE = os.path.join(AQUI, "fontes", "Montserrat-ExtraBold.ttf")
SAIDA = os.path.join(AQUI, "saida")
TMP = os.path.join(SAIDA, "tmp")
os.makedirs(TMP, exist_ok=True)

W, H, FPS = 1080, 1920, 30
ANTES, DEPOIS = 0.3, 0.4      # respiro antes/depois de cada fala
ASSINATURA = 2.8              # segundos finais com a assinatura
VOCE_NA_FALA6 = 12.45         # instante do "VOCÊ!" dentro de corte6.wav
AZUL, LARANJA = "0x0B2A5B", "0xF26B1F"

# (linhas de texto: (texto, tamanho, cor do fundo, cor do texto))
TEXTOS = {
    1: [("DÓLAR ACIMA DE R$ 6", 84, AZUL, "white"),
        ("MAIOR PATAMAR DESDE ABRIL DE 2025", 44, LARANJA, "white")],
    2: [("DÉFICIT NOMINAL", 78, AZUL, "white"),
        ("R$ 1,275 TRI", 110, LARANJA, "white"),
        ("FONTE: BC • SET/2026", 34, "white", AZUL)],
    3: [("DÍVIDA BRUTA", 78, AZUL, "white"),
        ("PROJEÇÃO 2027: 86,4% DO PIB", 54, LARANJA, "white"),
        ("FONTE: IFI", 34, "white", AZUL)],
    4: [("O DÓLAR SOBE", 84, AZUL, "white"),
        ("O CUSTO PODE AUMENTAR", 60, LARANJA, "white")],
    5: [("COMBUSTÍVEIS • FRETES", 70, AZUL, "white"),
        ("PEQUENOS NEGÓCIOS", 64, LARANJA, "white")],
    6: [("NO FINAL, QUEM PAGA", 70, AZUL, "white"),
        ("A CONTA É", 70, AZUL, "white")],
}


def run(cmd):
    subprocess.run(cmd, check=True)


def dur(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "json", path], capture_output=True, text=True).stdout
    return float(json.loads(out)["format"]["duration"])


def esc(t):
    return t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def linha(texto, tam, fundo, cor, y, inicio, fim=None):
    """drawtext com caixa colorida, entrando de baixo com fade."""
    ent = f"min(1,max(0,(t-{inicio})/0.35))"
    enable = f"gte(t,{inicio})" if fim is None else f"between(t,{inicio},{fim})"
    return (f"drawtext=fontfile='{FONTE}':expansion=none:text='{esc(texto)}':fontsize={tam}:fontcolor={cor}"
            f":box=1:boxcolor={fundo}:boxborderw={int(tam*0.35)}"
            f":x=(w-text_w)/2:y='{y}+60*(1-{ent})':alpha='{ent}':enable='{enable}'"
            f":shadowcolor=black@0.35:shadowx=6:shadowy=8")


def blocos(cena, inicio=0.25):
    filtros, y = [], 1360
    for i, (t, tam, fundo, cor) in enumerate(TEXTOS[cena]):
        filtros.append(linha(t, tam, fundo, cor, y, inicio + 0.25 * i,
                             fim=(None if cena != 6 else None)))
        y += int(tam * 1.75) + 18
    return filtros


# 1) duração de cada cena a partir da fala
falas = [os.path.join(AQUI, "audio", f"corte{i}.wav") for i in range(1, 7)]
durs = []
for i, f in enumerate(falas, 1):
    d = ANTES + dur(f) + DEPOIS
    if i == 6:
        d = ANTES + VOCE_NA_FALA6 + 1.0 + ASSINATURA
    durs.append(round(d, 3))
inicios = [round(sum(durs[:i]), 3) for i in range(6)]
total = round(sum(durs), 3)
print("cenas:", durs, "total:", total)
t_voce = inicios[5] + ANTES + VOCE_NA_FALA6

# 2) cada cena: clipe esticado/congelado até a duração, em 1080x1920
for comtexto in (True, False):
    partes = []
    for i in range(1, 7):
        clipe = os.path.join(AQUI, "clipes", f"cena{i}.mp4")
        d = durs[i - 1]
        fator = min(1.25, d / dur(clipe))
        vf = [f"setpts={fator:.4f}*PTS", f"fps={FPS}",
              f"scale={W}:{H}:flags=lanczos", "setsar=1",
              f"tpad=stop_mode=clone:stop_duration={d}",
              # zoom curto contínuo (parallax leve)
              f"zoompan=z='min(1.0+0.0012*on,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS}",
              f"trim=duration={d}", "setpts=PTS-STARTPTS",
              # entrada em "corte de papel": flash creme curto
              "fade=t=in:st=0:d=0.18:color=0xF3EAD8"]
        if comtexto:
            if i < 6:
                vf += blocos(i)
            else:
                tv = ANTES + VOCE_NA_FALA6
                fim_frase = tv + 1.0
                vf += [linha(t, tam, fundo, cor, y, 0.6 + 0.25 * k, fim_frase)
                       for k, ((t, tam, fundo, cor), y) in enumerate(zip(TEXTOS[6], (1300, 1450)))]
                # VOCÊ! avançando em direção à câmera
                vf.append(
                    f"drawtext=fontfile='{FONTE}':text='VOCÊ!':fontcolor=white"
                    f":fontsize='min(300,80+(t-{tv})*1100)'"
                    f":borderw=14:bordercolor={LARANJA}:shadowcolor=black@0.5:shadowx=10:shadowy=14"
                    f":x=(w-text_w)/2:y=1720-text_h/2:enable='between(t,{tv},{fim_frase})'")
                # assinatura institucional
                vf += [
                    f"drawbox=x=0:y=1440:w=iw:h=300:color={AZUL}@0.92:t=fill:enable='gte(t,{fim_frase})'",
                    linha("EDUARDO MOURA", 92, AZUL, "white", 1480, fim_frase + 0.1),
                    linha("FISCALIZAR PARA MUDAR", 50, LARANJA, "white", 1620, fim_frase + 0.35),
                ]
        out = os.path.join(TMP, f"{'t' if comtexto else 'l'}{i}.mp4")
        run(["ffmpeg", "-v", "error", "-y", "-i", clipe, "-vf", ",".join(vf), "-an",
             "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out])
        partes.append(out)
    lista = os.path.join(TMP, f"lista_{comtexto}.txt")
    with open(lista, "w") as fh:
        fh.writelines(f"file '{p}'\n" for p in partes)
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista,
         "-c", "copy", os.path.join(TMP, f"video_{comtexto}.mp4")])

# 3) áudio: narração posicionada, trilha com queda antes do VOCÊ, impacto
narr = os.path.join(SAIDA, "narracao.wav")
ins, fc = [], []
for i, f in enumerate(falas):
    ins += ["-i", f]
    atraso = int((inicios[i] + ANTES) * 1000)
    fc.append(f"[{i}]adelay={atraso}|{atraso}[n{i}]")
fc.append("".join(f"[n{i}]" for i in range(6)) +
          f"amix=inputs=6:normalize=0,apad,atrim=0:{total},loudnorm=I=-16:TP=-1.5[out]")
run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fc),
     "-map", "[out]", "-ar", "48000", narr])

trilha = os.path.join(SAIDA, "trilha.wav")
queda = t_voce - 1.2
run(["ffmpeg", "-v", "error", "-y", "-stream_loop", "1", "-i", os.path.join(AQUI, "audio", "trilha.mp3"),
     "-af", (f"atrim=0:{total},volume='if(lt(t,{queda}),0.20,if(lt(t,{t_voce}),0.20*(1-(t-{queda})/1.2),0))':eval=frame,"
             f"afade=t=in:d=0.6"),
     "-ar", "48000", "-ac", "2", trilha])

impacto = os.path.join(TMP, "impacto.wav")
run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
     "aevalsrc='0.9*sin(2*PI*(48+30*exp(-8*t))*t)*exp(-3.2*t)+0.5*(random(0)*2-1)*exp(-22*t)':s=48000:d=2.2",
     "-af", "lowpass=f=900,volume=1.4", "-ac", "2", impacto])

mix = os.path.join(TMP, "mix.wav")
d_imp = int(t_voce * 1000)
run(["ffmpeg", "-v", "error", "-y", "-i", narr, "-i", trilha, "-i", impacto, "-filter_complex",
     f"[2]adelay={d_imp}|{d_imp}[imp];[0][1][imp]amix=inputs=3:normalize=0,atrim=0:{total},"
     "alimiter=limit=0.95[out]", "-map", "[out]", mix])

for comtexto, nome in ((True, "video_final.mp4"), (False, "video_sem_texto.mp4")):
    run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(TMP, f"video_{comtexto}.mp4"), "-i", mix,
         "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-shortest", "-movflags", "+faststart", os.path.join(SAIDA, nome)])
print("ok", total, "VOCÊ em", round(t_voce, 2))
