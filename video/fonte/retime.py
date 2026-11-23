import re,json,subprocess
src='colagem/index.html'; s=open(src).read()
durs=[6.765688,17.789375,12.512625,12.277500,18.285688,12.826063,4.127313]
brk=[[3.98],[14.21],[5.62],[2.05],[7.30,10.40],[4.20],[3.20]]
LEAD,TAIL=0.35,0.45
old=[(0,5),(5,20),(20,35),(35,50),(50,70),(70,85),(85,90)]
texts=re.findall(r'^ \[\d+,\d+,"(.*)"\],?$',s,re.M); assert len(texts)==7
starts=[];t=0
for i,d in enumerate(durs):
    starts.append(t); t+= LEAD+d+(TAIL if i<6 else 2.2)
total=round(t,2); ends=starts[1:]+[total]
# cenas
secs=s.split('<section ')
out=[secs[0]]
for i,sec in enumerate(secs[1:]):
    ratio=(ends[i]-starts[i])/(old[i][1]-old[i][0])
    sec=re.sub(r'data-start="[\d.]+" data-end="[\d.]+"',f'data-start="{starts[i]:.3f}" data-end="{ends[i]:.3f}"',sec,1)
    sec=re.sub(r'data-in="([\d.]+)"',lambda m:f'data-in="{float(m.group(1))*ratio:.2f}"',sec)
    sec=re.sub(r'data-hl-in="([\d.]+)"',lambda m:f'data-hl-in="{float(m.group(1))*ratio:.2f}"',sec)
    out.append(sec)
s='<section '.join(out)
# segmentos de legenda ancorados nas pausas da narração
segs=[]
for i,txt in enumerate(texts):
    words=txt.split(); L=sum(len(w)+1 for w in words); acc=0; cands=[]
    for k,w in enumerate(words[:-1]):
        acc+=len(w)+1
        if re.search(r'[.?!:,]$',w): cands.append((k,acc/L))
    cuts=[]
    for b in brk[i]:
        k,_=min(cands,key=lambda c:abs(c[1]-b/durs[i])); cuts.append((k,b))
    v0=starts[i]+LEAD; prev_k=-1; prev_t=0
    for k,b in sorted(set(cuts))+[(len(words)-1,durs[i])]:
        segs.append([round(v0+prev_t,3),round(v0+b,3),' '.join(words[prev_k+1:k+1])]); prev_k=k; prev_t=b
narr='const NARR = '+json.dumps(segs,ensure_ascii=False)+';'
s=re.sub(r'const NARR = \[.*?\n\];',lambda m:narr,s,flags=re.S)
s=s.replace("let t=s+0.15; const span=(e-s)-0.45;","let t=s; const span=(e-s)-0.1;")
open(src,'w').write(s)
json.dump({'starts':starts,'total':total},open('timing.json','w'))
print(total); print(*segs,sep='\n')
