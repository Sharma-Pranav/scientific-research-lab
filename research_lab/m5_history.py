"""M5 historical-selection-length falsification; development-only, no holdout access."""
import argparse
import hashlib
import json
import math
import statistics as stats
from collections import defaultdict
from pathlib import Path

from research_lab.engine import write_new
from research_lab.leadtime import canonical, newsvendor_cost
from research_lab.m5_baselines import (
    METHODS, acquire, cost, errors, forecast, load_panel, quantile, verify_protocol
)

def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()

def validate(cfg, base):
    if cfg["phase"] != "exploratory" or cfg["publication_gate"] != "STOP":
        raise ValueError("This is exploratory; no publication approval")
    if cfg["base_protocol_sha256"] != digest(base):
        raise ValueError("Baseline protocol mismatch")
    for key in ("n_days","origins","dev_states","sealed_state","sealed_test_days",
                "lead_times","alphas","calibration_windows","selection_windows",
                "methods","per_stratum"):
        if cfg[key] != base[key]:
            raise ValueError("Changed original experimental conditions: "+key)
    if cfg["history_lengths"] != [1,3,6,12] or cfg["selection_windows"]!=12:
        raise ValueError("Invalid prespecified history lengths")
    if cfg["regime_threshold"] != 0.5:
        raise ValueError("Changed exploratory regime threshold")
    return verify_protocol(base,cfg["n_days"])

def shift_score(y, origin):
    # Both windows end before the forecast origin.
    a=stats.fmean(y[origin-28:origin])
    b=stats.fmean(y[origin-84:origin-28])
    return abs(a-b)/(1+b)

def matched_daily_errors(w,L):
    return [w["actual"][i]-w["pred"][i] for i in range(0,28,L)]

def matched_daily_cost(w,L,alpha,correction):
    # Same number of scored loss terms as lead-time policy replay.
    return stats.fmean(newsvendor_cost(w["actual"][i],
              max(0.,w["pred"][i]+correction),alpha) for i in range(0,28,L))

def windows(y,origin,cal,sel):
    return {m: [{"actual":y[origin-28*j:origin-28*j+28],
                   "pred":forecast(y[:origin-28*j],m)}
                  for j in range(cal+sel+1)] for m in METHODS}

def scores_for_method(w,L,alpha,cal,sel):
    past={"policy":[],"daily_matched":[],"daily_full":[]}
    for j in range(1,sel+1):
        older=w[j+1:j+1+cal]
        if len(older)!=cal: raise ValueError("Missing past calibration windows")
        ql=quantile([v for x in older for v in errors(x,L)],alpha)
        q1=quantile([v for x in older for v in errors(x,1)],alpha)
        qm=quantile([v for x in older for v in matched_daily_errors(x,L)],alpha)
        past["policy"].append(cost(w[j],L,alpha,ql))
        past["daily_full"].append(cost(w[j],1,alpha,q1))
        past["daily_matched"].append(matched_daily_cost(w[j],L,alpha,qm))
    q0=quantile([v for x in w[1:cal+1] for v in errors(x,L)],alpha)
    future=cost(w[0],L,alpha,q0)
    return past,future

