#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd


def main():
    p = argparse.ArgumentParser(description="Create a short markdown report from benchmark tables")
    p.add_argument("--summary", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    df = pd.read_csv(args.summary)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# SSVEP-FBCCA wearability benchmark summary", ""]
    lines.append("This report is generated from benchmark outputs. No claims are made beyond these data.")
    lines.append("")
    if not df.empty:
        lines.append("## Best FBCCA condition by mean accuracy")
        fbcca = df[df["method"] == "fbcca"].copy()
        if not fbcca.empty:
            best = fbcca.sort_values("mean_accuracy", ascending=False).iloc[0]
            lines.append(best.to_frame().T.to_markdown(index=False))
            lines.append("")
        lines.append("## Full summary")
        lines.append(df.to_markdown(index=False))
    out.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
