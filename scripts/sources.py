# -*- coding: utf-8 -*-
"""FRED 밖 데이터 소스 (2차 지표).

- Yahoo Finance : 금(GC=F), 코인(BTC-USD, ETH-USD)  — 비공식 API, best-effort
- Cboe          : SKEW, VIX, VIX3M 일별 공식 CSV
- VIX 만기구조   : Cboe VIX / VIX3M 비율 (콘탱고/백워데이션)

각 함수는 fred.fetch_series 와 동일하게 (points, mode) 를 반환한다.
실패 시 fred._sample 로 폴백하여 대시보드가 깨지지 않게 한다.
"""
from datetime import date, timedelta

try:
    import requests
except ImportError:
    requests = None

from fred import _sample, HISTORY_DAYS

_HEADERS = {"User-Agent": "Mozilla/5.0 (macro-dashboard)"}


def _recent(points):
    """최근 HISTORY_DAYS 이내로 자른다."""
    cutoff = (date.today() - timedelta(days=HISTORY_DAYS)).isoformat()
    return [p for p in points if p["date"] >= cutoff]


def fetch_yahoo(symbol, series_id, freq):
    """Yahoo Finance 일별 종가."""
    if requests is None:
        return _sample(series_id, freq), "sample"
    # 지수 심볼의 '^'(예: ^KS11)는 URL 인코딩 필요
    url = "https://query1.finance.yahoo.com/v8/finance/chart/" + symbol.replace("^", "%5E")
    try:
        r = requests.get(url, params={"range": "6mo", "interval": "1d"},
                         headers=_HEADERS, timeout=20)
        r.raise_for_status()
        res = r.json()["chart"]["result"][0]
        ts = res["timestamp"]
        closes = res["indicators"]["quote"][0]["close"]
        points = [
            {"date": date.fromtimestamp(t).isoformat(), "value": round(c, 4)}
            for t, c in zip(ts, closes) if c is not None
        ]
        return (points, "yahoo") if points else (_sample(series_id, freq), "sample")
    except Exception as e:
        print(f"[yahoo] {symbol} 실패 → 샘플 폴백: {e}")
        return _sample(series_id, freq), "sample"


def _cboe_points(index_name):
    """Cboe 일별 CSV 파싱. 마지막 열을 값으로 쓴다(SKEW=값, VIX계열=종가)."""
    url = "https://cdn.cboe.com/api/global/us_indices/daily_prices/" + index_name + "_History.csv"
    r = requests.get(url, headers=_HEADERS, timeout=20)
    r.raise_for_status()
    points = []
    for line in r.text.strip().splitlines():
        parts = line.split(",")
        try:
            m, d, y = parts[0].split("/")
            iso = f"{y}-{int(m):02d}-{int(d):02d}"
            points.append({"date": iso, "value": float(parts[-1])})
        except (ValueError, IndexError):
            continue  # 헤더 등
    return _recent(points)


def fetch_cboe(index_name, series_id, freq):
    if requests is None:
        return _sample(series_id, freq), "sample"
    try:
        points = _cboe_points(index_name)
        return (points, "cboe") if points else (_sample(series_id, freq), "sample")
    except Exception as e:
        print(f"[cboe] {index_name} 실패 → 샘플 폴백: {e}")
        return _sample(series_id, freq), "sample"


def fetch_vix_termstructure(series_id, freq):
    """VIX(근월) / VIX3M(원월) 비율. <1 콘탱고, >1 백워데이션."""
    if requests is None:
        return _sample(series_id, freq), "sample"
    try:
        vix = {p["date"]: p["value"] for p in _cboe_points("VIX")}
        vix3m = {p["date"]: p["value"] for p in _cboe_points("VIX3M")}
        common = sorted(set(vix) & set(vix3m))
        points = [
            {"date": d, "value": round(vix[d] / vix3m[d], 4)}
            for d in common if vix3m[d]
        ]
        return (points, "cboe") if points else (_sample(series_id, freq), "sample")
    except Exception as e:
        print(f"[vix_ts] 실패 → 샘플 폴백: {e}")
        return _sample(series_id, freq), "sample"
