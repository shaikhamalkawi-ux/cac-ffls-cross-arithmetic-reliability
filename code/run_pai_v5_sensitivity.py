#!/usr/bin/env python3
"""Reproduce CAC-FFLS V5 crossed PAI phase/envelope sensitivity.

Usage:
  python run_pai_v5_sensitivity.py GROUP.tar.gz TASK.tar.gz JOB.tar.gz --out OUTDIR

This script reuses the frozen source-lock, join, complete-case, and weekly-balance
logic from run_pai_v3_gate.py, then crosses five center-preserving empirical
envelope rules with all seven UTC+8 weekday block phases.
"""
from __future__ import annotations
import argparse, csv, io, tarfile, math, datetime as dt, json
from pathlib import Path
from collections import Counter
import numpy as np
import importlib.util

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('gate',HERE/'run_pai_v3_gate.py')
gate=importlib.util.module_from_spec(spec); spec.loader.exec_module(gate)

ENVS=['Full weekly range','Q10-Q90','Q20-Q80','Q25-Q75','Trim one extreme/side']


def load_records(group:Path,task:Path,job:Path):
    # Recheck official archive and CSV payload hashes before analysis.
    for k,p in {'group':group,'task':task,'job':job}.items():
        ar=gate.sha256_path(p); _,_,me=gate.member_sha256(p)
        if ar!=gate.EXPECTED[k]['archive'] or me!=gate.EXPECTED[k]['member']:
            raise SystemExit(f'STOP: hash mismatch for {k}')
    tag_map={}
    with tarfile.open(group,'r:gz') as tf:
        f=io.TextIOWrapper(tf.extractfile(tf.getmembers()[0]),encoding='utf-8',newline='')
        for row in csv.reader(f):
            if len(row)>=5 and row[4].strip(): tag_map[row[0].strip()]=row[4].strip()
    job_map={}
    with tarfile.open(job,'r:gz') as tf:
        f=io.TextIOWrapper(tf.extractfile(tf.getmembers()[0]),encoding='utf-8',newline='')
        for row in csv.reader(f):
            if len(row)>=6 and row[1].strip() in tag_map:
                job_map[row[0].strip()]=tag_map[row[1].strip()]
    row_freq=Counter();inst_freq=Counter();records=[];start_min=math.inf;start_max=-math.inf
    # One pass collects frequency and top-pair candidate records.
    raw=[]
    with tarfile.open(task,'r:gz') as tf:
        f=io.TextIOWrapper(tf.extractfile(tf.getmembers()[0]),encoding='utf-8',newline='')
        for row in csv.reader(f):
            if len(row)<10: continue
            try:
                st=float(row[4]) if row[4] else math.nan
                inst=float(row[2]) if row[2] else math.nan
                cpu=float(row[6]) if row[6] else math.nan
                gpu=float(row[8]) if row[8] else math.nan
            except Exception:
                continue
            if math.isfinite(st): start_min=min(start_min,st);start_max=max(start_max,st)
            w=job_map.get(row[0].strip())
            if not w or not all(map(math.isfinite,[inst,st,cpu,gpu])) or inst<=0: continue
            row_freq[w]+=1;inst_freq[w]+=inst;raw.append((w,st,inst,cpu,gpu))
    top_rows=[x for x,_ in row_freq.most_common(2)]
    top_inst=[x for x,_ in inst_freq.most_common(2)]
    if set(top_rows)!=set(top_inst) or set(top_inst)!={'bert','ctr'}:
        raise SystemExit(f'STOP: frozen top-two set changed rows={top_rows} instances={top_inst}')
    selected=['bert','ctr']
    records=[r for r in raw if r[0] in selected]
    return records,start_min,start_max,selected


