"""Null Monte Carlo: false positives from repeated A/B significance checks."""
import math
import random
import statistics as stats
from statistics import NormalDist

def run(protocol,inputs):
    if inputs:
        raise ValueError("This experiment uses no external dataset")
    cfg=protocol["settings"]
    n_per_look=int(cfg["observations_per_arm_per_look"])
    checks=int(cfg["looks"])
    reps=int(cfg["replicates_per_seed"])
    alpha=float(cfg["alpha"])
    if n_per_look<2 or checks<2 or reps<100 or not 0<alpha<1:
        raise ValueError("Invalid simulation design")
    normal=NormalDist()
    rows=[]
    for seed in protocol["seeds"]:
        rng=random.Random(seed)
        any_nominal=any_bonf=fixed=0
        for _ in range(reps):
            sa=sb=0.0
            saw_nominal=saw_bonf=False
            for look in range(1,checks+1):
                for _ in range(n_per_look):
                    sa+=rng.gauss(0,1)
                    sb+=rng.gauss(0,1)
                n=look*n_per_look
                z=abs((sa-sb)/n)/math.sqrt(2/n)
                p=2*(1-normal.cdf(z))
                saw_nominal |= p<alpha
                saw_bonf |= p<alpha/checks
                if look==checks:
                    fixed+=int(p<alpha)
            any_nominal+=int(saw_nominal)
            any_bonf+=int(saw_bonf)
        rows.append({"seed":seed,"replicates":reps,
                     "false_positive_any_unadjusted":any_nominal/reps,
                     "false_positive_any_bonferroni":any_bonf/reps,
                     "false_positive_fixed_final":fixed/reps})
    rates={k:stats.fmean(row[k] for row in rows) for k in
           ("false_positive_any_unadjusted","false_positive_any_bonferroni","false_positive_fixed_final")}
    return {"kind":"sequential_testing_null_monte_carlo","true_effect":0.0,
            "n_seeds":len(rows),"total_replicates":len(rows)*reps,
            "false_positive_rates":rates,"by_seed":rows,
            "warning":"Simulation of a known multiple-testing mechanism, not a novel discovery"}
