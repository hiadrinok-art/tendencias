import re,json,subprocess
S=open('colagem/index.html').read()
T=json.load(open('timing.json')); starts=T['starts']; LEAD=0.35
LINES=["Um deputado pode ser processado pelo que fala na tribuna da Câmara? O STF está decidindo isso agora.",
"Em 2024, em discursos no plenário e numa comissão da Câmara, o deputado Marcel van Hattem, do Novo, acusou o delegado da PF Fábio Shor de fazer relatórios fraudulentos para manter preso Filipe Martins, ex-assessor de Bolsonaro. Mostrou a foto do delegado e postou tudo nas redes.",
"A PF indiciou o deputado, e a PGR o denunciou por calúnia e injúria. Para a acusação, ele foi além da crítica política: acusou um servidor de crime e espalhou isso na internet.",
"A defesa cita a Constituição: deputados são invioláveis por quaisquer de suas opiniões, palavras e votos. E lembra precedentes do próprio STF que protegeram discursos feitos na tribuna.",
"Na sexta, dia 20, o relator Flávio Dino votou para tornar o deputado réu, e rejeitou o argumento da imunidade. Alexandre de Moraes antecipou o voto e acompanhou. Zanin pediu destaque, e o julgamento vai para uma sessão presencial, ainda sem data. Falta um voto para a denúncia ser aceita.",
"Nesta fase não se decide culpa, só se a denúncia é aceita. Mas o resultado vai mostrar até onde vai a liberdade de um parlamentar na tribuna. E isso vale para qualquer deputado, de qualquer partido.",
"Para você, a tribuna deve ter proteção total? Comenta aí."]
SPOKEN={'2024':'dois mil e vinte e quatro','20':'vinte','PF':'pê éfe','PGR':'pê gê érre','STF':'ésse tê éfe'}
def syl(w):
    w=SPOKEN.get(re.sub(r'[^\wÀ-ú]','',w),w).lower()
    return max(1,len(re.findall(r'[aeiouáéíóúâêôãõà]+',w)))
def silences(f):
    o=subprocess.run(['ffmpeg','-i',f,'-af','silencedetect=n=-38dB:d=0.07','-f','null','-'],capture_output=True,text=True).stderr
    st=[float(x) for x in re.findall(r'silence_start: ([\d.]+)',o)]; en=[float(x) for x in re.findall(r'silence_end: ([\d.]+)',o)]
    dur=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f],capture_output=True,text=True).stdout)
    return list(zip(st,en+[dur]*(len(st)-len(en)))),dur
WORDS=[]
for i,line in enumerate(LINES):
    words=line.split(); sy=[syl(w) for w in words]
    sil,dur=silences(f'vo/l{i}.mp3')
    sp0=0.0; sp1=dur
    inner=[]
    for a,b in sil:
        if a<=0.02: sp0=b
        elif b>=dur-0.02: sp1=a
        else: inner.append((a,b))
    # tempo esperado de cada fronteira entre palavras (sem pausas)
    tot=sum(sy); cum=0; gaps=[]
    for k in range(len(words)-1):
        cum+=sy[k]; gaps.append((k,sp0+(sp1-sp0)*cum/tot,bool(re.search(r'[.,?!:]$',words[k]))))
    anchors=[]; last=-1
    for a,b in inner:
        mid=(a+b)/2
        best=min([g for g in gaps if g[0]>last],key=lambda g:abs(g[1]-mid)-(0.6 if g[2] else 0),default=None)
        if best and abs(best[1]-mid)-(0.6 if best[2] else 0)<1.0:
            anchors.append((best[0],a,b)); last=best[0]
    # distribui palavras entre âncoras por sílabas
    bounds=[(-1,sp0)]+[(k,b) for k,a,b in anchors]  # início de cada bloco
    ends=[a for k,a,b in anchors]+[sp1]
    for (k0,t0),t1,k1 in zip(bounds,ends,[k for k,_,_ in anchors]+[len(words)-1]):
        blk=list(range(k0+1,k1+1)); s_=sum(sy[j] for j in blk); t=t0
        for j in blk:
            d=(t1-t0)*sy[j]/s_; off=starts[i]+LEAD
            WORDS.append([round(off+t,3),round(off+t+d,3),words[j],i]); t+=d
