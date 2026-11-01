"""UCI Iris: held-out multiclass nearest-centroid classification."""
import csv
import hashlib
import math
from collections import Counter


def stable_test(i, salt="iris-uci-holdout-v1"):
    h=hashlib.sha256(f"{salt}:{i}".encode()).digest()
    return int.from_bytes(h[:8],"big")/(1<<64) < 0.25


def run(protocol, inputs):
    with inputs["dataset"].open(newline="",encoding="utf-8") as f:
        rows=[r for r in csv.reader(f) if r]
    if len(rows)!=150 or not all(len(r)==5 for r in rows):
        raise ValueError("Unexpected Iris dataset")
    dataset=[([float(v) for v in r[:4]],r[4]) for r in rows]
    labels=sorted(set(y for _,y in dataset))
    if len(labels)!=3 or any(sum(y==label for _,y in dataset)!=50 for label in labels):
        raise ValueError("Iris labels/counts invalid")
    train=[(x,y) for i,(x,y) in enumerate(dataset) if not stable_test(i)]
    test=[(x,y) for i,(x,y) in enumerate(dataset) if stable_test(i)]
    if min(Counter(y for _,y in train).values())<25 or len(test)<20:
        raise ValueError("Holdout split invalid")
    train_counts=Counter(y for _,y in train)
    majority=max(labels,key=lambda label:(train_counts[label],label))
    centroids={}
    for label in labels:
        samples=[x for x,y in train if y==label]
        centroids[label]=[sum(row[j] for row in samples)/len(samples) for j in range(4)]
    def centroid_prediction(x):
        return min(labels,key=lambda label:(sum((x[j]-centroids[label][j])**2 for j in range(4)),label))
    base=[majority]*len(test)
    model=[centroid_prediction(x) for x,_ in test]
    actual=[y for _,y in test]
    def metrics(pred):
        acc=sum(a==b for a,b in zip(pred,actual))/len(actual)
        per_class=[]
        for label in labels:
            tp=sum(p==label and y==label for p,y in zip(pred,actual))
            fp=sum(p==label and y!=label for p,y in zip(pred,actual))
            fn=sum(p!=label and y==label for p,y in zip(pred,actual))
            per_class.append(2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0)
        return {"accuracy":acc,"macro_f1":sum(per_class)/len(per_class)}
    return {"dataset":"UCI Iris 53","task":"multiclass_classification","records":len(rows),
            "train":len(train),"test":len(test),"split":"fixed SHA256 row-index 25% holdout",
            "baselines":{"train_majority":metrics(base),"nearest_centroid":metrics(model)},
            "caveats":["Illustrative single split, easy small dataset; not a new classifier",
                       "No independent external test, no scientific novelty"]}
