#!/usr/bin/env python3
"""
CAC-FFLS PAI v2020 production-AI raw-data gate.

Frozen design:
- official Alibaba PAI v2020 group-tag, task, and job archives;
- workload tags joined group.inst_id -> job.inst_id -> task.job_name;
- complete-case rows require inst_num>0 and finite start_time, plan_cpu, plan_gpu;
- select the same top-two workload set before fuzzy arithmetic from complete-case
  task-instance frequency; task-row ranking is audited as a selection sensitivity;
- primary blocks are complete Monday-to-Monday weeks in the UTC+8 pseudo-calendar,
  because Alibaba documents that time-of-day and day-of-week are preserved after
  timestamp desensitization;
- plan_cpu/100 = requested vCPU cores per instance;
- plan_gpu/100 = requested GPU-equivalents per instance;
- temporal fuzzy spreads are pooled-center to observed weekly min/max;
- compare 2014 positive center-spread arithmetic with direct two-term TA arithmetic
  on the same positive-triangular domain.

Usage:
  python run_pai_v3_gate.py GROUP.tar.gz TASK.tar.gz JOB.tar.gz --out OUTPUT_DIR
"""
from __future__ import annotations
import argparse, csv, io, tarfile, hashlib, math, json, datetime as dt
from collections import Counter
from pathlib import Path
import numpy as np

EXPECTED = {
    "group": {
        "archive":"722fef30b7fb7aa50dabd79155614b5423a9d65cf45a9b26c590d57725423a14",
        "member":"d23fcb56d88b2976fda4a62708d77b2a8c98635c4b443f100ed5553d4cd07fbe",
    },
    "task": {
        "archive":"cd1d6dc3215d2a8607ccf6b6dd952b5db776df86926c73259fea7c1499ac40e5",
        "member":"6954802b457305f8a9e480ef97c40060baee59649fd3adc62c5a1e048aa058de",
    },
    "job": {
        "archive":"5aad7f7caac501136d14ed6a48e40546f825d7b0617a3a4f337e2348fe0a6cb0",
        "member":"379ecb3becaba347f44a53bf7eb53e54b185221b2a0338a3f828828d269ba96c",
    },
}
WEEK=604800.0
TZ=dt.timezone(dt.timedelta(hours=8))
WEEKDAYS=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