json.dump(WORDS,open('words.json','w'),ensure_ascii=False)
def wt(scene,phrase,nth=0):
    ws=[w for w in WORDS if w[3]==scene]; p=phrase.split(); hits=[]
    for k in range(len(ws)-len(p)+1):
        if all(re.sub(r'[^\wÀ-ú]','',ws[k+m][2]).lower()==q.lower() for m,q in enumerate(p)): hits.append(ws[k][0])
    assert hits,(scene,phrase); return hits[nth]
CUES=[
 ['@0','deputado','deputado','processado','processado','+processado','+processado','tribuna','STF'],
 ['@0','@0','2024','Marcel','Fábio','acusou','acusou','relatórios','+relatórios','Mostrou','postou','postou'],
 ['@0','@0','+@0','+@0','PF','PGR','calúnia','injúria','além','servidor'],
 ['@0','+@0','invioláveis','invioláveis','precedentes'],
 ['@0','sexta','Flávio','rejeitou','Alexandre','Zanin','destaque','sessão','Falta','voto:1'],
 ['culpa','denúncia','liberdade','liberdade','+tribuna','qualquer'],
 ['@0','@0','tribuna','Comenta','Comenta','+Comenta'],
]
secs=S.split('<section ')
out=[secs[0]]
for i,sec in enumerate(secs[1:]):
    els=list(re.finditer(r'class="(?:tape )?el[ "][^>]*?data-in="([\d.]+)"',sec))
    assert len(els)==len(CUES[i]),(i,len(els),len(CUES[i]))
    vals=[]
    for c in CUES[i]:
        plus=c.startswith('+'); c=c.lstrip('+')
        if c=='@0': v=0.05
        else:
            ph,_,n=c.partition(':'); v=wt(i,ph,int(n or 0))-starts[i]-0.08
        vals.append(max(0.0,v+(0.12 if plus else 0)))
    for m,v in reversed(list(zip(els,vals))):
        a,b=m.span(1); sec=sec[:a]+f'{v:.2f}'+sec[b:]
    if i==3: sec=re.sub(r'data-hl-in="[\d.]+"',f'data-hl-in="{wt(3,"quaisquer")-starts[3]:.2f}"',sec)
    out.append(sec)
S='<section '.join(out)
# legendas com tempo real por palavra
S=re.sub(r'const NARR = .*?;\n','const WORDS = '+json.dumps(WORDS,ensure_ascii=False)+';\n',S,count=1,flags=re.S)
S=re.sub(r'function buildCaps\(\)\{.*?\n\}\nconst CAPS=buildCaps\(\);',r'''function buildCaps(){
  const caps=[]; let cur=[];
  WORDS.forEach((w,k)=>{cur.push(w); const len=cur.map(x=>x[2]).join(' ').length; const nx=WORDS[k+1];
    if(!nx||nx[3]!==w[3]||len>26||/[.?!:]$/.test(w[2])||(/,$/.test(w[2])&&len>14)){caps.push(cur);cur=[];}});
  return caps.map((c,k)=>{const nx=caps[k+1]; const end=c[c.length-1][1]; const e=(nx&&nx[0][3]===c[0][3])?nx[0][0]:end+0.35;
    return {s:c[0][0]-0.05,e,words:c.map(x=>x[2]),ts:c.map(x=>x[0])};});
}
const CAPS=buildCaps();''',S,flags=re.S)
S=S.replace("const spans=cb.querySelectorAll('.w'); const tot=c.words.join('').length; let acc=0; const prog=(t-c.s)/(c.e-c.s)*tot;\n  spans.forEach((sp,k)=>{const L=c.words[k].length; sp.classList.toggle('on',prog>=acc&&(prog<acc+L||k===spans.length-1)); acc+=L;});",
"const spans=cb.querySelectorAll('.w');\n  spans.forEach((sp,k)=>{sp.classList.toggle('on',t>=c.ts[k]&&(k===spans.length-1||t<c.ts[k+1]));});")
assert 'c.ts[k]' in S and 'const WORDS' in S
open('colagem/index.html','w').write(S)
for w in WORDS[:12]: print(w)
