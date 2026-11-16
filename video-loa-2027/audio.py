import numpy as np, wave
SR=44100; DUR=240.6; N=int(SR*DUR); t=np.arange(N)/SR
SC=[0,15,35,60,90,120,140,165,195,225,240]
BPM=96; BEAT=60/BPM
L=np.zeros(N); R=np.zeros(N)
rng=np.random.default_rng(3)
def env(x,a,b): return np.clip((x-a)/(b-a),0,1)
def midi(m): return 440*2**((m-69)/12)
# chord progression (Am F C G / Am F C E) — 2 bars each
prog=[[57,60,64],[53,57,60],[48,55,60],[55,59,62],[57,60,64],[53,57,60],[48,55,60],[52,56,59]]
bar=4*BEAT; seg=2*bar
# PAD
pad=np.zeros(N)
for i in range(int(DUR/seg)+1):
    ch=prog[i%len(prog)]; s0=i*seg; s1=s0+seg
    a=int(max(0,(s0-0.6))*SR); b=min(N,int((s1+0.6)*SR))
    if a>=N: break
    tt=t[a:b]; e=np.minimum(env(tt,s0-0.6,s0+0.6),1-env(tt,s1-0.6,s1+0.6))
    for m in ch+[ch[0]+12]:
        f=midi(m)
        for d in (-0.12,0.12):
            ph=2*np.pi*f*(1+d/100)*tt
            pad[a:b]+=e*(np.sin(ph)+0.35*np.sin(2*ph)+0.15*np.sin(3*ph))*0.035
# gentle low-pass via moving average
k=np.ones(24)/24; pad=np.convolve(pad,k,'same')
# BASS (root, 8th pulse) from 4.2s
bass=np.zeros(N); step=BEAT/2
for j in range(int(DUR/step)):
    s0=j*step
    if s0<4.2 or s0>237.2: continue
    i=int(s0//seg); root=prog[i%len(prog)][0]-24
    a=int(s0*SR); n=int(step*SR*0.9); tt=np.arange(n)/SR
    if a+n>N: break
    e=np.exp(-tt*7)*(1-np.exp(-tt*300))
    bass[a:a+n]+=np.tanh(2.2*np.sin(2*np.pi*midi(root)*tt))*e*(0.16 if j%2==0 else 0.10)
# KICK on each beat from 4.2s, HATS offbeat from 15s
kick=np.zeros(N); hat=np.zeros(N)
for j in range(int(DUR/BEAT)):
    s0=j*BEAT
    if 4.2<=s0<=237.2:
        a=int(s0*SR); n=int(0.35*SR); tt=np.arange(n)/SR
        if a+n<N:
            f=45+90*np.exp(-tt*28); ph=2*np.pi*np.cumsum(f)/SR
            kick[a:a+n]+=np.sin(ph)*np.exp(-tt*9)*0.55
    s1=s0+BEAT/2
    if 15<=s1<=236:
        a=int(s1*SR); n=int(0.06*SR); tt=np.arange(n)/SR
        if a+n<N:
            nz=rng.standard_normal(n); nz=np.diff(np.concatenate([[0],nz]))
            hat[a:a+n]+=nz*np.exp(-tt*70)*0.05
# WHOOSH risers into each scene + impacts
fx=np.zeros(N)
def whoosh(at,length=1.4,amp=0.22):
    a=int((at-length)*SR); n=int((length+0.5)*SR)
    if a<0: return
    tt=np.arange(n)/SR; nz=rng.standard_normal(n)
    # sweeping band: crude via mixing smoothed noise of decreasing window
    sm=np.convolve(nz,np.ones(8)/8,'same')
    e=np.where(tt<length,(tt/length)**2.5,np.exp(-(tt-length)*9))
    fx[a:a+n]+=(nz*0.35+sm*0.65)*e*amp
def impact(at,amp=0.6):
    a=int(at*SR); n=int(2.2*SR); tt=np.arange(n)/SR
    if a+n>N: n=N-a; tt=tt[:n]
    f=38+70*np.exp(-tt*6); ph=2*np.pi*np.cumsum(f)/SR
    nz=np.convolve(rng.standard_normal(n),np.ones(30)/30,'same')
    fx[a:a+n]+=(np.sin(ph)*np.exp(-tt*2.2)+nz*np.exp(-tt*5)*0.8)*amp
for s in SC[1:-1]: whoosh(s); impact(s,0.28)
whoosh(4.2,1.8,0.3); impact(4.2,0.7); impact(225.4,0.6); whoosh(237.2,1.2,0.3); impact(237.2,0.8)
# soft "tick" sparkle on number reveals
for at in [4.35,22.2,35.6,54.3,60.6,73.3,82.6,90.6,96.2,124.2,140.6,145.7,165.6,199.6]:
    a=int(at*SR); n=int(0.5*SR); tt=np.arange(n)/SR
    fx[a:a+n]+=np.sin(2*np.pi*1760*tt)*np.exp(-tt*9)*0.06+np.sin(2*np.pi*2637*tt)*np.exp(-tt*12)*0.04
# intro: only pad + riser for first 4.2s
mix_mono=bass+kick+hat
music=pad*1.0
# stereo
L=music+mix_mono+fx; R=music+mix_mono+fx
# stereo width on pad: slight delay
d=int(0.012*SR); R[d:]+=pad[:-d]*0.3; L+=pad*0.3
# ducking hats/kick lightly on reflective beats? keep simple. Master fade
fade=np.minimum(env(t,0,0.8),1-env(t,239.0,240.6))
L*=fade; R*=fade
m=max(np.abs(L).max(),np.abs(R).max()); L=np.tanh(L/m*1.3)/np.tanh(1.3)*0.89; R=np.tanh(R/m*1.3)/np.tanh(1.3)*0.89
st=(np.stack([L,R],1)*32767).astype(np.int16)
w=wave.open('trilha.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes()); w.close()
print('ok',DUR)