def sha256_path(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()

def member_sha256(path: Path):
    h=hashlib.sha256()
    with tarfile.open(path,"r:gz") as tf:
        ms=tf.getmembers()
        if len(ms)!=1: raise RuntimeError(f"{path}: expected one member")
        f=tf.extractfile(ms[0])
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
        return ms[0].name,ms[0].size,h.hexdigest()

def evaluate(records,start_min,start_max,start0,selected):
    nwin=int(math.floor((start_max-start0)/WEEK))
    if nwin<2: raise RuntimeError("Too few complete weekly blocks")
    agg=[{w:{"n":0.0,"cpu":0.0,"gpu":0.0} for w in selected} for _ in range(nwin)]
    for w,st,inst,cpu,gpu in records:
        if st<start0: continue
        i=int((st-start0)//WEEK)
        if 0<=i<nwin:
            d=agg[i][w]
            d["n"]+=inst; d["cpu"]+=inst*cpu; d["gpu"]+=inst*gpu
    if any(d[w]["n"]<=0 for d in agg for w in selected):
        raise RuntimeError("A selected class is absent from a complete block")
    weekly=[]
    for i,d in enumerate(agg):
        r={"window":i+1,"start_second":start0+i*WEEK,"end_second":start0+(i+1)*WEEK}
        for w in selected:
            r[f"instances_{w}"]=d[w]["n"]
            r[f"aC_{w}"]=d[w]["cpu"]/d[w]["n"]/100.0
            r[f"aG_{w}"]=d[w]["gpu"]/d[w]["n"]/100.0
            r[f"lambda_{w}"]=d[w]["n"]/7.0
        r["bC"]=sum(d[w]["cpu"] for w in selected)/7.0/100.0
        r["bG"]=sum(d[w]["gpu"] for w in selected)/7.0/100.0
        r["closureC"]=r["bC"]-(r["aC_bert"]*r["lambda_bert"]+r["aC_ctr"]*r["lambda_ctr"])
        r["closureG"]=r["bG"]-(r["aG_bert"]*r["lambda_bert"]+r["aG_ctr"]*r["lambda_ctr"])
        weekly.append(r)
    days=7*nwin
    pooled={}
    for w in selected:
        n=sum(d[w]["n"] for d in agg); cpu=sum(d[w]["cpu"] for d in agg); gpu=sum(d[w]["gpu"] for d in agg)
        pooled[f"instances_{w}"]=n
        pooled[f"aC_{w}"]=cpu/n/100.0
        pooled[f"aG_{w}"]=gpu/n/100.0
        pooled[f"lambda_{w}"]=n/days
    pooled["bC"]=sum(d[w]["cpu"] for d in agg for w in selected)/days/100.0
    pooled["bG"]=sum(d[w]["gpu"] for d in agg for w in selected)/days/100.0

    qs=["aC_bert","aC_ctr","aG_bert","aG_ctr","bC","bG"]
    tfn={}
    for q in qs:
        vals=[r[q] for r in weekly]; c=pooled[q]
        tfn[q]={"center":c,"left_spread":c-min(vals),"right_spread":max(vals)-c,
                "min_week":min(vals),"max_week":max(vals)}
    A=np.array([[pooled["aC_bert"],pooled["aC_ctr"]],[pooled["aG_bert"],pooled["aG_ctr"]]],float)
    M=np.array([[tfn["aC_bert"]["left_spread"],tfn["aC_ctr"]["left_spread"]],
                [tfn["aG_bert"]["left_spread"],tfn["aG_ctr"]["left_spread"]]],float)
    N=np.array([[tfn["aC_bert"]["right_spread"],tfn["aC_ctr"]["right_spread"]],
                [tfn["aG_bert"]["right_spread"],tfn["aG_ctr"]["right_spread"]]],float)
    b=np.array([pooled["bC"],pooled["bG"]],float)
    h=np.array([tfn["bC"]["left_spread"],tfn["bG"]["left_spread"]],float)
    g=np.array([tfn["bC"]["right_spread"],tfn["bG"]["right_spread"]],float)
    x=np.linalg.solve(A,b)
    yM=np.linalg.solve(A,h-M@x); zM=np.linalg.solve(A,g-N@x)
    yTA=np.linalg.solve(A,4*h-M@x); zTA=np.linalg.solve(A,4*g-N@x)
    def adm(y,z):
        return bool(np.all(y>=-1e-10) and np.all(z>=-1e-10) and np.all(x-y>=-1e-10))
    am,at=adm(yM,zM),adm(yTA,zTA)
    return {
        "n_weeks":nwin,"weekly":weekly,"pooled":pooled,"tfn":tfn,
        "A":A.tolist(),"M":M.tolist(),"N":N.tolist(),"b":b.tolist(),"h":h.tolist(),"g":g.tolist(),
        "detA":float(np.linalg.det(A)),"rankA":int(np.linalg.matrix_rank(A)),"cond2A":float(np.linalg.cond(A)),
        "x":x.tolist(),
        "M_solution":{"y":yM.tolist(),"z":zM.tolist(),"lower":(x-yM).tolist(),"upper":(x+zM).tolist(),"admissible":am},
        "TA_solution":{"y":yTA.tolist(),"z":zTA.tolist(),"lower":(x-yTA).tolist(),"upper":(x+zTA).tolist(),"admissible":at},
        "k_M":1 if am else 0,"k_TA":1 if at else 0,
        "k_core":1 if (am and at and np.allclose(yM,yTA,rtol=0,atol=1e-10) and np.allclose(zM,zTA,rtol=0,atol=1e-10)) else 0,
        "max_abs_weekly_closure":max(abs(r[k]) for r in weekly for k in ["closureC","closureG"]),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("group",type=Path); ap.add_argument("task",type=Path); ap.add_argument("job",type=Path)
    ap.add_argument("--out",type=Path,default=Path("pai_v3_gate_output"))
    a=ap.parse_args(); a.out.mkdir(parents=True,exist_ok=True)
    paths={"group":a.group,"task":a.task,"job":a.job}
    source={}
    for k,p in paths.items():
        ar=sha256_path(p); name,size,me=member_sha256(p)
        if ar!=EXPECTED[k]["archive"] or me!=EXPECTED[k]["member"]:
            raise SystemExit(f"STOP: hash mismatch for {k}")
        source[k]={"file":p.name,"bytes":p.stat().st_size,"archive_sha256":ar,
                   "member":name,"uncompressed_bytes":size,"member_sha256":me}
    tag_map={}; tag_counts=Counter(); group_rows=0
    with tarfile.open(a.group,"r:gz") as tf:
        f=io.TextIOWrapper(tf.extractfile(tf.getmembers()[0]),encoding="utf-8",newline="")
        for row in csv.reader(f):
            group_rows+=1
            if len(row)<5: continue
            inst=row[0].strip(); w=row[4].strip()
            if w: tag_map[inst]=w; tag_counts[w]+=1
    job_map={}; job_rows=0; unmatched=set(tag_map)
    with tarfile.open(a.job,"r:gz") as tf:
        f=io.TextIOWrapper(tf.extractfile(tf.getmembers()[0]),encoding="utf-8",newline="")
        for row in csv.reader(f):
            job_rows+=1
            if len(row)<6: continue
            inst=row[1].strip()
            if inst in tag_map:
                job_map[row[0].strip()]=tag_map[inst]; unmatched.discard(inst)
    task_rows=0; start_min=math.inf; start_max=-math.inf
    row_freq=Counter(); inst_freq=Counter(); dropped=Counter()
    with tarfile.open(a.task,"r:gz") as tf:
        f=io.TextIOWrapper(tf.extractfile(tf.getmembers()[0]),encoding="utf-8",newline="")
        for row in csv.reader(f):
            task_rows+=1
            if len(row)<10: continue
            try: st=float(row[4]) if row[4] else math.nan
            except: st=math.nan
            if math.isfinite(st): start_min=min(start_min,st); start_max=max(start_max,st)
            w=job_map.get(row[0].strip())
            if not w: continue
            try:
                inst=float(row[2]) if row[2] else math.nan
                cpu=float(row[6]) if row[6] else math.nan
                gpu=float(row[8]) if row[8] else math.nan
            except: inst=cpu=gpu=math.nan
            if not all(map(math.isfinite,[inst,st,cpu,gpu])) or inst<=0:
                dropped[w]+=1; continue
            row_freq[w]+=1; inst_freq[w]+=inst
    top_rows=[x for x,_ in row_freq.most_common(2)]
    top_inst=[x for x,_ in inst_freq.most_common(2)]
    if set(top_rows)!=set(top_inst):
        raise SystemExit(f"STOP: top-two set differs by ranking rule: rows={top_rows}, instances={top_inst}")
    selected=sorted(top_inst)
    if set(selected)!={"bert","ctr"}:
        raise SystemExit(f"STOP: frozen top-two pair changed: {selected}")
    records=[]
    with tarfile.open(a.task,"r:gz") as tf:
        f=io.TextIOWrapper(tf.extractfile(tf.getmembers()[0]),encoding="utf-8",newline="")
        for row in csv.reader(f):
            if len(row)<10: continue
            w=job_map.get(row[0].strip())
            if w not in selected: continue
            try:
                inst=float(row[2]) if row[2] else math.nan; st=float(row[4]) if row[4] else math.nan
                cpu=float(row[6]) if row[6] else math.nan; gpu=float(row[8]) if row[8] else math.nan
            except: continue
            if all(map(math.isfinite,[inst,st,cpu,gpu])) and inst>0:
                records.append((w,st,inst,cpu,gpu))
    first=dt.datetime.fromtimestamp(start_min,TZ); midnight=first.replace(hour=0,minute=0,second=0,microsecond=0)
    cand=midnight+dt.timedelta(days=(7-midnight.weekday())%7)
    if cand.timestamp()<start_min: cand+=dt.timedelta(days=7)
    primary=evaluate(records,start_min,start_max,cand.timestamp(),selected)
    align=[]
    for wd in range(7):
        c=midnight+dt.timedelta(days=(wd-midnight.weekday())%7)
        if c.timestamp()<start_min: c+=dt.timedelta(days=7)
        rr=evaluate(records,start_min,start_max,c.timestamp(),selected)
        align.append({"weekday":WEEKDAYS[wd],"start_second":c.timestamp(),"n_weeks":rr["n_weeks"],
                      "detA":rr["detA"],"cond2A":rr["cond2A"],"k_M":rr["k_M"],"k_TA":rr["k_TA"],
                      "k_core":rr["k_core"],"min_M_lower":min(rr["M_solution"]["lower"]),
                      "min_TA_lower":min(rr["TA_solution"]["lower"])})
    result={"decision":"PASS_TO_V3" if primary["k_M"]==1 and primary["k_TA"]==0 else "HOLD",
            "source_lock":source,
            "census":{"group_rows":group_rows,"job_rows":job_rows,"task_rows":task_rows,
                      "tagged_unique_jobs":len(tag_map),"tagged_jobs_matched":len(job_map),"tagged_jobs_unmatched":len(unmatched),
                      "workload_tag_counts":dict(tag_counts),"complete_case_task_rows":dict(row_freq),
                      "complete_case_task_instances":dict(inst_freq),"dropped_incomplete_rows":dict(dropped),
                      "top_two_by_task_rows":top_rows,"top_two_by_task_instances":top_inst,
                      "selected_pair":selected,"trace_start_min":start_min,"trace_start_max":start_max,
                      "primary_rule":"Complete Monday-to-Monday 7-day blocks in UTC+8 pseudo-calendar."},
            "primary":primary,"weekday_alignment_sensitivity":align}
    (a.out/"results.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    with (a.out/"weekly.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(primary["weekly"][0].keys())); w.writeheader(); w.writerows(primary["weekly"])
    with (a.out/"alignment.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(align[0].keys())); w.writeheader(); w.writerows(align)
    print(json.dumps({"decision":result["decision"],"selected_pair":selected,
                      "n_weeks":primary["n_weeks"],"detA":primary["detA"],"cond2A":primary["cond2A"],
                      "x":primary["x"],"k_M":primary["k_M"],"k_TA":primary["k_TA"],"k_core":primary["k_core"],
                      "weekday_robust":all(r["k_M"]==1 and r["k_TA"]==0 for r in align)},indent=2))
if __name__=="__main__":
    main()
