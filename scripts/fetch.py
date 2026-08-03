# -*- coding: utf-8 -*-
"""수집 단계: 모든 지표의 시계열을 가져와 latest/prev/change를 계산한다.

단일 책임: '데이터를 가져오는 일'만 한다. 해석·판정은 interpret.py가 맡는다.
지표 도메인(금리/유동성/위험선호/물가/시장)은 config.INDICATORS의 axis 필드로
구분되며, 여기서는 그 목록을 그대로 순회한다.
"""
from config import INDICATORS
from fred import fetch_series
import sources


def _fetch_one(ind):
    """지표의 source 필드에 따라 알맞은 취득 함수로 분기한다."""
    src = ind.get("source", "fred")
    if src == "yahoo":
        return sources.fetch_yahoo(ind["symbol"], ind["id"], ind["freq"])
    if src == "cboe":
        return sources.fetch_cboe(ind["symbol"], ind["id"], ind["freq"])
    if src == "vix_ts":
        return sources.fetch_vix_termstructure(ind["id"], ind["freq"])
    return fetch_series(ind["id"], ind["freq"])


def _change(points):
    """마지막 두 관측치로 변화량/변화율을 계산한다."""
    if len(points) < 2:
        return None, None
    prev, last = points[-2]["value"], points[-1]["value"]
    diff = last - prev
    pct = (diff / prev * 100) if prev else None
    return diff, pct


def fetch_all():
    """지표 id -> 수집 결과 dict."""
    result = {}
    modes = []
    for ind in INDICATORS:
        points, mode = _fetch_one(ind)
        modes.append(mode)
        diff, pct = _change(points)
        result[ind["id"]] = {
            "id": ind["id"],
            "name": ind["name"],
            "axis": ind["axis"],
            "cadence": ind["cadence"],
            "unit": ind["unit"],
            "meaning": ind["meaning"],
            "read": ind["read"],
            "series": points,
            "latest": points[-1] if points else None,
            "prev": points[-2] if len(points) > 1 else None,
            "change": round(diff, 4) if diff is not None else None,
            "change_pct": round(pct, 2) if pct is not None else None,
            "status": "ok" if points else "unavailable",
            "data_source": mode,  # fred / yahoo / cboe / sample
        }
    # 전체 소스 모드: 하나라도 fred면 fred, 전부 sample이면 sample
    overall_mode = "fred" if "fred" in modes else "sample"
    return result, overall_mode


if __name__ == "__main__":
    data, mode = fetch_all()
    print(f"수집 완료: {len(data)}개 지표, 소스={mode}")
