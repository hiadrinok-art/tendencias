# Trilha sintetizada (pulso de frevo ~150 BPM), efeitos e narração com ducking.
import numpy as np, wave, json
SR=44100; T=json.load(open('timing.json')); ST=T['starts']; DUR=T['total']; N=int(SR*DUR)
rng=np.random.default_rng(3)
def buf(): return np.zeros(N)
def add(m,sig,t,g=1.0):
    i=int(t*SR); j=min(N,i+len(sig))
    if 0<=i<N: m[i:j]+=g*sig[:j-i]
def tt(d): return np.arange(int(d*SR))/SR
def kick(): t=tt(.3); return np.sin(2*np.pi*np.cumsum(50+120*np.exp(-t*35))/SR)*np.exp(-t*10)
def snare(): t=tt(.15); return (rng.standard_normal(len(t))*.7+np.sin(2*np.pi*200*t)*.4)*np.exp(-t*28)
def hat(): t=tt(.04); return rng.standard_normal(len(t))*np.exp(-t*110)*.5
def brass(f,d=.18):  # metal estilizado: dente-de-serra com ataque rápido
    t=tt(d); s=sum(np.sin(2*np.pi*f*k*t)/k for k in range(1,9))
    return np.tanh(1.5*s)*np.minimum(1,t/.01)*np.exp(-t*6)
def whoosh(d=.45):
    n=int(d*SR); x=np.cumsum(rng.standard_normal(n)); L=10; s=np.r_[np.zeros(L),(x[L:]-x[:-L])/L]
    return s*np.sin(np.pi*np.arange(n)/n)**2*1.4
def pop(): t=tt(.08); return np.sin(2*np.pi*np.cumsum(1000-600*t/.08)/SR)*np.exp(-t*45)
def stamp(): t=tt(.4); return np.sin(2*np.pi*np.cumsum(70+90*np.exp(-t*40))/SR)*np.exp(-t*12)*1.2+rng.standard_normal(len(t))*np.exp(-t*40)*.5
def chime():
    t=tt(2.0); return sum(np.sin(2*np.pi*f*t) for f in (523.25,659.25,783.99,1046.5))*np.exp(-t*1.8)*.25
def tick(f): t=tt(.025); return np.sin(2*np.pi*f*t)*np.exp(-t*160)
def wave_(d=1.6): n=int(d*SR); x=np.cumsum(rng.standard_normal(n)); x-=np.convolve(x,np.ones(400)/400,'same'); return x/np.max(np.abs(x))*np.sin(np.pi*np.arange(n)/n)*.5
music=buf(); bpm=150; beat=60/bpm; t=0.0; b=0
# frase de metais em Fá maior (estilo frevo de rua)
riff=[(349.2,0),(440,.5),(523.3,1),(587.3,1.5),(523.3,2),(440,2.75),(523.3,3.25)]
riff2=[(466.2,0),(587.3,.5),(698.5,1),(587.3,1.75),(523.3,2.5),(440,3.25)]
while t<DUR-1.0:
    add(music,kick(),t,.5 if b%2==0 else .3)
    if b%2==1: add(music,snare(),t,.22)
    add(music,snare(),t+beat*.75,.07)
    add(music,hat(),t,.1); add(music,hat(),t+beat/2,.07)
    root=87.3 if (b//8)%2==0 else 116.5
    add(music,np.tanh(2*np.sin(2*np.pi*root*tt(beat*.45)))*np.exp(-tt(beat*.45)*6)*.2,t)
    add(music,np.tanh(2*np.sin(2*np.pi*root*1.5*tt(beat*.4)))*np.exp(-tt(beat*.4)*6)*.12,t+beat/2)
    if b%8==0:
        for f,o in (riff if (b//8)%2==0 else riff2): add(music,brass(f),t+o*beat,.11)
    t+=beat; b+=1
sfx=buf()
def at(k,o): return ST[k]+o
for c in ST[1:]: add(sfx,whoosh(),c-.3,.5)
add(sfx,stamp(),.15,.8); add(sfx,pop(),.6,.4); add(sfx,pop(),2.0,.3)
add(sfx,pop(),at(1,.5),.5); [add(sfx,pop(),at(1,x),.4) for x in (2.2,4.0,5.0)]; add(sfx,stamp(),at(1,6.6),1.0)
add(sfx,pop(),at(2,.8),.5); [add(sfx,pop(),at(2,x),.4) for x in (2.0,3.4)]; add(sfx,stamp(),at(2,4.7),1.0); add(sfx,whoosh(.3),at(2,7.6),.4)
add(sfx,wave_(),at(3,.3),.35)
for i in range(21): add(sfx,tick(1300+i*40),at(3,2.1+1.2*(1-(1-i/21)**1.5)),.35)
add(sfx,pop(),at(3,3.8),.4); add(sfx,chime(),at(3,5.4),.6)
[add(sfx,pop(),at(4,1.0+i*.25),.45) for i in range(3)]; add(sfx,chime(),at(4,2.0),.5)
voice=buf()
for k in range(len(ST)):
    with wave.open(f'voz_{k+1}.wav') as w: v=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16)/32768.0
    i=int((ST[k]+T['lead'])*SR); voice[i:i+len(v)]+=v[:N-i]
k=int(.25*SR); envv=np.convolve(np.abs(voice),np.ones(k)/k,'same')
music*=1-0.6*np.clip(envv/0.02,0,1); voice=voice/np.max(np.abs(voice))*0.9
mix=music+sfx*.8+voice*1.2
fo=int(.8*SR); mix[-fo:]*=np.linspace(1,0,fo)
mix=np.tanh(mix*1.1); mix/=np.max(np.abs(mix))*1.12
with wave.open('trilha_voz.wav','w') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype(np.int16).tobytes())
print('ok')
