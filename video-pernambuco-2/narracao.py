# Gera a narração (Piper, voz pt_BR-faber) e mede a duração de cada fala.
# Uso: python3 narracao.py caminho/pt_BR-faber-medium.onnx
import sys, wave, json, subprocess, os
from piper import PiperVoice, SynthesisConfig
voice=PiperVoice.load(sys.argv[1])
L=[
"Mais três coisas que só Pernambuco tem. E a segunda você vai querer provar agora.",
"Número um: o Galo da Madrugada. Nasceu em mil novecentos e setenta e oito, no bairro de São José, no Recife, e está no Guinness como o maior bloco de carnaval do mundo.",
"Número dois: a cartola. Banana frita, queijo derretido, açúcar e canela por cima. Parece estranho? Prova uma vez e me conta.",
"Número três: Olinda. Ladeiras, casarões coloridos e bonecos gigantes, como o Homem da Meia-Noite. O centro histórico é Patrimônio Mundial da UNESCO desde mil novecentos e oitenta e dois.",
"Qual dessas você já viveu? Comenta aqui, e manda pra quem precisa conhecer Pernambuco.",
]
durs=[]
for i,t in enumerate(L,1):
    with wave.open(f'raw_{i}.wav','wb') as w: voice.synthesize_wav(t,w,syn_config=SynthesisConfig(length_scale=0.8))
    subprocess.run(['ffmpeg','-loglevel','error','-y','-i',f'raw_{i}.wav','-af','silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,atempo=1.06','-ar','44100','-ac','1',f'voz_{i}.wav'],check=True)
    os.remove(f'raw_{i}.wav')
    with wave.open(f'voz_{i}.wav') as w: durs.append(w.getnframes()/w.getframerate())
ORIG=[4.5,10,10,10,6]; LEAD=0.3; TAIL=[.4,.5,.5,.5,2.0]
lens=[round(max(o,LEAD+d+t),2) for o,d,t in zip(ORIG,durs,TAIL)]
starts=[0]
for l in lens: starts.append(round(starts[-1]+l,2))
json.dump({'lead':LEAD,'voice':[round(d,2) for d in durs],'lens':lens,'starts':starts[:-1],'total':starts[-1]},open('timing.json','w'),indent=1)
print(json.dumps(json.load(open('timing.json'))))
