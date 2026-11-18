"""Plant fakes in copies of the PS1 target and write a selections file for the shipped chain.

Run from a scratch dir; writes inj/. Env: NSEED (images), NPER (fakes per flux level per image),
SPACING (minimum px between fakes; keep it above the 51 px stamp so no stamp holds two fakes)."""
import json, warnings, numpy as np; warnings.simplefilter("ignore")
from astropy.io import fits
import os, pathlib; D=os.environ.get("DATA") or str(pathlib.Path(__file__).resolve().parents[2] / "04-your-own-data" / "data"); D=D.rstrip("/")+"/"
tgt=fits.getdata(D+"target.fits").astype(np.float64); th=fits.getheader(D+"target.fits")
tvar=fits.getdata(D+"target.var.fits").astype(np.float64); tvh=fits.getheader(D+"target.var.fits")
rm,tm=fits.getdata(D+"reference.mask.fits"),fits.getdata(D+"target.mask.fits")
ref=fits.getdata(D+"reference.fits")
os.makedirs("inj",exist_ok=True)
use=np.isfinite(ref)&np.isfinite(tgt)&np.isfinite(tvar)&((rm&8575)==0)&((tm&8575)==0)&(tvar>0)
# keep fakes off existing sources: |target| below 3 sigma in the neighbourhood
quiet=np.abs(np.nan_to_num(tgt))<3*np.sqrt(np.nan_to_num(tvar,nan=1e30))
import os; NSEED=int(os.environ.get("NSEED",4)); NPER=int(os.environ.get("NPER",25)); SPACING=float(os.environ.get("SPACING",60))
sig=1.57; gain=th["CELL.GAIN"]; yy,xx=np.mgrid[:800,:800]
sels=[]; truth={}
for seed in range(NSEED):
    rng=np.random.default_rng(100+seed)
    fluxes=np.repeat([8000,4000,2000],NPER).astype(float); pos=[]
    tries=0
    while len(pos)<len(fluxes) and tries<200000:
        tries+=1; x,y=rng.uniform(40,760,2); iy,ix=int(y),int(x)
        if use[iy-12:iy+13,ix-12:ix+13].all() and quiet[iy-8:iy+9,ix-8:ix+9].all() and all((x-a)**2+(y-b)**2>SPACING**2 for a,b in pos) and (x-402)**2+(y-400)**2>40**2: pos.append((x,y))
    pos=np.array(pos); fluxes=fluxes[:len(pos)]
    fake=np.zeros_like(tgt)
    for (x,y),f in zip(pos,fluxes): fake+=f/(2*np.pi*sig**2)*np.exp(-((xx-x)**2+(yy-y)**2)/(2*sig**2))
    t2=tgt+fake+rng.normal(0,1,fake.shape)*np.sqrt(np.clip(fake,0,None)/gain); v2=tvar+np.clip(fake,0,None)/gain
    fits.writeto(f"inj/target-{seed}.fits",t2.astype(np.float32),th,overwrite=True)
    fits.writeto(f"inj/target-{seed}.var.fits",v2.astype(np.float32),tvh,overwrite=True)
    sels.append({"expnum":f"inj{seed}","ccdnum":"sc053","band":"r","image":f"inj/target-{seed}.fits","mask":D+"target.mask.fits","variance":f"inj/target-{seed}.var.fits",
                 "template":D+"reference.fits","template_mask":D+"reference.mask.fits","template_variance":D+"reference.var.fits"})
    truth[f"inj{seed}"]={"x":pos[:,0].tolist(),"y":pos[:,1].tolist(),"flux":fluxes.tolist()}
    print(seed,len(pos),"fakes")
json.dump({"selections":sels},open("inj/selections.json","w")); json.dump(truth,open("inj/truth.json","w"))
