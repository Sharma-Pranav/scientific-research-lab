"""M5 rolling-origin forecast-selection development study (never opens sealed holdouts).

The *data* are sourced separately and hash checked. No raw dataset is committed.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import statistics
import urllib.request
from collections import defaultdict
from pathlib import Path
from research_lab.leadtime import canonical, newsvendor_cost
from research_lab.engine import write_new

URL="https://zenodo.org/records/10203108/files/sales_train_validation.csv?download=1"
MD5="26a366a25beb57b0a8f4c7b148758f94"
METHODS=("seasonal_naive","mean28","mean56","croston_sba")

def hash_file(path):
    h=hashlib.md5()  # legacy published dataset checksum; not cryptographic integrity
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def acquire(path,download=False):
    path=Path(path)
    if not path.exists():
        if not download: raise FileNotFoundError("Obtain rules-authorized M5 file or pass --download")
        path.parent.mkdir(parents=True,exist_ok=True)
        tmp=path.with_suffix(".partial")
        try:
            req=urllib.request.Request(URL,headers={"User-Agent":"scientific-research-lab/0.3"})
            with urllib.request.urlopen(req,timeout=180) as inp,tmp.open("wb") as out:
                while b:=inp.read(1024*1024):out.write(b)
            if hash_file(tmp)!=MD5:raise ValueError("M5 source checksum mismatch")
            tmp.replace(path)
        finally:
            tmp.unlink(missing_ok=True)
    if hash_file(path)!=MD5: raise ValueError("Local M5 source checksum mismatch")
    return MD5

def load_panel(path,n_days=1913,n_each=8):
    """Select lowest SHA256 identifier ranks in each of nine state/category groups."""
    header=["id","item_id","dept_id","cat_id","store_id","state_id"]+[f"d_{i}" for i in range(1,n_days+1)]
    groups=defaultdict(list); scanned=0
    with open(path,newline="",encoding="utf-8") as f:
        reader=csv.reader(f)
        if next(reader)!=header:raise ValueError("Unexpected M5 column schema")
        for row in reader:
            if len(row)!=len(header):raise ValueError("Malformed M5 row")
            ident,_,_,category,store,state=row[:6]
            if state not in {"CA","TX","WI"} or not store.startswith(state+"_"):raise ValueError("Unexpected state")
            sample=groups[(state,category)]
            rank=hashlib.sha256(ident.encode()).hexdigest()
            if len(sample)<n_each or rank<sample[-1][0]:
                data=[int(x) for x in row[6:]]
                if min(data)<0:raise ValueError("Negative sales")
                sample.append((rank,ident,store,state,category,data))
                sample.sort(key=lambda t:t[0]);del sample[n_each:]
            scanned+=1
    if len(groups)!=9 or any(len(v)!=n_each for v in groups.values()):
        raise ValueError("Missing or undersized M5 strata")
    panel=[{"id":r[1],"store":r[2],"state":r[3],"category":r[4],"y":r[5]}
           for rows in groups.values() for r in rows]
    panel.sort(key=lambda x:x["id"])
    meta={"url":URL,"md5":MD5,"source_rows":scanned,"n_days":n_days,"sampled":len(panel),
          "sample_id_sha256":hashlib.sha256(canonical([x["id"] for x in panel])).hexdigest(),
          "sample_rule":"SHA256 identifier, eight per state/category; not outcome-based"}
    return panel,meta

def forecast(hist,method,length=28):
    if len(hist)<56:raise ValueError("Too little training history")
    if method=="seasonal_naive":return [float(hist[-7+i%7]) for i in range(length)]
    if method=="mean28":return [statistics.fmean(hist[-28:])]*length
    if method=="mean56":return [statistics.fmean(hist[-56:])]*length
    if method=="croston_sba":
        size,interval,last=0.,1.,None
        for i,y in enumerate(hist):
            if y>0:
                if last is None:size=float(y)
                else:
                    size+=.1*(y-size)
                    interval+=.1*((i-last)-interval)
                last=i
        return [max(0.,.95*size/interval) if last is not None else 0.]*length
    raise ValueError("Unknown baseline")

def quantile(values,alpha):
    if not values:raise ValueError("Empty calibration")
    return sorted(values)[min(len(values)-1,math.ceil(alpha*len(values))-1)]

def errors(w,horizon):
    return [sum(w["actual"][i:i+horizon])-sum(w["pred"][i:i+horizon])
            for i in range(0,28-horizon+1,horizon)]

def cost(w,horizon,alpha,shift):
    return statistics.fmean(newsvendor_cost(sum(w["actual"][i:i+horizon]),
       max(0.,sum(w["pred"][i:i+horizon])+shift),alpha)
       for i in range(0,28-horizon+1,horizon))

def verify_protocol(cfg,n_days):
    if cfg["phase"]!="exploratory":raise ValueError("Must remain exploratory")
    if cfg["dev_states"]!=["CA","TX"] or cfg["sealed_state"]!="WI":
        raise ValueError("Group holdout must stay sealed")
    if cfg["methods"]!=list(METHODS):raise ValueError("Baseline list changed")
    if cfg["n_days"]!=n_days:raise ValueError("Unexpected day count")
    lo=cfg["min_history"]+(cfg["calibration_windows"]+cfg["selection_windows"])*28
    origins=cfg["origins"]; cutoff=n_days-cfg["sealed_test_days"]
    if not origins or min(origins)<lo:raise ValueError("Past calibration would leak or lack history")
    if max(origins)+28>cutoff:raise ValueError("Sealed period contaminated")
    if any(b-a<28 for a,b in zip(origins,origins[1:])):raise ValueError("Overlapping labels")
    if cfg["partial_windows"]>=cfg["selection_windows"] or cfg["calibration_windows"]<4:
        raise ValueError("Invalid historical budgets")
    if any(28%l for l in cfg["lead_times"]):raise ValueError("Lead time must divide 28")
    if any(not 0<a<1 for a in cfg["alphas"]):raise ValueError("Invalid fractile")
    return {"sealed_start_index":cutoff,"latest_dev_label_index":max(origins)+27,
            "earliest_historical_origin":min(origins)-(cfg["calibration_windows"]+cfg["selection_windows"])*28}

def evaluate_origin(y,origin,cfg):
    cal,sel=cfg["calibration_windows"],cfg["selection_windows"]
    data={}
    for method in METHODS:
        data[method]=[]
        for j in range(cal+sel+1):
            t=origin-28*j
            data[method].append({"actual":y[t:t+28],"pred":forecast(y[:t],method)})
    outcomes=[]
    for alpha in cfg["alphas"]:
        for horizon in cfg["lead_times"]:
            daily={};full={};partial={};evaluated={}
            for method in METHODS:
                w=data[method]
                def eval_at(j,L):
                    old=w[j+1:j+1+cal]
                    if len(old)!=cal:raise ValueError("Insufficient past windows")
                    shift=quantile([e for item in old for e in errors(item,L)],alpha)
                    return cost(w[j],L,alpha,shift)
                evaluated[method]=eval_at(0,horizon)
                daily[method]=statistics.fmean(eval_at(j,1) for j in range(1,sel+1))
                full[method]=statistics.fmean(eval_at(j,horizon) for j in range(1,sel+1))
                partial[method]=statistics.fmean(eval_at(j,horizon) for j in range(1,cfg["partial_windows"]+1))
            best=min(evaluated.values())  # ex-post, only for reporting evaluation regret
            selected={"daily_pinball":min(daily,key=lambda m:(daily[m],m)),
                      "partial_replay":min(partial,key=lambda m:(partial[m],m)),
                      "full_replay":min(full,key=lambda m:(full[m],m))}
            outcomes.append({"origin":origin,"alpha":alpha,"lead_time":horizon,
               "candidate_costs":evaluated,"ex_post_oracle_cost":best,
               "selected":selected,
               "regret":{k:round(max(0.,evaluated[v]-best),12) for k,v in selected.items()}})
    return outcomes

def summarize(rows):
    groups=defaultdict(list)
    for r in rows:groups[(r["lead_time"],r["alpha"])].append(r)
    out=[]
    for (lead,alpha),items in sorted(groups.items()):
        metrics={}
        for m in ("daily_pinball","partial_replay","full_replay"):
            vals=[r["regret"][m] for r in items]
            metrics[m]={"mean_ex_post_regret":statistics.fmean(vals),
                        "zero_regret_share":sum(v<1e-10 for v in vals)/len(vals)}
        by_id=defaultdict(list)
        for row in items:by_id[row["series_id"]].append(row)
        paired=[statistics.fmean(x["regret"]["daily_pinball"]-x["regret"]["full_replay"] for x in block)
                for block in by_id.values()]
        mu=statistics.fmean(paired)
        se=statistics.stdev(paired)/math.sqrt(len(paired)) if len(paired)>1 else None
        out.append({"lead_time":lead,"alpha":alpha,"n_cases":len(items),"sku_count":len(by_id),
             "methods":metrics,"daily_minus_full_regret":mu,
             "approx_95ci":[mu-1.96*se,mu+1.96*se] if se is not None else None})
    return out

def run(cfg,panel,meta):
    bounds=verify_protocol(cfg,meta["n_days"])
    rows=[]
    for item in panel:
        if item["state"] not in cfg["dev_states"]:continue
        for origin in cfg["origins"]:
            rows.extend([{"series_id":item["id"],"state":item["state"],"store":item["store"],
                          "category":item["category"],**r}
                         for r in evaluate_origin(item["y"],origin,cfg)])
    if len({r["series_id"] for r in rows})!=48:raise ValueError("Wrong development sample count")
    return {"scientific_status":"EXPLORATORY_BASELINES_ONLY_PUBLICATION_STOP",
            "protocol_sha256":hashlib.sha256(canonical(cfg)).hexdigest(),
            "data":meta,"boundaries":bounds,
            "n_cases":len(rows),"n_skus":48,"holdout_states_excluded":["WI"],
            "summary":summarize(rows),"evaluations":rows,
            "limitations":["Historical sales are not latent unconstrained demand",
                           "Candidate-oracle costs use test outcomes and are not deployable",
                           "Correlation of SKUs invalidates nominal independent CI coverage",
                           "Evaluation compute is not yet rigorously budget matched",
                           "No new method and no publication claim"]}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--config",required=True);p.add_argument("--data",default="data/raw/sales_train_validation.csv")
    p.add_argument("--output",required=True);p.add_argument("--download",action="store_true")
    args=p.parse_args();cfg=json.loads(Path(args.config).read_text())
    acquire(args.data,args.download)
    panel,meta=load_panel(args.data,n_days=cfg["n_days"],n_each=cfg["per_stratum"])
    result=run(cfg,panel,meta)
    out=Path(args.output);out.mkdir(parents=True,exist_ok=False)
    raw=canonical(result);c=canonical(cfg)
    manifest={"result_sha256":hashlib.sha256(raw).hexdigest(),
              "protocol_sha256":hashlib.sha256(c).hexdigest(),
              "dataset_md5":meta["md5"],"sample_sha256":meta["sample_id_sha256"],
              "scientific_status":"EXPLORATORY"}
    for name,body in (("results.json",raw),("config.json",c),("manifest.json",canonical(manifest))):
        write_new(out/name,body)
    print(json.dumps({"source_rows":meta["source_rows"],"dev_skus":result["n_skus"],
                      "n_cases":result["n_cases"],"boundaries":result["boundaries"],
                      "summary":result["summary"]},indent=2))

if __name__=="__main__":main()
