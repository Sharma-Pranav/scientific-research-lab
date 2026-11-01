"""UCI red wine quality: held-out univariate regression with train-only fit."""
import csv
import hashlib
import math
import statistics as stats


def stable_test(i):
    h=hashlib.sha256(f"red-wine-uci-holdout-v1:{i}".encode()).digest()
    return int.from_bytes(h[:8],"big")/(1<<64) < 0.2


def run(protocol, inputs):
    with inputs["dataset"].open(newline="",encoding="utf-8") as f:
        rows=list(csv.DictReader(f,delimiter=";"))
    if len(rows)!=1599 or "alcohol" not in rows[0] or "quality" not in rows[0]:
        raise ValueError("Unexpected Wine Quality source")
    series=[(float(row["alcohol"]),float(row["quality"])) for row in rows]
    train=[r for i,r in enumerate(series) if not stable_test(i)]
    test=[r for i,r in enumerate(series) if stable_test(i)]
    if len(test)<250 or len(train)<1200:
        raise ValueError("Holdout split invalid")
    xbar=stats.fmean(x for x,y in train)
    ybar=stats.fmean(y for x,y in train)
    denominator=sum((x-xbar)**2 for x,y in train)
    if denominator <= 0:
        raise ValueError("Alcohol feature is constant")
    slope=sum((x-xbar)*(y-ybar) for x,y in train)/denominator
    offset=ybar-slope*xbar
    actual=[y for x,y in test]
    predictions={"train_mean":[ybar]*len(test),
                 "alcohol_only_ols":[offset+slope*x for x,y in test]}
    def metrics(pred):
        errors=[y-p for y,p in zip(actual,pred)]
        return {"mae":stats.fmean(abs(e) for e in errors),
                "rmse":math.sqrt(stats.fmean(e*e for e in errors))}
    return {"dataset":"UCI Wine Quality 186 red","task":"quality_score_regression",
            "records":len(rows),"train":len(train),"test":len(test),
            "split":"fixed SHA256 row-index 20% holdout",
            "baselines":{m:metrics(p) for m,p in predictions.items()},
            "fit":{"train_mean_quality":ybar,"alcohol_slope":slope},
            "caveats":["Quality is a subjective ordered score, treated illustratively as continuous",
                       "Only alcohol used; no claim about best models, causal chemistry or novelty"]}
