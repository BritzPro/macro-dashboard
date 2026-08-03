# -*- coding: utf-8 -*-
"""지표 메타데이터와 해석문의 단일 소스.

각 지표는 FRED series id, 축(axis), 관찰주기(cadence), 단위,
그리고 해석 3단(meaning / read / current 규칙)을 가진다.
지표를 추가할 때는 여기 INDICATORS 에만 추가한다 (fetch 모듈은 이 목록을 읽는다).
"""

# 5축 정의 (강의노트 1장)
AXES = {
    "rates": "금리 · 돈의 가격",
    "liquidity": "유동성 · 돈의 흐름",
    "discount": "할인율 · 미래이익을 깎는 정도",
    "risk": "위험선호 · 위험을 감당할 준비",
    "macro": "경기·물가 · 이익의 배경",
}

# cadence: 매일(d) / 매주(w) / 매월(m)  ← 강의노트 11장
# freq: 데이터 발표 주기 (샘플 생성·차트에 사용)  d/w/m
# 각 지표: id(FRED), name, axis, cadence, freq, unit, higher_is(방향해석용), meaning, read
INDICATORS = [
    # ── 금리: 매일 ──────────────────────────────────────────────
    {
        "id": "DFEDTARU", "name": "연방기금금리 목표 상단", "axis": "rates",
        "cadence": "d", "freq": "d", "unit": "%",
        "meaning": "FOMC가 정하는 정책금리 목표범위의 상단이다. 시장에서 '기준금리'라 부르는 것의 실체이며, 돈값의 방향을 정하는 출발점이다.",
        "read": "올리면 긴축(멀티플 부담), 내리면 완화(멀티플 여지). 목표범위 자체보다 EFFR가 그 안에서 안정적인지가 중요하다.",
    },
    {
        "id": "EFFR", "name": "실효 연방기금금리 (EFFR)", "axis": "rates",
        "cadence": "d", "freq": "d", "unit": "%",
        "meaning": "은행 간 초단기 자금이 실제로 거래된 금리. 연준의 정책 의도가 시장에서 실제로 어떻게 구현되는지를 보여준다.",
        "read": "목표범위 안에서 얌전하면 배관이 매끄러운 것. 상단(IORB)에 바짝 붙거나 튀면 자금조달 압력 신호일 수 있다.",
    },
    {
        "id": "IORB", "name": "지급준비금 부리금리 (IORB)", "axis": "rates",
        "cadence": "d", "freq": "d", "unit": "%",
        "meaning": "은행이 연준에 맡긴 준비금에 받는 이자. 현재 운영체계(ample reserves)에서 단기금리의 상단을 묶는 기준점이다.",
        "read": "IORB를 기준으로 EFFR가 어디에 위치하는지가 배관 상태를 말해준다. IORB 자체는 정책금리와 함께 움직인다.",
    },
    {
        "id": "RRPONTSYAWARD", "name": "ON RRP 금리 (하단)", "axis": "rates",
        "cadence": "d", "freq": "d", "unit": "%",
        "meaning": "MMF 등 비은행 참가자에게 제공되는 무위험 익일물 금리. 단기금리의 하단을 받쳐주는 장치다.",
        "read": "IORB(상단)와 ON RRP금리(하단) 사이에서 단기금리가 안정적으로 움직이면 정상. 이 밴드를 벗어나면 이상 신호.",
    },
    {
        "id": "SOFR", "name": "담보부 초단기 금리 (SOFR)", "axis": "rates",
        "cadence": "d", "freq": "d", "unit": "%",
        "meaning": "국채를 담보로 한 익일물 자금조달 금리. 담보부 단기자금 배관이 매끄러운지를 보여주는 대표 지표다.",
        "read": "EFFR와 나란히 안정적이면 정상. SOFR가 급등하거나 튀면 repo 시장에 자금조달 압력이 생겼다는 신호(2019년 9월 사례).",
    },
    # ── 할인율: 매일 (금리 축이지만 할인율 해석) ─────────────────
    {
        "id": "DGS2", "name": "미국채 2년물", "axis": "discount",
        "cadence": "d", "freq": "d", "unit": "%",
        "meaning": "연준의 향후 정책경로 기대를 가장 민감하게 반영하는 만기.",
        "read": "내려갈 때 VIX 낮고 유동성 안정이면 완화 기대. 내려가는데 VIX 오르고 유가 밀리면 침체 우려일 가능성이 크다.",
    },
    {
        "id": "DGS10", "name": "미국채 10년물", "axis": "discount",
        "cadence": "d", "freq": "d", "unit": "%",
        "meaning": "주식시장의 표준 할인율. 미래 이익을 현재가치로 가져올 때 쓰는 기준.",
        "read": "방향보다 '이유'가 핵심. 실질금리 주도 상승은 성장주에 직접적 부담, 기대인플레 주도 상승은 명목성장 기대가 섞여 해석이 복합적.",
    },
    {
        "id": "DGS30", "name": "미국채 30년물", "axis": "discount",
        "cadence": "d", "freq": "d", "unit": "%",
        "meaning": "장기 인플레 우려, 재정 불안, 장기 risk premium 같은 구조적 불안을 더 많이 담는 만기.",
        "read": "2년물보다 30년물이 더 빠르게 오르면 단기정책 공포보다 장기 할인율 상승·재정 불안 성격이 강하다.",
    },
    {
        "id": "DFII10", "name": "10년 실질금리 (TIPS)", "axis": "discount",
        "cadence": "d", "freq": "d", "unit": "%",
        "meaning": "물가를 제거한 10년 실질 할인율. 성장주·고밸류에이션 자산의 부담을 가장 직접적으로 결정한다.",
        "read": "실질금리 상승은 미래이익을 더 세게 깎으라는 뜻 → 성장주·고밸류에 불리. 하락은 그 반대.",
    },
    {
        "id": "T10YIE", "name": "10년 기대인플레이션 (BEI)", "axis": "discount",
        "cadence": "d", "freq": "d", "unit": "%",
        "meaning": "10년물 명목-실질 차이로 본 시장의 기대 인플레이션.",
        "read": "10년물이 올라도 이게 주도했다면 명목성장 기대일 수 있어 덜 부정적. 급등하면 인플레 재점화 우려.",
    },
    # ── 유동성: 매주 ────────────────────────────────────────────
    {
        "id": "WALCL", "name": "연준 총자산", "axis": "liquidity",
        "cadence": "w", "freq": "w", "unit": "백만$",
        "meaning": "연준 대차대조표 총자산(H.4.1). 다만 '총액'보다 '구성'과 준비금 방향이 훨씬 중요하다.",
        "read": "총자산이 늘어도 그 돈이 준비금으로 남는지, TGA·ON RRP로 흡수되는지가 관건. 총액만 보고 완화라 단정하지 말 것.",
    },
    {
        "id": "WRESBAL", "name": "지급준비금", "axis": "liquidity",
        "cadence": "w", "freq": "w", "unit": "백만$",
        "meaning": "은행이 연준에 보유한 즉시 사용가능한 현금성 자금. 실전에서 시장 유동성의 핵심 변수로 본다.",
        "read": "안정적이거나 늘면 위험자산에 우호적. 빠르게 감소하면 체감 유동성이 타이트해진다.",
    },
    {
        "id": "WTREGEN", "name": "재무부 일반계정 (TGA)", "axis": "liquidity",
        "cadence": "w", "freq": "w", "unit": "백만$",
        "meaning": "연준 안의 정부 계좌. 세금·국채발행 대금이 들어오면 차오르고, 정부지출로 빠져나간다.",
        "read": "TGA 급증은 민간 준비금을 흡수(부담). TGA 감소는 돈이 민간으로 돌아옴(우호적).",
    },
    {
        "id": "RRPONTSYD", "name": "ON RRP 잔액", "axis": "liquidity",
        "cadence": "w", "freq": "d", "unit": "십억$",
        "meaning": "단기자금 참가자가 남는 돈을 연준에 하룻밤 주차하는 잔액. 시장금리 비교로 참가자가 스스로 움직인다.",
        "read": "감소하면 자금이 T-bill·민간시장으로 이동(우호적). 재증가하면 돈이 다시 연준으로 주차(보수적).",
    },
    {
        "id": "TREAST", "name": "보유 국채 (SOMA)", "axis": "liquidity",
        "cadence": "w", "freq": "w", "unit": "백만$",
        "meaning": "연준이 직접 보유한 국채(Securities held outright). 구조적 정책(QE/QT/재투자)의 뼈대가 드러나는 항목.",
        "read": "증가는 구조적 완화(QE·재투자), 감소는 QT. 긴급대출 증가와는 성격이 전혀 다르니 구분할 것.",
    },
    {
        "id": "WSHOMCB", "name": "보유 MBS", "axis": "liquidity",
        "cadence": "w", "freq": "w", "unit": "백만$",
        "meaning": "연준이 보유한 주택저당증권. 국채와 함께 SOMA 구조적 자산정책의 일부.",
        "read": "QT 국면에서 서서히 줄어드는 것이 정상. 급변은 정책 변화 신호.",
    },
    # ── 위험선호: 매일 ──────────────────────────────────────────
    {
        "id": "VIXCLS", "name": "VIX (변동성지수)", "axis": "risk",
        "cadence": "d", "freq": "d", "unit": "pt",
        "meaning": "주식시장의 보험료. 높을수록 시장이 앞으로 더 크게 흔들릴 수 있다고 본다.",
        "read": "유동성이 멀쩡한데 VIX만 튀면 이벤트성 공포일 수 있다. 준비금 감소·스프레드 확대와 겹치면 진짜 risk-off.",
    },
    {
        "id": "BAMLH0A0HYM2", "name": "하이일드 스프레드 (HY OAS)", "axis": "risk",
        "cadence": "d", "freq": "d", "unit": "%",
        "meaning": "투기등급 회사채의 신용보험료. 위험자산에 대한 시장의 신용 스트레스를 직접 보여준다.",
        "read": "좁으면 risk-on(신용 안심), 벌어지면 시장이 기업 신용위험을 민감하게 보기 시작한 것. 실질금리 상승과 겹치면 경계.",
    },
    {
        "id": "NFCI", "name": "시카고 연준 금융여건지수 (NFCI)", "axis": "risk",
        "cadence": "w", "freq": "w", "unit": "지수",
        "meaning": "미국 금융여건을 종합한 지표. 0을 기준으로 +는 긴축적, -는 완화적 여건.",
        "read": "음수(완화적)에서 안정적이면 우호적. 0을 넘어 상승하면 금융여건이 조여지는 중.",
    },
    {
        "id": "STLFSI4", "name": "세인트루이스 금융스트레스 (STLFSI)", "axis": "risk",
        "cadence": "w", "freq": "w", "unit": "지수",
        "meaning": "금융시장 전반의 스트레스 지표. 0이 평균, +는 스트레스 상승.",
        "read": "0 아래에서 조용하면 평온. 급하게 +로 튀면 금융 스트레스가 번지는 신호.",
    },
    # ── 경기·물가: 매월 ─────────────────────────────────────────
    {
        "id": "CPIAUCSL", "name": "소비자물가 CPI", "axis": "macro",
        "cadence": "m", "freq": "m", "unit": "지수",
        "meaning": "소비자가 체감하는 물가 수준. 전년비 상승률로 인플레 추세를 본다.",
        "read": "서서히 둔화하면 연준이 긴축 강도를 낮출 여지. 재상승하면 할인율 부담이 다시 커진다.",
    },
    {
        "id": "CPILFESL", "name": "근원 CPI (Core)", "axis": "macro",
        "cadence": "m", "freq": "m", "unit": "지수",
        "meaning": "food·energy를 뺀 기조적 물가. 인플레의 끈적한 추세를 본다.",
        "read": "헤드라인보다 느리게 움직인다. Core가 안 꺾이면 금리인하가 늦춰진다.",
    },
    {
        "id": "PCEPI", "name": "PCE 물가", "axis": "macro",
        "cadence": "m", "freq": "m", "unit": "지수",
        "meaning": "연준이 통화정책 판단에 특히 중시하는 물가지표.",
        "read": "연준의 2% 목표는 PCE 기준. 이 둔화 여부가 정책 경로를 좌우한다.",
    },
    {
        "id": "PCEPILFE", "name": "근원 PCE (Core PCE)", "axis": "macro",
        "cadence": "m", "freq": "m", "unit": "지수",
        "meaning": "연준이 가장 신뢰하는 기조적 물가지표.",
        "read": "Core PCE 추세가 연준 결정의 최종 준거. 여기가 목표로 수렴하면 완화 여지가 열린다.",
    },
    {
        "id": "PPIACO", "name": "생산자물가 PPI", "axis": "macro",
        "cadence": "m", "freq": "m", "unit": "지수",
        "meaning": "생산자가 받는 가격. 소비자물가에 선행하는 경향이 있는 파이프라인 인플레.",
        "read": "PPI가 먼저 오르면 CPI 상방 압력, 먼저 꺾이면 인플레 둔화 선행 신호일 수 있다.",
    },
    {
        "id": "PAYEMS", "name": "비농업고용 (NFP)", "axis": "macro",
        "cadence": "m", "freq": "m", "unit": "천명",
        "meaning": "미국 고용의 핵심 지표. 경기와 이익의 배경이 버티는지를 보여준다.",
        "read": "급격히 무너지지 않으면 연착륙 기대. 급감하면 침체 우려로 할인율·이익이 동시에 압박.",
    },
    {
        "id": "UNRATE", "name": "실업률", "axis": "macro",
        "cadence": "m", "freq": "m", "unit": "%",
        "meaning": "노동시장의 냉각 정도를 보는 지표.",
        "read": "완만한 상승은 연착륙 범위. 빠르게 오르면(Sahm rule) 침체 신호로 해석된다.",
    },
    # ISM 대체 proxy (실측 ISM은 무료 소스 없음 → 지역 연준 서베이·경기지수로 대체)
    {
        "id": "GACDISA066MSFRBNY", "name": "엠파이어스테이트 제조업 (ISM 대체)", "axis": "macro",
        "cadence": "m", "freq": "m", "unit": "지수",
        "meaning": "뉴욕 연준의 제조업 경기 서베이(diffusion index). 무료 실측 ISM이 없어 대체 지표로 쓴다. 0이 확장/수축의 경계다(ISM의 50에 해당).",
        "read": "0 위=제조업 확장, 아래=위축. ISM 제조업 PMI에 선행하는 경향이 있어 제조업 경기 방향을 먼저 시사할 수 있다.",
    },
    {
        "id": "BACTSAMFRBDAL", "name": "댈러스 연준 제조업 (ISM 대체)", "axis": "macro",
        "cadence": "m", "freq": "m", "unit": "지수",
        "meaning": "댈러스 연준의 제조업 경기 서베이(diffusion index). 텍사스 제조업 활동을 보여주며 ISM 대체로 함께 본다. 0이 경계.",
        "read": "여러 지역 연준 서베이(뉴욕·댈러스 등)가 함께 확장/위축을 가리키면 신뢰도가 높아진다.",
    },
    {
        "id": "CFNAI", "name": "시카고 연준 경기활동지수 (CFNAI)", "axis": "macro",
        "cadence": "m", "freq": "m", "unit": "지수",
        "meaning": "85개 지표를 종합한 시카고 연준 경기활동지수. 0=추세 성장, 음수=추세 하회. 경기 전반의 강도를 넓게 본다.",
        "read": "-0.7 아래가 지속되면 침체 신호로 해석되곤 한다. 개별 서베이보다 광범위한 경기 배경을 확인하는 용도.",
    },
    # ── 시장가격: 매일 ──────────────────────────────────────────
    {
        "id": "DEXKOUS", "name": "달러/원 환율", "axis": "risk",
        "cadence": "d", "freq": "d", "unit": "원",
        "meaning": "한국 투자자에게 글로벌 매크로가 한국 시장으로 번역되는 속도계.",
        "read": "상승은 risk-off·외국인 수급 부담·수입물가 압력. 하락은 위험선호 회복·원화자산 선호 회복.",
    },
    {
        "id": "DCOILWTICO", "name": "WTI 유가", "axis": "macro",
        "cadence": "d", "freq": "d", "unit": "$",
        "meaning": "성장·인플레이션·지정학을 동시에 반영하는 원유 가격(서부텍사스).",
        "read": "상승이 항상 좋은 것도 나쁜 것도 아니다. VIX·장기금리·달러와 함께 봐야 성격을 안다.",
    },
    {
        "id": "DCOILBRENTEU", "name": "Brent 유가", "axis": "macro",
        "cadence": "d", "freq": "d", "unit": "$",
        "meaning": "국제 벤치마크 원유 가격(브렌트).",
        "read": "WTI와의 스프레드는 지역 수급을 반영. 방향은 WTI와 함께 인플레·성장 신호로 읽는다.",
    },
    # ── 2차 지표 (FRED 밖 소스) ─────────────────────────────────
    {
        "id": "GOLD", "name": "금 (COMEX)", "axis": "macro",
        "cadence": "d", "freq": "d", "unit": "$",
        "source": "yahoo", "symbol": "GC=F",
        "meaning": "전통적 안전자산이지만, 최근에는 화폐가치 희석 우려와 중앙은행의 대체자산 수요까지 함께 반영한다. 그래서 주식과 금이 동시에 오르기도 한다.",
        "read": "공포만이 아니라 통화가치 훼손 헤지·달러 대체수요·지정학 분산수요도 함께 담는다. 방향을 단독으로 단정하지 말고 달러·실질금리와 함께 본다.",
    },
    {
        "id": "BTC", "name": "비트코인", "axis": "risk",
        "cadence": "d", "freq": "d", "unit": "$",
        "source": "yahoo", "symbol": "BTC-USD",
        "meaning": "실적이나 전통적 펀더멘털의 닻이 약해, 종종 초과 유동성과 위험선호의 고베타 지표처럼 움직인다.",
        "read": "상승은 '시장 어딘가에 남는 돈이 있다'는 힌트일 수 있다. 유동성·위험선호 축과 함께 읽는다.",
    },
    {
        "id": "ETH", "name": "이더리움", "axis": "risk",
        "cadence": "d", "freq": "d", "unit": "$",
        "source": "yahoo", "symbol": "ETH-USD",
        "meaning": "비트코인과 함께 위험선호·유동성의 고베타를 반영하는 대표 알트코인.",
        "read": "비트코인과의 상대강도는 위험선호의 세기를 보조적으로 확인하는 데 쓴다.",
    },
    {
        "id": "SKEW", "name": "SKEW (꼬리위험)", "axis": "risk",
        "cadence": "d", "freq": "d", "unit": "pt",
        "source": "cboe", "symbol": "SKEW",
        "meaning": "'평소 변동성'이 아니라 '급락 꼬리위험 보험료'에 가깝다. VIX는 낮은데 SKEW만 높으면 시장이 충격성 급락을 경계하고 있을 수 있다.",
        "read": "높을수록 시장이 일상 변동성보다 충격성 급락(테일 리스크)을 대비. VIX와 함께 봐야 의미가 산다.",
    },
    {
        "id": "VIXTS", "name": "VIX 만기구조 (근/원월)", "axis": "risk",
        "cadence": "d", "freq": "d", "unit": "ratio",
        "source": "vix_ts",
        "meaning": "근월 변동성(VIX·30일)을 원월(VIX3M·93일)로 나눈 비율. 보통 원월이 더 높은 콘탱고(비율<1)가 정상에 가깝다.",
        "read": "1 미만 콘탱고=정상. 1 이상 백워데이션=가까운 시점의 스트레스를 시장이 더 크게 보고 있다는 뜻.",
    },
]

