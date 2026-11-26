# Gera a narração (Piper, voz pt_BR-faber) e mede a duração de cada fala.
import sys, wave
from piper import PiperVoice, SynthesisConfig
import json, subprocess, os
V=sys.argv[1]; voice=PiperVoice.load(V)
L=[
"Onze bilhões, cento e trinta e cinco milhões de reais. Esse é o orçamento da Prefeitura do Recife pra dois mil e vinte e sete. Em um minuto, eu te mostro de onde vem e pra onde vai o seu dinheiro.",
"Quase quarenta por cento vem de transferências, e mais de quatro bilhões saem direto do seu bolso. E a Prefeitura prevê arrecadar ainda mais em dois mil e vinte e sete: ISS sobe doze por cento, IPTU sobe oito por cento, Taxa de Lixo sobe sete por cento, e só em multas de trânsito são setenta e dois milhões.",
"E pra onde vai tudo isso? Mais de oitenta por cento, quase nove bilhões de reais, morre no custeio da máquina. Só treze vírgula três por cento sobra pra investimentos, como obras e equipamentos.",
"Só em contratos com empresas terceirizadas e locação de mão de obra, são dois bilhões e oitocentos e dez milhões de reais. Um quarto de todo o orçamento da cidade.",
"Urbanismo, Educação e Saúde passam de dois bilhões cada. Mas na Saúde, menos de três por cento vai pra obra e equipamento. Enquanto a Câmara custa trezentos milhões, Habitação fica com meio por cento, e Segurança Pública com apenas zero vírgula dois por cento.",
"E tem mais: a Prefeitura quer pegar seiscentos e noventa milhões em novos empréstimos, enquanto já vamos gastar seiscentos e quarenta milhões só pagando juros e parcelas de dívida velha. A dívida total já encosta nos cinco bilhões.",
"Nas letras miúdas, o prefeito ainda pede quinze por cento de remanejamento por decreto, mantém cinco milhões e setecentos mil num Gabinete do Vice sem vice-prefeito, e deixa só dez mil reais pro Fundo da Mulher e pro Bairro do Recife.",
"Por isso, apresentamos vinte e quatro emendas, redirecionando mais de cento e vinte e um milhões da máquina direto pra ponta. Compartilha esse resumo com quem paga imposto no Recife.",
]
durs=[]
for i,t in enumerate(L,1):
    with wave.open(f'raw_{i}.wav','wb') as w: voice.synthesize_wav(t,w,syn_config=SynthesisConfig(length_scale=0.76))
    # corta silêncio das pontas e acelera levemente sem mudar o tom
    subprocess.run(['ffmpeg','-loglevel','error','-y','-i',f'raw_{i}.wav','-af','silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,atempo=1.07','-ar','44100','-ac','1',f'voz_{i}.wav'],check=True)
    os.remove(f'raw_{i}.wav')
    with wave.open(f'voz_{i}.wav') as w: durs.append(w.getnframes()/w.getframerate())
# Cada cartela dura o máximo entre o tempo do roteiro e a fala + respiro.
ORIG=[6,9,8,8,8,8,7,6]; LEAD=0.25; TAIL=[.5,.5,.5,.5,.5,.5,.5,2.2]
lens=[round(max(o,LEAD+d+t),2) for o,d,t in zip(ORIG,durs,TAIL)]
starts=[0]
for l in lens: starts.append(round(starts[-1]+l,2))
json.dump({'lead':LEAD,'voice':[round(d,2) for d in durs],'lens':lens,'starts':starts[:-1],'total':starts[-1]},open('timing.json','w'),indent=1)
print(open('timing.json').read())
