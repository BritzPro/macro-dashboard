# -*- coding: utf-8 -*-
"""해석 단계: 최신 데이터로 지표별 '현재 상황'과 5축 신호등을 판정한다.

단일 책임: '판정하는 일'만 한다. 수집(fetch)이나 조립(build)은 하지 않는다.
판정 논리는 강의노트의 규칙을 코드로 옮긴 것이며, 투자조언이 아니라
'위험자산 환경에 우호적/중립/부담'인지의 방향만 표시한다.
"""
from config import AXES

# 지표가 '오를 때' 위험자산 환경에 유리(+1)/불리(-1)/중립(0)한지.
DIRECTION = {
    "WRESBAL": +1, "WALCL": +1, "TREAST": +1, "WSHOMCB": +1,
    "WTREGEN": -1, "RRPONTSYD": -1,
    "VIXCLS": -1, "BAMLH0A0HYM2": -1, "NFCI": -1, "STLFSI4": -1,
    "DFII10": -1, "DGS10": -1, "DGS30": -1, "DEXKOUS": -1, "UNRATE": -1,
    "PAYEMS": +1,
    "BTC": +1, "ETH": +1, "VIXTS": -1,
    "KOSPI": +1, "KOSDAQ": +1, "NASDAQ": +1,
    # 정책금리·기대인플레·유가·2년물·물가지수·금·SKEW 등은 방향 단정 대신 중립(0)
}

SIGNAL_LABEL = {"good": "우호적", "neutral": "중립", "bad": "부담"}

# ISM 대체 proxy: 추세보다 '0 기준 확장/수축'이 핵심 (CFNAI는 스케일이 달라 임계값 별도)
ISM_PROXY = {"GACDISA066MSFRBNY", "BACTSAMFRBDAL", "CFNAI"}


def _trend(series):
    """앞 3점 평균 대비 뒤 3점 평균의 변화. (metric, is_absolute)."""
    vals = [p["value"] for p in series]
    if len(vals) < 4:
        return 0.0, False
    ref = sum(vals[:3]) / 3
    last = sum(vals[-3:]) / 3
    if abs(ref) < 1:  # 0 근처 지표(NFCI, STLFSI 등)는 절대변화로
        return last - ref, True
    return (last - ref) / abs(ref) * 100, False  # 그 외는 % 변화


def _bucket(metric, is_abs, direction):
    """방향을 반영해 good/neutral/bad로 분류."""
    if direction == 0:
        return "neutral"
    thresh = 0.1 if is_abs else 1.0
    friendly = metric * direction
    if friendly > thresh:
        return "good"
    if friendly < -thresh:
        return "bad"
    return "neutral"


def _trend_word(metric):
    if metric > (0.1):
        return "상승"
    if metric < -0.1:
        return "하락"
    return "횡보"


def interpret(fetched):
    """fetch 결과에 current/signal을 붙이고, 축·종합 신호를 계산한다."""
    axis_scores = {a: [] for a in AXES}
    score_map = {"good": 1, "neutral": 0, "bad": -1}

    for ind_id, d in fetched.items():
        if d["status"] != "ok":
            d["current"] = "데이터를 가져오지 못해 현재 판정을 보류한다."
            d["signal"] = "neutral"
            continue
        # VIX 만기구조는 추세보다 '현재 수준'(콘탱고/백워데이션)이 핵심
        if ind_id == "VIXTS":
            v = d["latest"]["value"]
            if v >= 1.0:
                sig, msg = "bad", f"현재 {v:.2f} — 백워데이션(근월>원월). 가까운 시점의 스트레스를 시장이 더 크게 보는 국면."
            elif v <= 0.95:
                sig, msg = "good", f"현재 {v:.2f} — 콘탱고(원월>근월)가 뚜렷. 단기 스트레스가 낮은 정상 국면."
            else:
                sig, msg = "neutral", f"현재 {v:.2f} — 콘탱고에 가깝지만 1에 근접. 스트레스 신호는 아직 약하다."
            d["current"], d["signal"] = msg, sig
            axis_scores[d["axis"]].append(score_map[sig])
            continue
        # ISM 대체 proxy는 0 기준 확장/수축으로 판정
        if ind_id in ISM_PROXY:
            v = d["latest"]["value"]
            hi, lo = (0.0, -0.35) if ind_id == "CFNAI" else (2.0, -2.0)
            if v > hi:
                sig, state = "good", "확장"
            elif v < lo:
                sig, state = "bad", "수축·둔화"
            else:
                sig, state = "neutral", "경계 부근"
            d["current"] = f"현재 {v:.2f} — {state} 국면(0이 확장/수축 경계)."
            d["signal"] = sig
            axis_scores[d["axis"]].append(score_map[sig])
            continue
        direction = DIRECTION.get(ind_id, 0)
        metric, is_abs = _trend(d["series"])
        signal = _bucket(metric, is_abs, direction)
        word = _trend_word(metric if is_abs else metric)
        if direction == 0:
            current = f"최근 흐름은 '{word}'. 방향만으로 우호·부담을 단정하기 어려운 지표라 다른 축과 함께 읽는다."
        else:
            current = f"최근 흐름은 '{word}'이며, 이는 위험자산 환경에 {SIGNAL_LABEL[signal]}인 방향이다."
        d["current"] = current
        d["signal"] = signal
        axis_scores[d["axis"]].append(score_map[signal])

    # 축별 신호등
    axis_signal = {}
    for axis, scores in axis_scores.items():
        avg = sum(scores) / len(scores) if scores else 0
        label = "good" if avg > 0.25 else "bad" if avg < -0.25 else "neutral"
        axis_signal[axis] = {"label": label, "score": round(avg, 2), "title": AXES[axis]}

    # 종합
    vals = [s["score"] for s in axis_signal.values()]
    overall_avg = sum(vals) / len(vals) if vals else 0
    overall_label = "good" if overall_avg > 0.2 else "bad" if overall_avg < -0.2 else "neutral"
    headline = {
        "good": "유동성·위험선호가 대체로 우호적인 국면. 멀티플을 허용할 여지가 있는 환경에 가깝다.",
        "neutral": "우호·부담 요인이 섞여 있는 중립 국면. 특정 축의 방향 전환을 주시할 때다.",
        "bad": "유동성 위축·위험회피 신호가 우세한 국면. 멀티플이 눌리기 쉬운 환경에 가깝다.",
    }[overall_label]

    return {
        "axis_signal": axis_signal,
        "overall": {"label": overall_label, "score": round(overall_avg, 2), "headline": headline},
    }
