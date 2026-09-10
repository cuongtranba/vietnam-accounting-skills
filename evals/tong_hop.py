#!/usr/bin/env python3
"""Gộp grading.json + timing.json của các lượt chạy thành benchmark.json cho eval viewer.

    python3 tong_hop.py <thu_muc_iteration>

Script aggregate_benchmark của skill-creator mong một bố cục thư mục khác nên không đọc được
workspace này; đây là bản tối thiểu sinh đúng schema viewer cần.

Cách tính pass_rate: các tiêu chí 'chờ người xem' (passed = None) KHÔNG tính vào mẫu số. Tính
chúng là trượt sẽ phạt oan cả hai cấu hình; tính là đạt sẽ thổi phồng điểm. Loại ra là cách
trung thực duy nhất — và số tiêu chí chờ người xem được ghi riêng để không bị giấu đi.
"""
from __future__ import annotations

import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

CAU_HINH = ("with_skill", "without_skill")


def thong_ke(ds: list[float]) -> dict:
    if not ds:
        return {"mean": 0, "stddev": 0, "min": 0, "max": 0}
    return {
        "mean": round(statistics.mean(ds), 4),
        "stddev": round(statistics.stdev(ds), 4) if len(ds) > 1 else 0.0,
        "min": round(min(ds), 4),
        "max": round(max(ds), 4),
    }


def main() -> int:
    goc = Path(sys.argv[1]).expanduser()
    runs, theo_cau_hinh = [], {c: {"pr": [], "t": [], "tok": []} for c in CAU_HINH}

    for d in sorted(goc.iterdir()):
        meta_f = d / "eval_metadata.json"
        if not d.is_dir() or not meta_f.exists():
            continue
        meta = json.loads(meta_f.read_text(encoding="utf-8"))

        for cfg in CAU_HINH:
            g_f, t_f = d / cfg / "grading.json", d / cfg / "timing.json"
            if not g_f.exists():
                continue
            g = json.loads(g_f.read_text(encoding="utf-8"))
            t = json.loads(t_f.read_text(encoding="utf-8")) if t_f.exists() else {}

            exps = g["expectations"]
            cham_duoc = [e for e in exps if e["passed"] is not None]
            dat = sum(1 for e in cham_duoc if e["passed"])
            pr = dat / len(cham_duoc) if cham_duoc else 0.0
            giay = t.get("total_duration_seconds", 0)
            tok = t.get("total_tokens", 0)

            runs.append({
                "eval_id": meta["eval_id"],
                "eval_name": meta["eval_name"],
                "configuration": cfg,
                "run_number": 1,
                "result": {
                    "pass_rate": round(pr, 4),
                    "passed": dat,
                    "failed": len(cham_duoc) - dat,
                    "total": len(cham_duoc),
                    "needs_review": len(exps) - len(cham_duoc),
                    "time_seconds": giay,
                    "tokens": tok,
                    "tool_calls": t.get("tool_uses", 0),
                    "errors": 0,
                },
                "expectations": exps,
                "notes": [f"{len(exps) - len(cham_duoc)} tiêu chí cần người xem đánh giá"]
                if len(exps) > len(cham_duoc) else [],
            })
            theo_cau_hinh[cfg]["pr"].append(pr)
            theo_cau_hinh[cfg]["t"].append(giay)
            theo_cau_hinh[cfg]["tok"].append(tok)

    # with_skill đứng trước bản đối chứng của nó trong viewer
    runs.sort(key=lambda r: (r["eval_id"], r["configuration"] != "with_skill"))

    tt = {c: {"pass_rate": thong_ke(v["pr"]),
              "time_seconds": thong_ke(v["t"]),
              "tokens": thong_ke(v["tok"])}
          for c, v in theo_cau_hinh.items()}
    tt["delta"] = {
        "pass_rate": f"{tt['with_skill']['pass_rate']['mean'] - tt['without_skill']['pass_rate']['mean']:+.4f}",
        "time_seconds": f"{tt['with_skill']['time_seconds']['mean'] - tt['without_skill']['time_seconds']['mean']:+.1f}",
        "tokens": f"{tt['with_skill']['tokens']['mean'] - tt['without_skill']['tokens']['mean']:+.0f}",
    }

    bm = {
        "metadata": {
            "skill_name": "ke-toan-vn",
            "skill_path": str(Path(__file__).resolve().parent.parent
                              / "skills" / "ke-toan-vn"),
            "executor_model": "claude-opus-5",
            "analyzer_model": "claude-opus-5",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "evals_run": sorted({r["eval_id"] for r in runs}),
            "runs_per_configuration": 1,
        },
        "runs": runs,
        "run_summary": tt,
    }
    (goc / "benchmark.json").write_text(
        json.dumps(bm, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"{'Ca thử':<34}{'có skill':>22}{'không skill':>22}")
    for eid in bm["metadata"]["evals_run"]:
        hang = {r["configuration"]: r for r in runs if r["eval_id"] == eid}
        ten = next(iter(hang.values()))["eval_name"]
        o = []
        for c in CAU_HINH:
            r = hang.get(c)
            o.append(f"{r['result']['passed']}/{r['result']['total']} ({r['result']['pass_rate']:.0%})"
                     f" {r['result']['time_seconds']:.0f}s" if r else "—")
        print(f"{ten:<34}{o[0]:>22}{o[1]:>22}")
    print()
    print(f"{'TRUNG BÌNH':<34}"
          f"{tt['with_skill']['pass_rate']['mean']:>21.0%} "
          f"{tt['without_skill']['pass_rate']['mean']:>21.0%}")
    print(f"Delta pass_rate: {tt['delta']['pass_rate']}  |  "
          f"thời gian: {tt['delta']['time_seconds']}s  |  token: {tt['delta']['tokens']}")
    print(f"\nĐã ghi {goc / 'benchmark.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
