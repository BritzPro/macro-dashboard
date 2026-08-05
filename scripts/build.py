# -*- coding: utf-8 -*-
"""조립 단계: 수집 + 해석 결과를 docs/data/indicators.json 하나로 합친다.

단일 책임: '조립하고 파일로 쓰는 일'만 한다.
GitHub Pages는 docs/ 폴더를 서빙하므로 데이터도 docs/data/ 아래에 둔다.
"""
import os
import json
from datetime import datetime, timezone

from fetch import fetch_all
from interpret import interpret
from config import AXES, AXIS_GUIDE

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "data")
OUT_PATH = os.path.join(OUT_DIR, "indicators.json")


def main():
    fetched, mode = fetch_all()
    signals = interpret(fetched)

    sample_ids = [k for k, v in fetched.items() if v.get("data_source") == "sample"]
    data_status = {
        "total": len(fetched),
        "sample": len(sample_ids),
        "real": len(fetched) - len(sample_ids),
        "sample_ids": sample_ids,
    }

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": mode,  # "fred" 또는 "sample"
        "data_status": data_status,
        "axes": AXES,
        "overall": signals["overall"],
        "axis_signal": signals["axis_signal"],
        "commentary": signals["commentary"],
        "axis_guide": AXIS_GUIDE,
        "indicators": fetched,
    }

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    # 로컬에서 HTML을 그냥 더블클릭해도 열리도록 JS 형태로도 내보낸다
    # (file:// 에서는 fetch가 막히므로 script 태그로 주입)
    js_path = os.path.join(OUT_DIR, "data.js")
    with open(js_path, "w", encoding="utf-8") as f:
        f.write("window.__MACRO_DATA__ = ")
        json.dump(payload, f, ensure_ascii=False)
        f.write(";")

    print(f"완료 → {os.path.relpath(OUT_PATH)}")
    print(f"실데이터 {data_status['real']}/{data_status['total']}개, "
          f"샘플폴백 {data_status['sample']}개 {sample_ids or ''}, "
          f"종합신호={signals['overall']['label']}")


if __name__ == "__main__":
    main()
