"""UCI bike-sharing daily counts: chronological one-step rolling forecast tests."""
import csv
import datetime as dt
import statistics as stats


def run(protocol, inputs):
    with inputs["dataset"].open(newline="",encoding="utf-8") as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=731:
        raise ValueError("Unexpected daily bike dataset length")
    if any(int(r["casual"])+int(r["registered"])!=int(r["cnt"]) for r in rows):
        raise ValueError("Leaked/incorrect demand schema")
    dates=[dt.date.fromisoformat(r["dteday"]) for r in rows]
    if any((b-a).days!=1 for a,b in zip(dates,dates[1:])):
        raise ValueError("Daily timestamps are not contiguous and chronological")
    y=[int(row["cnt"]) for row in rows]
    cutoff=int(protocol["settings"]["train_cutoff"])
    if cutoff<70 or cutoff>=len(y)-60:
        raise ValueError("Unsupported temporal holdout")
    truth=y[cutoff:]
    # Evaluation is online rolling-origin one-step ahead: only earlier realized counts.
    # No contemporaneous weather, registered or casual data are fed to predictors.
    forecasts={"last_day":[],"last_week_same_day":[],"last_28_day_mean":[]}
    for t in range(cutoff,len(y)):
        forecasts["last_day"].append(float(y[t-1]))
        forecasts["last_week_same_day"].append(float(y[t-7]))
        forecasts["last_28_day_mean"].append(stats.fmean(y[t-28:t]))
    def measures(pred):
        absolute=[abs(yy-pp) for yy,pp in zip(truth,pred)]
        return {"mae":stats.fmean(absolute),"wape":sum(absolute)/sum(truth)}
    out={name:measures(pred) for name,pred in forecasts.items()}
    return {"dataset":"UCI Bike Sharing 275 daily","task":"chronological_one_step_forecasting",
            "records":len(y),"train":cutoff,"test":len(truth),
            "train_through":str(dates[cutoff-1]),"test_from":str(dates[cutoff]),
            "test_through":str(dates[-1]),"baselines":out,
            "caveats":["One-step online forecasting: realized previous test-day demand is observable",
                       "No exogenous features used; no claim about multi-step forecasts",
                       "No modern model comparison, causal conclusions or novelty"]}