def solve_envelope(weekly,pooled,env):
    qs=['aC_bert','aC_ctr','aG_bert','aG_ctr','bC','bG'];t={}
    for q in qs:
        v=np.array([r[q] for r in weekly],float);c=float(pooled[q])
        if env=='Full weekly range': lo,hi=float(v.min()),float(v.max())
        elif env=='Q10-Q90': lo,hi=np.quantile(v,[.10,.90])
        elif env=='Q20-Q80': lo,hi=np.quantile(v,[.20,.80])
        elif env=='Q25-Q75': lo,hi=np.quantile(v,[.25,.75])
        elif env=='Trim one extreme/side':
            sv=np.sort(v);lo,hi=float(sv[1]),float(sv[-2])
        else: raise ValueError(env)
        lo=min(float(lo),c);hi=max(float(hi),c)
        t[q]=(c,c-lo,hi-c)
    A=np.array([[pooled['aC_bert'],pooled['aC_ctr']],[pooled['aG_bert'],pooled['aG_ctr']]],float)
    M=np.array([[t['aC_bert'][1],t['aC_ctr'][1]],[t['aG_bert'][1],t['aG_ctr'][1]]],float)
    N=np.array([[t['aC_bert'][2],t['aC_ctr'][2]],[t['aG_bert'][2],t['aG_ctr'][2]]],float)
    b=np.array([pooled['bC'],pooled['bG']],float);h=np.array([t['bC'][1],t['bG'][1]],float);g=np.array([t['bC'][2],t['bG'][2]],float)
    x=np.linalg.solve(A,b)
    yM=np.linalg.solve(A,h-M@x);zM=np.linalg.solve(A,g-N@x)
    yT=np.linalg.solve(A,4*h-M@x);zT=np.linalg.solve(A,4*g-N@x)
    def adm(y,z): return bool(np.all(y>=-1e-10) and np.all(z>=-1e-10) and np.all(x-y>=-1e-10))
    am,at=adm(yM,zM),adm(yT,zT)
    core=int(am and at and np.allclose(yM,yT,rtol=0,atol=1e-10) and np.allclose(zM,zT,rtol=0,atol=1e-10))
    if am and not at: patt='admissibility fragility (M only)'
    elif am and at and not core: patt='identity fragility (both admissible, distinct)'
    elif not am and not at: patt='double inadmissibility'
    elif core: patt='shared-core stability'
    else: patt='other'
    return {'k_M':int(am),'k_TA':int(at),'k_core':core,'pattern':patt,
            'min_lower_M':float(np.min(x-yM)),'min_lower_TA':float(np.min(x-yT)),
            'min_y_M':float(np.min(yM)),'min_z_M':float(np.min(zM)),
            'min_y_TA':float(np.min(yT)),'min_z_TA':float(np.min(zT))}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('group',type=Path);ap.add_argument('task',type=Path);ap.add_argument('job',type=Path);ap.add_argument('--out',type=Path,default=Path('pai_v5_sensitivity'))
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    records,start_min,start_max,selected=load_records(a.group,a.task,a.job)
    first=dt.datetime.fromtimestamp(start_min,gate.TZ);midnight=first.replace(hour=0,minute=0,second=0,microsecond=0)
    rows=[]
    for wd in range(7):
        c=midnight+dt.timedelta(days=(wd-midnight.weekday())%7)
        if c.timestamp()<start_min:c+=dt.timedelta(days=7)
        rr=gate.evaluate(records,start_min,start_max,c.timestamp(),selected)
        for env in ENVS:
            z=solve_envelope(rr['weekly'],rr['pooled'],env)
            rows.append({'weekday':gate.WEEKDAYS[wd],'n_weeks':rr['n_weeks'],'envelope':env,**z})
    fields=list(rows[0].keys())
    with (a.out/'pai_5x7_joint_sensitivity.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    counts=Counter(r['pattern'] for r in rows)
    summary={'total_combinations':len(rows),'patterns':dict(counts),'common_core_nonempty_count':sum(r['k_core']>0 for r in rows),'at_least_one_admissible_count':sum((r['k_M']+r['k_TA'])>0 for r in rows),'primary_pattern_count':sum(r['k_M']==1 and r['k_TA']==0 for r in rows),'exceptions':[r for r in rows if not (r['k_M']==1 and r['k_TA']==0)]}
    (a.out/'pai_5x7_joint_sensitivity_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
