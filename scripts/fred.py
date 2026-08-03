# -*- coding: utf-8 -*-
"""FRED 데이터 취득 헬퍼.

- FRED_API_KEY 환경변수가 있으면 실제 FRED API에서 시계열을 가져온다.
- 없거나 실패하면 결정론적 합성 시계열(샘플)로 폴백한다.
  (키 없이도 대시보드가 렌더되도록 하기 위함 — skill.md 5장 규칙)

반환 형식: (points, mode)
  points: [{"date": "YYYY-MM-DD", "value": float}, ...]  (오래된→최신)
  mode:   "fred" | "sample"
"""
import os
import math
import random
from datetime import date, timedelta

try:
    import requests
except ImportError:  # 키가 없을 땐 requests 없이도 동작
    requests = None

from config import SAMPLE_BASE

FRED_URL = "https://api.stlouisfed.org/fred/series/observations"
HISTORY_DAYS = 180  # 차트에 보여줄 기간


def _points_for_freq(freq):
    """freq(d/w/m)에 맞춰 (오늘로부터 과거) 날짜 리스트를 만든다."""
    today = date.today()
    if freq == "m":
        dates = []
        y, m = today.year, today.month
        for _ in range(7):  # 최근 7개월
            dates.append(date(y, m, 1))
            m -= 1
            if m == 0:
                m = 12
                y -= 1
        return list(reversed(dates))
    step = 7 if freq == "w" else 1
    n = HISTORY_DAYS // step
    return [today - timedelta(days=step * i) for i in range(n)][::-1]


def _sample(series_id, freq):
    """결정론적 합성 시계열. series_id를 seed로 써서 매번 동일하게 생성."""
    base, vol_pct, trend = SAMPLE_BASE.get(series_id, (100.0, 5.0, 0))
    rng = random.Random(hash(series_id) & 0xFFFFFFFF)
    dates = _points_for_freq(freq)
    n = len(dates)
    daily_vol = (vol_pct / 100.0) * base / math.sqrt(252)
    val = base
    points = []
    for i, d in enumerate(dates):
        drift = trend * daily_vol * 0.15
        val = max(0.0, val + drift + rng.gauss(0, daily_vol))
        points.append({"date": d.isoformat(), "value": round(val, 4)})
    # 마지막 값을 base 근처로 부드럽게 당겨 현실감 유지
    return points


def fetch_series(series_id, freq):
    """지표 하나의 시계열을 반환한다. 실패 시 샘플 폴백."""
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key or requests is None:
        return _sample(series_id, freq), "sample"

    start = (date.today() - timedelta(days=HISTORY_DAYS + 40)).isoformat()
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": start,
        "sort_order": "asc",
    }
    try:
        r = requests.get(FRED_URL, params=params, timeout=20)
        r.raise_for_status()
        obs = r.json().get("observations", [])
        points = [
            {"date": o["date"], "value": float(o["value"])}
            for o in obs
            if o.get("value") not in (".", "", None)
        ]
        if not points:
            return _sample(series_id, freq), "sample"
        return points, "fred"
    except Exception as e:
        print(f"[fred] {series_id} 실패 → 샘플 폴백: {e}")
        return _sample(series_id, freq), "sample"
