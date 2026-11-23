import json,sys,wave,numpy as np
SR=44100;DUR=float(sys.argv[3]);rng=np.random.default_rng(7)
out=np.zeros(int(SR*DUR))
def env(n,a=0.005,d=None):
    t=np.arange(n)/SR;e=np.minimum(1,t/a);return e*np.exp(-t/(d or 0.05))
def lp(x,k):  # média móvel simples
    return np.convolve(x,np.ones(k)/k,'same')
def noise(n):return rng.standard_normal(n)
def snd(k):
    if k=='slap':n=int(.18*SR);x=lp(noise(n),3)*env(n,.002,.03)*.9;t=np.arange(n)/SR;x+=np.sin(2*np.pi*90*t)*env(n,.002,.04)*.6;return x
    if k=='stamp':n=int(.3*SR);t=np.arange(n)/SR;return np.sin(2*np.pi*(70-30*t)*t)*env(n,.002,.08)+lp(noise(n),6)*env(n,.001,.02)*.6
    if k=='swish':n=int(.28*SR);x=noise(n);x=x-lp(x,40);e=np.sin(np.pi*np.arange(n)/n)**2;return x*e*.35
    if k=='wipe':n=int(.45*SR);x=lp(noise(n),2)-lp(noise(n),30);e=np.sin(np.pi*np.arange(n)/n)**1.5;return x*e*.5
    if k=='pop':n=int(.12*SR);t=np.arange(n)/SR;return np.sin(2*np.pi*(900-3000*t)*t)*env(n,.001,.03)*.4
    if k=='marker':n=int(.45*SR);x=noise(n);x=x-lp(x,8);e=(0.5+0.5*np.sin(2*np.pi*14*np.arange(n)/SR))*np.sin(np.pi*np.arange(n)/n);return x*e*.12
for ev in json.load(open(sys.argv[1])):
    s=snd(ev['k']);i=int(ev['t']*SR);j=min(len(out),i+len(s));out[i:j]+=s[:j-i]*.55
# trilha leve: batida lo-fi 88 bpm
bpm=88;beat=60/bpm;t=np.arange(int(.25*SR))/SR
kick=np.sin(2*np.pi*(55+60*np.exp(-t*30))*t)*np.exp(-t*12)
hat=(noise(int(.05*SR)));hat=(hat-lp(hat,4))*np.exp(-np.arange(len(hat))/SR*80)*.25
chords=[(220,261.6,329.6),(196,246.9,293.7),(174.6,220,261.6),(196,246.9,293.7)]
bed=np.zeros_like(out)
b=0;T=0.0
while T<DUR-1:
    i=int(T*SR)
    if b%4 in(0,2) or b%8==7: s=kick[:len(bed)-i];bed[i:i+len(s)]+=s*.5
    for off in (0,beat/2):
        k=int((T+off)*SR);h=hat[:max(0,len(bed)-k)];bed[k:k+len(h)]+=h*(.6 if off else .35)
    if b%4==0:
        n=int(beat*4*SR);tt=np.arange(n)/SR;c=chords[(b//4)%4];pad=sum(np.sin(2*np.pi*f*tt)+.3*np.sin(2*np.pi*2*f*tt) for f in c)
        pad*=np.minimum(1,tt/.3)*np.minimum(1,(n/SR-tt)/.4)*.05;n=min(n,len(bed)-i);bed[i:i+n]+=pad[:n]
    b+=1;T+=beat
fade=np.ones_like(bed);fl=int(2*SR);fade[-fl:]=np.linspace(1,0,fl);fade[:int(.5*SR)]=np.linspace(0,1,int(.5*SR))
mix=out+bed*.55*fade;mix/=max(1,np.abs(mix).max()/0.9)
w=wave.open(sys.argv[2],'w');w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((mix*32767).astype(np.int16).tobytes());w.close()
