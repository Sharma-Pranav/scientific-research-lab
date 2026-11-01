"""Fetch three genuine curated UCI datasets, preserving licenses and fingerprints.

Only named expected files are extracted from their official UCI repository ZIPs.
No synthetic or fallback data is ever substituted on failure.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import urllib.request
import zipfile
from pathlib import Path

CATALOG = {
    "iris": {
        "url": "https://archive.ics.uci.edu/static/public/53/iris.zip",
        "member": "iris.data",
        "output": "data/curated/iris.data",
        "rows": 150, "uci_id": 53, "doi": "10.24432/C56C76",
        "license": "CC BY 4.0",
    },
    "wine_quality_red": {
        "url": "https://archive.ics.uci.edu/static/public/186/wine+quality.zip",
        "member": "winequality-red.csv",
        "output": "data/curated/winequality-red.csv",
        "rows": 1599, "uci_id": 186, "doi": "10.24432/C56S3T",
        "license": "CC BY 4.0",
    },
    "bike_sharing_daily": {
        "url": "https://archive.ics.uci.edu/static/public/275/bike+sharing+dataset.zip",
        "member": "day.csv",
        "output": "data/curated/day.csv",
        "rows": 731, "uci_id": 275, "doi": "10.24432/C5W894",
        "license": "CC BY 4.0",
    },
}


def digest(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def parse_count(dataset, raw):
    if dataset == "iris":
        rows = [row for row in csv.reader(io.StringIO(raw.decode("utf-8"))) if row]
        if len(rows) != 150 or not all(len(r) == 5 for r in rows):
            raise ValueError("Iris row/column schema invalid")
        if set(r[4] for r in rows) != {"Iris-setosa", "Iris-versicolor", "Iris-virginica"}:
            raise ValueError("Iris classes invalid")
    elif dataset == "wine_quality_red":
        r = list(csv.DictReader(io.StringIO(raw.decode("utf-8")), delimiter=";"))
        if len(r) != 1599 or len(r[0]) != 12 or "quality" not in r[0]:
            raise ValueError("Red wine row/column schema invalid")
        rows = r
    elif dataset == "bike_sharing_daily":
        r = list(csv.DictReader(io.StringIO(raw.decode("utf-8"))))
        if len(r) != 731 or "cnt" not in r[0] or "dteday" not in r[0]:
            raise ValueError("Bike sharing row/column schema invalid")
        if any(int(x["casual"])+int(x["registered"]) != int(x["cnt"]) for x in r):
            raise ValueError("Daily bike counts do not sum")
        rows = r
    else:
        raise ValueError("Unknown dataset")
    return len(rows)


def fetch_one(name, base="."):
    spec = CATALOG[name]
    req=urllib.request.Request(spec["url"],headers={"User-Agent":"research-lab-curated-dataset-validation/1.0"})
    with urllib.request.urlopen(req,timeout=120) as response:
        payload=response.read(5*1024*1024)
    if not zipfile.is_zipfile(io.BytesIO(payload)):
        raise ValueError("Expected official UCI ZIP, received another document")
    with zipfile.ZipFile(io.BytesIO(payload)) as bundle:
        matching=[member for member in bundle.namelist() if Path(member).name == spec["member"]]
        if len(matching)!=1:
            raise ValueError(f"Expected one member {spec['member']}, got {matching}")
        raw=bundle.read(matching[0])
    n=parse_count(name,raw)
    output=Path(base)/spec["output"]
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_bytes(raw)
    return {"id":name,"source":spec["url"],"member":spec["member"],
            "path":spec["output"],"archive_sha256":digest(payload),
            "file_sha256":digest(raw),"file_bytes":len(raw),"rows":n,
            "uci_id":spec["uci_id"],"doi":spec["doi"],"license":spec["license"]}


def acquire_all(base=".", expected_hashes=None):
    records={}
    for name in CATALOG:
        row=fetch_one(name,base)
        if expected_hashes is not None:
            want=expected_hashes.get(name)
            if not isinstance(want,str) or len(want)!=64 or want!=row["file_sha256"]:
                raise ValueError(f"Curated source file hash mismatch or missing pin: {name}")
        records[name]=row
    return records


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",default=".")
    p.add_argument("--expected-hashes",default=None)
    a=p.parse_args()
    pins=json.loads(Path(a.expected_hashes).read_text()) if a.expected_hashes else None
    records=acquire_all(a.root,pins)
    print(json.dumps(records,indent=2,sort_keys=True))
    out=Path(a.root)/"data/curated/source_manifest.json"
    out.write_text(json.dumps(records,indent=2,sort_keys=True)+"\n")


if __name__=="__main__":main()
