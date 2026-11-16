import json, sys, numpy as np, pandas as pd
truth=json.load(open("inj/truth.json"))
for d in sys.argv[1:]:
    rows=[]
    for e,t in truth.items():
        try: c=pd.read_parquet(f"{d}/items/sc053-v{e}/catalog.parquet"); s=json.load(open(f"{d}/items/sc053-v{e}/summary.json"))
        except Exception as ex: continue
        x=s['diagnostics']['xpois']
        if e=="inj0": print(d,"chi2/dof",round(x['chi2']/x['dof'],2),"kernel sum",round(x['kernel_sum'],3),"fit px",x['fit_pixel_count'],"corr",{k:round(v,2) for k,v in s['uq']['correlation']['measured'].items()} if s['uq'].get('correlation') else None,"closed",{k:round(v,2) for k,v in s['uq']['correlation']['closed_form'].items()} if s['uq'].get('correlation') else None,"ncand",len(c))
        for X,Y,f in zip(t["x"],t["y"],t["flux"]):
            k=np.hypot(c.x-X,c.y-Y); i=k.idxmin()
            if k[i]<3: r=c.loc[i]; rows.append(dict(f=f,m=r.psf_flux,ef=r.psf_flux_err_fit,e=r.psf_flux_err))
    D=pd.DataFrame(rows).dropna()
    mad=lambda p: 1.4826*np.median(np.abs(p-np.median(p)))
    for f,g in D.groupby("f"):
        pf=(g.m-f)/g.ef; pt=(g.m-f)/g.e
        print(f"  {f:5.0f}: n {len(g)} ratio {np.median(g.m/f):.3f} | pull vs fit err: std {pf.std():.2f} mad {mad(pf):.2f} | vs total: std {pt.std():.2f} mad {mad(pt):.2f} | total/fit {np.median(g.e/g.ef):.2f}")
