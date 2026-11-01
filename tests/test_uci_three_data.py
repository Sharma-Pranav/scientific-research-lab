"""Non-network tests for independent domain adapters and archive validation."""
import csv
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path

from research_lab.study import execute


ROOT = Path(__file__).resolve().parents[1]


def module(rel):
    filename = ROOT / rel
    spec = importlib.util.spec_from_file_location("test_plugin_"+filename.stem, filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


class ThreeCuratedUciTests(unittest.TestCase):
    def test_iris_split_deterministic_and_roughly_balanced(self):
        iris = module("research/uci-iris-classification/experiment.py")
        selection = [iris.stable_test(i) for i in range(150)]
        self.assertEqual(selection, [iris.stable_test(i) for i in range(150)])
        self.assertTrue(20 <= sum(selection) <= 60)

    def test_wine_split_deterministic_and_holdout_sized(self):
        wine = module("research/uci-wine-regression/experiment.py")
        n = sum(wine.stable_test(i) for i in range(1599))
        self.assertTrue(250 <= n <= 380)

    def test_iris_runner_on_non_uci_fixture(self):
        iris = module("research/uci-iris-classification/experiment.py")
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/"flowers.csv"
            labels=("Iris-setosa","Iris-versicolor","Iris-virginica")
            with source.open("w",newline="") as handle:
                writer=csv.writer(handle)
                for label,offset in zip(labels,(1.,5.,10.)):
                    for i in range(50):
                        writer.writerow([offset+i/100,offset+1,offset+2,offset+3,label])
            result=iris.run({},{"dataset":source})
            self.assertEqual(result["records"],150)
            self.assertGreater(result["baselines"]["nearest_centroid"]["accuracy"],0.95)
            self.assertGreater(result["baselines"]["nearest_centroid"]["accuracy"],
                               result["baselines"]["train_majority"]["accuracy"])

    def test_wine_runner_train_only_fit_on_fixture(self):
        wine=module("research/uci-wine-regression/experiment.py")
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/"wine.csv"
            cols=["fixed acidity","volatile acidity","citric acid","residual sugar",
                  "chlorides","free sulfur dioxide","total sulfur dioxide","density",
                  "pH","sulphates","alcohol","quality"]
            with source.open("w",newline="") as handle:
                writer=csv.DictWriter(handle,fieldnames=cols,delimiter=";")
                writer.writeheader()
                for i in range(1599):
                    value=8.0+(i%19)*0.2
                    writer.writerow({**{k:"1.0" for k in cols},
                                      "alcohol":str(value),
                                      "quality":str(4+0.4*value)})
            result=wine.run({},{"dataset":source})
            self.assertEqual(result["records"],1599)
            self.assertLess(result["baselines"]["alcohol_only_ols"]["mae"],1e-8)

    def test_bike_runner_validates_daily_order_and_identity(self):
        bike=module("research/uci-bike-forecasting/experiment.py")
        from datetime import date,timedelta
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/"day.csv"
            with source.open("w",newline="") as handle:
                writer=csv.DictWriter(handle,fieldnames=["dteday","casual","registered","cnt"])
                writer.writeheader()
                for day in range(731):
                    dt=date(2011,1,1)+timedelta(days=day)
                    writer.writerow({"dteday":str(dt),"casual":1,"registered":9+day%7,
                                     "cnt":10+day%7})
            result=bike.run({"settings":{"train_cutoff":611}},{"dataset":source})
            self.assertEqual((result["train"],result["test"]),(611,120))
            self.assertAlmostEqual(result["baselines"]["last_week_same_day"]["mae"],0)
            with source.open("w") as handle:
                handle.write("dteday,casual,registered,cnt\n")
                handle.write("2011-01-01,1,2,100\n")
            with self.assertRaises(ValueError):
                bike.run({"settings":{"train_cutoff":611}},{"dataset":source})

    def test_source_validation_fails_closed(self):
        acquire=module("research/curated-three-datasets/acquire.py")
        for key in acquire.CATALOG:
            with self.assertRaises((ValueError,KeyError)):
                acquire.parse_count(key,b"wrong,source\n1,2\n")


if __name__ == "__main__":
    unittest.main()
