# 작업 로그 (PROGRESS)

> 이 파일 하나만 읽으면 누구든(Claude / Codex / 사람) 맥락을 잡고 이어서 작업할 수 있게 관리한다.
> 새 작업 세션을 시작하면 **① 이 파일을 읽고 → ② 아래 '재개 방법'대로 확인 → ③ 작업 후 '일일 기록'에 append** 한다.

---

## 1. 프로젝트 한 줄

주식 매크로 강의노트를 **매일 자동 갱신되는 정적 대시보드**로 만든다. 서버 없이 GitHub Actions가 하루 1회 데이터를 갱신하고 GitHub Pages로 서빙한다.

- **라이브 URL:** https://britzpro.github.io/macro-dashboard/
- **저장소:** https://github.com/BritzPro/macro-dashboard (public)

원본 노트: `D:\공부\★주식\주식시장을 위한 매크로 강의노트 ....md`

## 2. 확정된 결정 (Decision Log)

| 항목 | 결정 | 이유 |
|---|---|---|
| 데이터 소스 | **FRED**(무료 API) | 노트 지표의 ~85%를 한 곳에서 커버 |
| 호스팅 | **GitHub Pages (public)** | 폰·어디서든 URL로 열람, 무료, 매일 자동갱신 |
| 1차 범위 | FRED 커버 지표 전부 (30개) | 사용자 선택 |
| 레이아웃 | **종합 상황판 + 매일/매주/매월** 4탭 | 노트 11장 + 5축 요약 결합 |
| 데이터 수집 구조 | **LLM 아님, 결정론적 파이썬** | 매일 CI에서 LLM은 비용·불안정. 수집은 정해진 series→JSON |
| fetch 모듈 분리 | **5개 파일 대신 1개 `fetch.py`** + interpret/build 분리 | 도메인 구분은 `axis` 데이터로. 5개 동일모듈은 과한 추상화(원칙2) |
| 로컬 열람 | 데이터를 `data.js`로도 내보냄 | file:// 더블클릭으로도 열리게 (fetch CORS 회피) |

## 3. 아키텍처 / 데이터 흐름

```
config.py(지표+해석문) ─► fetch.py(값·변화) ─► interpret.py(현재판정·신호등)
                                                        │
                                                        ▼
                                        build.py ─► docs/data/{indicators.json, data.js}
                                                        │
                                          docs/{index.html, app.js, styles.css} 가 읽어 렌더
```

개발용 에이전트(`.claude/agents/`): data-engineer / frontend-engineer / content-writer / reviewer / evaluator.
개발 원칙: `.claude/skills/dev-principles/SKILL.md`.

## 4. 현재 상태 — Day 1 완료 (2026-08-03)

- [x] 프로젝트 스캐폴딩, 개발 원칙 스킬(skill.md)
- [x] 파이프라인(config/fred/fetch/interpret/build) — 30개 지표, 샘플 폴백 동작
- [x] 대시보드 4탭 렌더 확인 (종합 신호등 + 지표 카드 + SVG 스파크라인 + 해석문)
- [x] 개발/리뷰/평가 + 서브에이전트 5종 정의
- [x] GitHub Actions 일일 갱신 워크플로
- [x] README / PROGRESS

**현재 소스 = FRED 실데이터.** 키 연결·검증 완료. 30개 series 전부 실데이터로 취득(폴백 0건).
로컬 실행 시 `FRED_API_KEY` 환경변수 필요(키는 저장소에 커밋 안 함).

## 5. 남은 작업 (TODO)

우선순위 순:

1. ~~FRED 키 연결 & series id 검증~~ ✅ 완료(2026-08-03). 30개 전부 실데이터.
   `RRPONTSYD`는 FRED 단위가 십억$라 표시 단위 교정함(다른 대차대조표 항목은 백만$).
2. ~~GitHub 저장소 생성 + Pages 설정 + FRED_API_KEY Secret 등록~~ ✅ 완료(2026-08-03).
   `BritzPro/macro-dashboard`(public), Pages=main/docs, Secret 등록, 라이브 확인.
3. **2차 지표(FRED 밖)** — ✅ 대부분 완료(2026-08-03):
   - 금(Yahoo GC=F)·BTC·ETH(Yahoo)·SKEW(Cboe)·VIX 만기구조(Cboe VIX/VIX3M) 추가. `scripts/sources.py`.
   - ⚠️ **ISM PMI 미완**: 실측치 무료 소스가 없음(ISM 유료·FRED discontinued). 결정 필요:
     (a) 보류, (b) FRED 무료 대체 proxy(지역 연준 제조업지수·CFNAI 등) 사용.
   - 참고: stooq는 봇 차단(PoW)으로 사용 불가. Yahoo는 비공식 API라 best-effort(실패 시 샘플 폴백).
4. **해석문 심화** (content-writer): 각 지표 '현재 상황'을 노트 시나리오(5-6장)와 더 촘촘히 연결.
5. **인터랙티브 차트** (frontend, 사용자가 '기본 완성 후' 요청): hover 툴팁, 기간 확대/축소.
   현재는 자체 SVG 스파크라인 → 툴팁/줌 추가 시에도 외부 CDN 금지 유지.
6. **유동성 '보유증권 vs 대출' 구분** (노트 4-2): Loans 계열 series 추가.

## 6. 재개 방법 (다음 세션이 할 일)

```bash
# 1) 파이프라인이 도는지 확인
python scripts/build.py            # "완료 → docs\data\indicators.json" 나오면 OK

# 2) 화면 확인
cd docs && python -m http.server 8899   # http://localhost:8899, 4개 탭 점검

# 3) 작업 후: 이 파일 '일일 기록'에 한 줄 남기고, evaluator 기준 통과 시 커밋
```

## 7. 일일 기록 (최신이 위)

### 2026-08-03 (2차 지표)
- FRED 밖 소스 모듈(`scripts/sources.py`) 추가: Yahoo(금·BTC·ETH), Cboe(SKEW, VIX 만기구조).
- config에 `source`/`symbol` 필드로 소스 분기(fetch.py `_fetch_one`). 기존 FRED 경로는 그대로.
- interpret: BTC/ETH(+1), VIXTS(-1) 방향 추가. VIXTS는 추세 대신 수준(콘탱고<1/백워데이션>1) 판정.
- app.js: 큰 달러값 천단위 포맷($63,123), 비율 단위(0.84배) 추가.
- 검증: 5개 전부 실데이터. 매일 탭 카드 20개, 콘솔 에러 없음. 총 35개 지표.
- 남은 것: ISM(무료 소스 없음 — 사용자 결정 대기).

### 2026-08-03
- 프로젝트 최초 스캐폴딩 완료. 파이프라인·대시보드·에이전트·워크플로·문서 생성.
- 샘플 데이터로 4탭 렌더 검증 완료(로컬 http.server). 콘솔 에러 없음.
- FRED 키 연결·검증: 30개 series 전부 실데이터 취득(폴백 0). `RRPONTSYD` 단위(십억$) 교정.
- `git init`(main) + 첫 커밋 `0fc082a`, PROGRESS `8e658e2`.
- **배포 완료**: `BritzPro/macro-dashboard`(public) 생성·push, FRED_API_KEY Secret 등록,
  Pages(main/docs) 활성화. https://britzpro.github.io/macro-dashboard/ 라이브 확인(실데이터).
- 다음: 2차 지표(금/코인/ISM/SKEW/VIX만기구조), 해석문 심화, 인터랙티브 차트(hover/zoom).
