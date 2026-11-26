import numpy as np, wave
SR=44100; DUR=60.0; N=int(SR*DUR)
mix=np.zeros(N); rng=np.random.default_rng(7)
def add(sig,t,g=1.0):
    i=int(t*SR); j=min(N,i+len(sig)); 
    if i<N: mix[i:j]+=g*sig[:j-i]
def env(n,a=0.005,d=0.2):
    t=np.arange(n)/SR; return np.minimum(1,t/a)*np.exp(-t/d)
def kick():
    n=int(.35*SR); t=np.arange(n)/SR; f=45+110*np.exp(-t*30)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*9)
def hat(): n=int(.05*SR); return rng.standard_normal(n)*np.exp(-np.arange(n)/SR*90)*np.r_[np.diff(np.r_[0,rng.standard_normal(n)])][:n]*0.5
def snare():
    n=int(.18*SR); t=np.arange(n)/SR; return (rng.standard_normal(n)*.7+np.sin(2*np.pi*190*t)*.5)*np.exp(-t*22)
def pop():
    n=int(.09*SR); t=np.arange(n)/SR; f=900-500*t/.09; return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*45)
def tick(f):
    n=int(.025*SR); t=np.arange(n)/SR; return np.sin(2*np.pi*f*t)*np.exp(-t*160)
def whoosh(d=.45,up=True):
    n=int(d*SR); x=rng.standard_normal(n); t=np.arange(n)/n
    # crude band sweep via moving average length change
    out=np.zeros(n); w=np.sin(np.pi*t)**2
    k=np.cumsum(x); 
    for L,wt in ((40,1),(12,.6),(4,.3)):
        sm=(k[L:]-k[:-L])/L; sm=np.r_[np.zeros(L),sm]
        out+=sm*wt*(t if up else 1-t)
    return out*w*1.6
def boom():
    n=int(1.2*SR); t=np.arange(n)/SR; return (np.sin(2*np.pi*48*t)+.4*np.sin(2*np.pi*96*t))*np.exp(-t*3.5)+rng.standard_normal(n)*np.exp(-t*30)*.3
def chaching():
    n=int(.9*SR); t=np.arange(n)/SR; s=np.zeros(n)
    s+=rng.standard_normal(n)*np.exp(-t*25)*.35
    for f,o in ((2637,.06),(3136,.06),(3951,.12),(5274,.12)):
        m=t>=o; tt=t[m]-o; s[m]+=np.sin(2*np.pi*f*tt)*np.exp(-tt*5)*.25
    return s
def stamp():
    n=int(.45*SR); t=np.arange(n)/SR
    return np.sin(2*np.pi*np.cumsum(70+80*np.exp(-t*40))/SR)*np.exp(-t*12)*1.2+rng.standard_normal(n)*np.exp(-t*40)*.6
def beep(f=880,d=.12):
    n=int(d*SR); t=np.arange(n)/SR; return np.sign(np.sin(2*np.pi*f*t))*.25*env(n,.002,.06)
def chime():
    n=int(2.5*SR); t=np.arange(n)/SR; s=0
    for f in (523.25,659.25,783.99,1046.5): s=s+np.sin(2*np.pi*f*t)*np.exp(-t*1.6)
    return s*.25
# --- music bed: 104 BPM investigative pulse
bpm=104; beat=60/bpm; t=0.0; b=0
while t<58.6:
    if b%4 in (0,2) or (b%8==7): add(kick(),t,.55)
    if b%4 in (1,3): add(snare(),t,.18)
    add(hat(),t,.12); add(hat(),t+beat/2,.08)
    # bass pulse A1/F1
    root=55.0 if (b//8)%2==0 else 43.65
    n=int(beat*.9*SR); tt=np.arange(n)/SR
    add(np.tanh(2*np.sin(2*np.pi*root*tt))*np.exp(-tt*4)*.22,t)
    t+=beat; b+=1
# duck music fade at end; add final hit
mix*=1.0
# --- SFX
for c in (6,15,23,31,39,47,54): add(whoosh(),c-.3,.5)
for i in range(52):
    tt=.3+2.7*(1-(1-i/52)**1.6)
    add(tick(1400+i*25),tt,.35)
add(boom(),3.0,.9)
add(pop(),3.25,.5); add(whoosh(.35),4.3-.15,.25)
add(pop(),6.6,.5); add(pop(),7.0,.5)
add(whoosh(.4),9.4-.2,.3)
for i in range(4): add(pop(),10.0+i*.45,.6)
add(chaching(),11.6,.8)
add(pop(),17.0,.5); add(pop(),18.0,.4); add(pop(),19.4,.5)
add(whoosh(.3),24.0,.3); add(whoosh(.3),24.8,.3)
add(pop(),25.6,.5); add(boom(),27.0,.5); add(pop(),27.0,.6); add(stamp(),28.0,1.0)
for i in range(3): add(pop(),31.6+i*.25,.45)
add(beep(880),33.9); add(beep(880),34.1)
for i in range(3): add(pop(),35.2+i*.4,.4)
add(stamp(),39.6,.8); add(stamp(),40.4,.8)
for i in range(4): add(beep(660,.1),42.8+i*.34,.8)
for i in range(3): add(whoosh(.3),47.35+i*1.8,.35); add(pop(),47.8+i*1.8,.6)
add(whoosh(.6),53.9,.5); add(pop(),54.5,.5); add(pop(),55.1,.5); add(pop(),55.8,.5)
add(stamp(),57.0,1.1); add(chime(),58.0,.7); add(boom(),58.0,.6)
# fade out last 0.8s, normalize
fo=int(.8*SR); mix[-fo:]*=np.linspace(1,0,fo)
mix=np.tanh(mix*1.1); mix/=np.max(np.abs(mix))*1.12
d=(mix*32767).astype(np.int16)
with wave.open('trilha_sfx.wav','w') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(d.tobytes())
print('ok')
