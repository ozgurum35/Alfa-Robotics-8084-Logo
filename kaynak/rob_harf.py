import pymupdf, numpy as np, sys
def an(f, band):
    band=np.array(band); c=band.mean(0)
    u,s,vt=np.linalg.svd(band-c); u_=vt[0]*(1 if vt[0][0]>0 else -1); n_=np.array([-u_[1],u_[0]])
    z=8; pm=pymupdf.open(f)[0].get_pixmap(matrix=pymupdf.Matrix(z,z),alpha=False)
    im=np.frombuffer(pm.samples,np.uint8).reshape(pm.h,pm.w,3)
    ys,xs=np.mgrid[0:pm.h,0:pm.w]; X=xs/z; Y=ys/z
    U=(X-c[0])*u_[0]+(Y-c[1])*u_[1]; N=(X-c[0])*n_[0]+(Y-c[1])*n_[1]
    bu=(band-c)@u_; bn=(band-c)@n_
    m=(np.abs(N)<bn.max()-0.6)&(U>bu.min()+3)&(U<bu.max()-3)&(im.min(2)>200)
    Uw,Nw=U[m],N[m]
    best=None
    for sl in np.arange(-0.6,0.6,0.01):
        q=np.round((Uw-Nw*sl)*4).astype(int); occ=len(np.unique(q))
        if best is None or occ<best[0]: best=(occ,sl)
    sl=best[1]; q=np.sort(Uw-Nw*sl); g=np.where(np.diff(q)>0.6)[0]
    st=[q[0]]+list(q[g+1]); en=list(q[g])+[q[-1]]
    print(f,'slant %.2f (%.1f deg)'%(sl,np.degrees(np.arctan(sl))),'n %.1f..%.1f'%(Nw.min(),Nw.max()))
    print('  letters (start,width):',[(round(a,1),round(b-a,1)) for a,b in zip(st,en)])
    for a,b in zip(st,en):
        k=(Uw-Nw*sl>=a)&(Uw-Nw*sl<=b); print('   letter %.1f h %.2f..%.2f'%(a,Nw[k].min(),Nw[k].max()))
    print('  gaps:',[round(st[i+1]-en[i],1) for i in range(len(st)-1)])
an('v10_calisma/orig_v2.pdf',[[97.05,353.2],[110.42,326.64],[323.54,257.83],[336.06,276.03]])
an(sys.argv[1] if len(sys.argv)>1 else 'v10_calisma/cur.pdf',[[111.84,342.61],[123.47,316.5],[356.72,254.0],[365.87,274.55]])
