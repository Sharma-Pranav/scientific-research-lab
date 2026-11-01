"""Synthetic drift/anomaly-detection benchmark; not real industrial validation."""
import csv
import statistics as stats

def confusion(predictions,labels,indices):
    tp=sum(predictions[i] and labels[i] for i in indices)
    fp=sum(predictions[i] and not labels[i] for i in indices)
    fn=sum(not predictions[i] and labels[i] for i in indices)
    tn=sum(not predictions[i] and not labels[i] for i in indices)
    return {"tp":tp,"fp":fp,"fn":fn,"tn":tn,
            "precision":tp/(tp+fp) if tp+fp else 0.0,
            "recall":tp/(tp+fn) if tp+fn else 0.0,
            "false_positive_rate":fp/(fp+tn) if fp+tn else 0.0}

def run(protocol,inputs):
    with inputs["telemetry"].open(encoding="utf8",newline="") as f:
        rows=list(csv.DictReader(f))
    x=[float(r["reading"]) for r in rows]
    y=[int(r["fault"]) for r in rows]
    shifted=[int(r["shifted"]) for r in rows]
    if len(x)!=240 or [int(r["t"]) for r in rows]!=list(range(240)):
        raise ValueError("Unexpected sensor fixture shape")
    s=protocol["settings"]
    calibration=int(s["calibration_points"])
    window=int(s["rolling_window"])
    threshold=float(s["threshold"])
    if any(y[:calibration]) or any(shifted[:calibration]):
        raise ValueError("Training calibration contains labeled faults or drift")
    baseline_mu=stats.fmean(x[:calibration])
    baseline_sd=stats.stdev(x[:calibration])
    fixed=[int(abs(v-baseline_mu)>threshold*baseline_sd) for v in x]
    rolling=[]
    for t,value in enumerate(x):
        if t<calibration:
            rolling.append(0)
            continue
        history=x[max(0,t-window):t]
        center=stats.median(history)
        mad=stats.median([abs(v-center) for v in history])
        robust_sd=max(1.4826*mad,float(s["mad_floor"]))
        rolling.append(int(abs(value-center)>threshold*robust_sd))
    after=range(calibration,len(x))
    def regimes(pred):
        return {
            "overall":confusion(pred,y,after),
            "before_shift":confusion(pred,y,[i for i in after if not shifted[i]]),
            "after_shift":confusion(pred,y,[i for i in after if shifted[i]]),
        }
    return {"kind":"synthetic_sensor_drift_comparison",
            "calibration":{"n":calibration,"baseline_mean":baseline_mu,"baseline_sd":baseline_sd},
            "methods":{"fixed_3sigma":regimes(fixed),"past_rolling_mad":regimes(rolling)},
            "n_observations":len(x),"n_faults_after_calibration":sum(y[calibration:]),
            "note":"Designed synthetic fixture; not an external validation or novel mechanism"}
