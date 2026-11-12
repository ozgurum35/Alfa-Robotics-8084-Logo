# Brand colours -> CMYK (Coated FOGRA39 / Uncoated FOGRA29 via Adobe ICC) and nearest Pantone Solid Coated by CIEDE2000.
# usage: python renk.py colors.csv
import csv, math, sys
from PIL import Image, ImageCms
C = {"Lacivert": (0, 58, 111), "Acik Mavi": (99, 196, 242), "Buz": (208, 233, 232)}
def lab(rgb):  # sRGB -> Lab D50 (Bradford), like Photoshop
    l = [((c/255+0.055)/1.055)**2.4 if c/255 > 0.04045 else c/255/12.92 for c in rgb]
    M = [[0.4360747,0.3850649,0.1430804],[0.2225045,0.7168786,0.0606169],[0.0139322,0.0971045,0.7141733]]
    X,Y,Z = [sum(M[i][j]*l[j] for j in range(3)) for i in range(3)]
    w = (0.96422,1.0,0.82521); f=lambda t: t**(1/3) if t>216/24389 else (24389/27*t+16)/116
    fx,fy,fz = f(X/w[0]),f(Y/w[1]),f(Z/w[2]); return (116*fy-16, 500*(fx-fy), 200*(fy-fz))
def de00(a,b):
    L1,a1,b1=a; L2,a2,b2=b; C1=math.hypot(a1,b1); C2=math.hypot(a2,b2); Cm=(C1+C2)/2
    G=0.5*(1-math.sqrt(Cm**7/(Cm**7+25**7))); a1p,a2p=(1+G)*a1,(1+G)*a2
    C1p,C2p=math.hypot(a1p,b1),math.hypot(a2p,b2); h=lambda x,y: math.degrees(math.atan2(y,x))%360
    h1,h2=h(a1p,b1),h(a2p,b2); dL=L2-L1; dC=C2p-C1p
    dh=0 if C1p*C2p==0 else (h2-h1 if abs(h2-h1)<=180 else h2-h1-360 if h2>h1 else h2-h1+360)
    dH=2*math.sqrt(C1p*C2p)*math.sin(math.radians(dh/2)); Lm=(L1+L2)/2; Cpm=(C1p+C2p)/2
    hm=h1+h2 if C1p*C2p==0 else ((h1+h2)/2 if abs(h1-h2)<=180 else (h1+h2+360)/2 if h1+h2<360 else (h1+h2-360)/2)
    T=1-0.17*math.cos(math.radians(hm-30))+0.24*math.cos(math.radians(2*hm))+0.32*math.cos(math.radians(3*hm+6))-0.2*math.cos(math.radians(4*hm-63))
    SL=1+0.015*(Lm-50)**2/math.sqrt(20+(Lm-50)**2); SC=1+0.045*Cpm; SH=1+0.015*Cpm*T
    RT=-2*math.sqrt(Cpm**7/(Cpm**7+25**7))*math.sin(math.radians(60*math.exp(-((hm-275)/25)**2)))
    return math.sqrt((dL/SL)**2+(dC/SC)**2+(dH/SH)**2+RT*(dC/SC)*(dH/SH))
P=[(r["PANTONENAME"],(float(r["RED"]),float(r["GREEN"]),float(r["BLUE"]))) for r in csv.DictReader(open(sys.argv[1], encoding="utf-8"))]  # colors.csv: github.com/aj90909/unofficial-pantone-solid-coated-2024-v5
srgb=ImageCms.createProfile("sRGB"); prof="C:/Program Files (x86)/Common Files/Adobe/Color/Profiles/Recommended/"
for n,c in C.items():
    L=lab(c); best=sorted(P,key=lambda p: de00(L,p[1]))[:3]
    print(n, "Lab", tuple(round(x,1) for x in L), "|", ", ".join(f"{p[0]} ΔE {de00(L,p[1]):.1f}" for p in best))
    for icc in ["CoatedFOGRA39.icc","UncoatedFOGRA29.icc"]:
        for intent,nm in [(ImageCms.Intent.RELATIVE_COLORIMETRIC,"rel"),(ImageCms.Intent.PERCEPTUAL,"perc")]:
            t=ImageCms.buildTransform(srgb,ImageCms.getOpenProfile(prof+icc),"RGB","CMYK",renderingIntent=intent)
            k=ImageCms.applyTransform(Image.new("RGB",(1,1),c),t).getpixel((0,0))
            print("   ",icc,nm,"CMYK",[round(v/2.55) for v in k])
