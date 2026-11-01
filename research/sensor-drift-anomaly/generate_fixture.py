"""Generate deterministic synthetic sensor telemetry; labels are for evaluation only."""
import csv
import random
from pathlib import Path

def generate(path):
    rng=random.Random(65021)
    faults={45,71,99,131,152,174,196,217}
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf8") as f:
        w=csv.writer(f,lineterminator="\n")
        w.writerow(["t","reading","fault","shifted"])
        for t in range(240):
            shifted=int(t>=120)
            value=rng.gauss(0,0.8)+3.0*shifted+6.0*int(t in faults)
            w.writerow([t,f"{value:.6f}",int(t in faults),shifted])

if __name__=="__main__":
    generate("data/temperature_sensor.csv")