# id -> meta 빠른 조회
BY_ID = {ind["id"]: ind for ind in INDICATORS}

# 샘플(폴백) 생성용 기준값: id -> (base, 연변동성%, 추세방향)
# FRED 키가 없을 때 대시보드가 렌더되도록 현실적인 합성 시계열을 만든다.
SAMPLE_BASE = {
    "DFEDTARU": (4.50, 0.5, 0), "EFFR": (4.33, 0.5, 0), "IORB": (4.40, 0.5, 0),
    "RRPONTSYAWARD": (4.25, 0.5, 0), "SOFR": (4.36, 2, 0),
    "DGS2": (3.90, 8, -1), "DGS10": (4.30, 7, 0), "DGS30": (4.65, 7, 1),
    "DFII10": (1.90, 10, 0), "T10YIE": (2.30, 6, 0),
    "WALCL": (6900000, 2, -1), "WRESBAL": (3300000, 6, -1),
    "WTREGEN": (720000, 25, 1), "RRPONTSYD": (500, 40, -1),
    "TREAST": (4200000, 3, -1), "WSHOMCB": (2180000, 3, -1),
    "VIXCLS": (16, 35, 0), "BAMLH0A0HYM2": (3.10, 20, 0),
    "NFCI": (-0.35, 30, 0), "STLFSI4": (-0.50, 40, 0),
    "CPIAUCSL": (313, 2, 1), "CPILFESL": (318, 2, 1),
    "PCEPI": (125, 2, 1), "PCEPILFE": (126, 2, 1), "PPIACO": (260, 3, 1),
    "PAYEMS": (159000, 0.4, 1), "UNRATE": (4.10, 6, 1),
    "DEXKOUS": (1360, 6, 0), "DCOILWTICO": (74, 20, 0), "DCOILBRENTEU": (78, 20, 0),
    "GOLD": (3000, 15, 1), "BTC": (68000, 50, 0), "ETH": (2600, 55, 0),
    "SKEW": (140, 8, 0), "VIXTS": (0.9, 10, 0),
    "GACDISA066MSFRBNY": (10, 150, 0), "BACTSAMFRBDAL": (3, 300, 0), "CFNAI": (0.1, 500, 0),
}
