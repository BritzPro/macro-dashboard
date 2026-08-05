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


def _series_dir(d):
    """지표 시계열의 방향(상승/하락/횡보)을 한 단어로 반환. 서술문에 쓴다."""
    if not d or d.get("status") != "ok":
        return "횡보"
    vals = [p["value"] for p in d["series"]]
    if len(vals) < 4:
        return "횡보"
    ref = sum(vals[:3]) / 3
    last = sum(vals[-3:]) / 3
    diff = (last - ref) if abs(ref) < 1 else (last - ref) / abs(ref)
    thr = 0.1 if abs(ref) < 1 else 0.005
    return "상승" if diff > thr else "하락" if diff < -thr else "횡보"


def _fmt(d):
    """서술문용 값 포맷(파이썬측). 대시보드 표기와 대략 일치."""
    if not d or not d.get("latest"):
        return "-"
    v = d["latest"]["value"]
    u = d.get("unit")
    if u == "%":
        return f"{v:.2f}%"
    if u == "pt":
        return f"{v:,.0f}" if v >= 1000 else f"{v:.1f}"
    if u == "백만$":
        return f"{v / 1e6:.2f}조$"
    if u == "십억$":
        return f"{v / 1000:.2f}조$" if v >= 1000 else f"{v:.0f}십억$"
    return f"{v:.1f}"


def _commentary(fetched, axis_signal, overall_label):
    """여러 지표를 엮어 노트의 5단계 흐름대로 시황을 서술한다."""
    g = fetched.get

    def sofr_gap():
        s, e = g("SOFR"), g("EFFR")
        if s and e and s.get("latest") and e.get("latest"):
            return abs(s["latest"]["value"] - e["latest"]["value"]) > 0.2
        return False

    rd = _series_dir(g("DFII10"))
    cf = g("CFNAI")
    cfv = cf["latest"]["value"] if cf and cf.get("latest") else None
    cf_state = ("확장" if (cfv is not None and cfv > 0)
                else "둔화" if (cfv is not None and cfv < -0.35) else "추세 부근")
    reads = {
        "rates": (
            f"정책금리 상단 {_fmt(g('DFEDTARU'))}, 실효금리(EFFR) {_fmt(g('EFFR'))}, "
            f"SOFR {_fmt(g('SOFR'))} — "
            + ("SOFR가 실효금리와 벌어져 단기 자금 압력 신호가 보입니다."
               if sofr_gap() else "단기 자금시장은 대체로 안정적입니다.")
        ),
        "discount": (
            f"10년물 {_fmt(g('DGS10'))}, 10년 실질금리 {_fmt(g('DFII10'))}로 실질금리가 {rd} 중입니다. "
            + {"상승": "실질금리 상승은 성장주·고밸류에 할인 부담을 키우는 방향입니다.",
               "하락": "실질금리 하락은 성장주에 우호적인 방향입니다.",
               "횡보": "할인율 부담은 큰 변화가 없습니다."}[rd]
        ),
        "liquidity": (
            f"지급준비금은 {_series_dir(g('WRESBAL'))}, 재무부 계정(TGA)은 {_series_dir(g('WTREGEN'))}, "
            f"ON RRP는 {_series_dir(g('RRPONTSYD'))} 흐름입니다. "
            + {"good": "돈이 시장에 남아 유동성은 우호적입니다.",
               "bad": "체감 유동성이 타이트해지는 방향입니다.",
               "neutral": "유동성은 중립적입니다."}[axis_signal["liquidity"]["label"]]
        ),
        "risk": (
            f"VIX {_fmt(g('VIXCLS'))}, 하이일드 스프레드 {_fmt(g('BAMLH0A0HYM2'))} — "
            + {"good": "위험선호가 살아있는 편입니다.",
               "bad": "위험을 피하려는 신호가 우세합니다.",
               "neutral": "위험선호는 중립적입니다."}[axis_signal["risk"]["label"]]
        ),
        "macro": (
            f"실업률은 {_series_dir(g('UNRATE'))}, 경기활동지수(CFNAI)는 '{cf_state}' 국면입니다. "
            + {"good": "고용·경기 배경은 우호적입니다.",
               "bad": "고용·경기 배경이 부담스럽습니다.",
               "neutral": "고용·경기는 혼재되어 있습니다."}[axis_signal["macro"]["label"]]
            + " (물가 상승률은 매월 탭의 CPI·PCE 최신치로 확인하세요.)"
        ),
    }

    ko = {"good": "우호적", "neutral": "중립", "bad": "부담"}
    goods = [AXES[a].split(" · ")[0] for a in AXES if axis_signal[a]["label"] == "good"]
    bads = [AXES[a].split(" · ")[0] for a in AXES if axis_signal[a]["label"] == "bad"]
    summary = f"지금은 종합적으로 '{ko[overall_label]}' 국면입니다. "
    if goods and bads:
        summary += (f"{'·'.join(goods)} 쪽은 우호적이지만 {'·'.join(bads)} 쪽이 부담으로 맞서고 있어, "
                    "방향을 결정지을 축의 전환을 지켜볼 때입니다.")
    elif goods:
        summary += (f"{'·'.join(goods)} 쪽이 우호적이고 뚜렷한 부담 요인은 적어, "
                    "위험자산에 비교적 우호적인 환경입니다.")
    elif bads:
        summary += f"{'·'.join(bads)} 쪽이 부담으로 작용해, 멀티플이 눌리기 쉬운 환경입니다."
    else:
        summary += "축들이 대체로 중립이라 뚜렷한 방향성은 아직 약합니다."

    return {"reads": reads, "summary": summary}


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
        "commentary": _commentary(fetched, axis_signal, overall_label),
    }
