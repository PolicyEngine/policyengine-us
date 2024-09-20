import yaml

with open("speedtest_old.yaml", "r") as f:
    old = yaml.safe_load(f)

with open("speedtest_new.yaml", "r") as f:
    new = yaml.safe_load(f)

import pandas as pd

df = pd.DataFrame(
    {
        "import": [old["import"], new["import"]],
        "run": [old["run"], new["run"]],
    }
)
df["total"] = df["import"] + df["run"]
df = df.T
df.columns = ["old", "new"]
df["change"] = df["new"] - df["old"]
df["percent_change"] = df["change"] / df["old"] * 100
print("Comparison of speedtest results:")
print(df.to_markdown())

rel_change = df.percent_change.values[-1]

if rel_change < 0:
    print("Nice! The new version is faster.")
elif rel_change < 5:
    print("The new version is slightly slower.")
elif rel_change < 100:
    print(
        "WARNING: The new version is significantly slower. PLEASE make sure to check nothing's super unnecessarily slow."
    )
else:
    raise ValueError(
        "The new version is WAY slower (over double runtime). Please check what's going on. Throwing this error."
    )