def evaluate_origin(y,origin,cfg):
    cal=cfg["calibration_windows"];sel=cfg["selection_windows"]
    w=windows(y,origin,cal,sel)
    score=shift_score(y,origin)
    out=[]
    for L in cfg["lead_times"]:
        for alpha in cfg["alphas"]:
            histories={};future={}
            for m in METHODS:
                histories[m],future[m]=scores_for_method(w[m],L,alpha,cal,sel)
            best=min(future.values())
            selections={}
            for k in cfg["history_lengths"]:
                for family in ("policy","daily_matched","daily_full"):
                    ranking={m:stats.fmean(histories[m][family][:k]) for m in METHODS}
                    winner=min(ranking,key=lambda m:(ranking[m],m))
                    name=family+"_"+str(k)
                    selections[name]={
                        "winner":winner,"regret":max(0.,future[winner]-best),
                        "loss_terms_per_model":k*(28 if family=="daily_full" else 28//L),
                        "history_windows":k}
            out.append({"origin":origin,"lead_time":L,"alpha":alpha,
                        "past_instability":score,
                        "instability_bin":"high" if score>cfg["regime_threshold"] else "low",
                        "candidate_costs":future,"ex_post_best":best,
                        "selections":selections})
    return out

def paired(rows,a,b):
    by_store=defaultdict(list)
    for row in rows:
        by_store[row["store"]].append(row["selections"][a]["regret"]-
                                    row["selections"][b]["regret"])
    store_mean={k:stats.fmean(v) for k,v in sorted(by_store.items())}
    vals=list(store_mean.values());mean=stats.fmean(vals)
    se=stats.stdev(vals)/math.sqrt(len(vals)) if len(vals)>1 else None
    return {"A_minus_B":mean,"n_stores":len(vals),"per_store":store_mean,
            "approx_normal_95ci":[mean-1.96*se,mean+1.96*se] if se else None,
            "limitations":"Descriptive store-block approximation, not independent sampling"}

def summarize(rows,cfg):
    groups=defaultdict(list)
    for x in rows:groups[(x["lead_time"],x["alpha"])].append(x)
    out=[]
    for (L,alpha),items in sorted(groups.items()):
        methods={}
        for k in cfg["history_lengths"]:
            for fam in ("policy","daily_matched","daily_full"):
                name=fam+"_"+str(k)
                vals=[x["selections"][name]["regret"] for x in items]
                methods[name]={"mean_regret":stats.fmean(vals),
                               "zero_regret_share":sum(v<1e-10 for v in vals)/len(vals),
                               "selection_loss_terms_per_model":items[0]["selections"][name]["loss_terms_per_model"]}
        regimes={}
        for band in ("high","low"):
            part=[x for x in items if x["instability_bin"]==band]
            regimes[band]={"n_cases":len(part),
                "policy_12_minus_policy_3_regret":stats.fmean(
                    x["selections"]["policy_12"]["regret"]-
                    x["selections"]["policy_3"]["regret"] for x in part) if part else None}
        out.append({"lead_time":L,"alpha":alpha,"n_cases":len(items),
                    "methods":methods,"regime_slices":regimes,
                    "policy_12_minus_policy_3":paired(items,"policy_12","policy_3"),
                    "policy_3_minus_daily_matched_3":paired(items,"policy_3","daily_matched_3"),
                    "policy_12_minus_daily_full_12":paired(items,"policy_12","daily_full_12")})
    return out

def run(cfg,base,panel,meta):
    bounds=validate(cfg,base)
    rows=[]
    for item in panel:
        if item["state"] not in cfg["dev_states"]:
            continue
        for origin in cfg["origins"]:
            rows.extend({"series_id":item["id"],"store":item["store"],"state":item["state"],
                         "category":item["category"],**x} for x in evaluate_origin(item["y"],origin,cfg))
    n=cfg["per_stratum"]*6
    if len({x["series_id"] for x in rows})!=n:
        raise ValueError("Incorrect development sample count")
    return {"phase":"exploratory","publication_gate":"STOP",
            "protocol_sha256":digest(cfg),"base_protocol_sha256":digest(base),
            "dataset":meta,"bounds":bounds,"n_cases":len(rows),"n_skus":n,
            "holdout_excluded":{"state":"WI","last_days":cfg["sealed_test_days"]},
            "summaries":summarize(rows,cfg),"rows":rows,
            "caveats":["Loss-term matching is not compute or information matching",
                       "Store intervals are descriptive only",
                       "Observed sales are not necessarily uncensored demand",
                       "History and regime comparisons are exploratory and not causal",
                       "No new algorithm, strong forecast model or novel claim"]}

def audit(folder,config_file,base_file):
    folder=Path(folder)
    config=json.loads((folder/"config.json").read_bytes())
    base=json.loads(Path(base_file).read_bytes())
    manifest=json.loads((folder/"manifest.json").read_bytes())
    raw=(folder/"results.json").read_bytes()
    result=json.loads(raw)
    if config!=json.loads(Path(config_file).read_bytes()):
        raise ValueError("Protocol reference mismatch")
    if hashlib.sha256(raw).hexdigest()!=manifest["results_sha256"]:
        raise ValueError("Results hash mismatch")
    if digest(config)!=manifest["protocol_sha256"] or digest(base)!=manifest["base_protocol_sha256"]:
        raise ValueError("Protocol hash mismatch")
    validate(config,base)
    expected=config["per_stratum"]*6*len(config["origins"])*len(config["lead_times"])*len(config["alphas"])
    rows=result["rows"]
    if len(rows)!=expected or result["n_cases"]!=expected:raise ValueError("Missing result cells")
    if {x["state"] for x in rows}!={"CA","TX"}:raise ValueError("Group holdout leaked")
    if result["holdout_excluded"]!={"state":"WI","last_days":config["sealed_test_days"]}:
        raise ValueError("Temporal or group holdout changed")
    for x in rows:
        costs=x["candidate_costs"]; best=min(costs.values())
        if abs(best-x["ex_post_best"])>1e-8:raise ValueError("Ex-post oracle mismatch")
        if set(costs)!=set(METHODS):raise ValueError("Baseline list mismatch")
        for name,v in x["selections"].items():
            if v["winner"] not in costs:raise ValueError("Invalid selected method")
            if abs(v["regret"]-max(0.,costs[v["winner"]]-best))>1e-8:
                raise ValueError("Stored regret mismatch")
    if canonical(result["summaries"])!=canonical(summarize(rows,config)):
        raise ValueError("Summary mismatch")
    return {"status":"PASS","n_cases":len(rows),"n_skus":result["n_skus"],
            "results_sha256":manifest["results_sha256"]}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--config",required=True)
    p.add_argument("--base-config",default="research/selection-transfer/m5_development.json")
    p.add_argument("--data",default="data/raw/sales_train_validation.csv")
    p.add_argument("--output",required=True)
    p.add_argument("--download",action="store_true")
    p.add_argument("--verify",action="store_true")
    args=p.parse_args()
    if args.verify:
        print(json.dumps(audit(args.output,args.config,args.base_config),sort_keys=True));return
    cfg=json.loads(Path(args.config).read_text())
    base=json.loads(Path(args.base_config).read_text())
    validate(cfg,base)
    acquire(args.data,args.download)
    panel,meta=load_panel(args.data,n_days=cfg["n_days"],n_each=cfg["per_stratum"])
    res=run(cfg,base,panel,meta)
    out=Path(args.output);out.mkdir(parents=True,exist_ok=False)
    raw=canonical(res)
    manifest={"protocol_sha256":digest(cfg),"base_protocol_sha256":digest(base),
              "results_sha256":hashlib.sha256(raw).hexdigest(),
              "dataset_md5":meta["md5"],"sample_id_sha256":meta["sample_id_sha256"],
              "status":"EXPLORATORY_PUBLICATION_STOP"}
    for name,body in (("config.json",canonical(cfg)),("results.json",raw),
                      ("manifest.json",canonical(manifest))):
        write_new(out/name,body)
    print(json.dumps({"status":"EXPLORATORY_COMPLETE","n_cases":res["n_cases"],
                      "n_skus":res["n_skus"],"protocol_sha256":digest(cfg),
                      "results_sha256":manifest["results_sha256"],
                      "summaries":res["summaries"]},indent=2))

if __name__=="__main__":
    main()
