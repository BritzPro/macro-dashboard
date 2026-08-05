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

> **▶ 다음 세션은 여기부터**: 6번(또는 7번 정교화). (1·2·3·4·5·7 완료, 8 보류)
> 사용자에게 어느 것부터 할지 물어보고 진행할 것.

우선순위 순:

1. ~~FRED 키 연결 & series id 검증~~ ✅ 완료(2026-08-03). 30개 전부 실데이터.
   `RRPONTSYD`는 FRED 단위가 십억$라 표시 단위 교정함(다른 대차대조표 항목은 백만$).
2. ~~GitHub 저장소 생성 + Pages 설정 + FRED_API_KEY Secret 등록~~ ✅ 완료(2026-08-03).
   `BritzPro/macro-dashboard`(public), Pages=main/docs, Secret 등록, 라이브 확인.
3. **2차 지표(FRED 밖)** — ✅ 대부분 완료(2026-08-03):
   - 금(Yahoo GC=F)·BTC·ETH(Yahoo)·SKEW(Cboe)·VIX 만기구조(Cboe VIX/VIX3M) 추가. `scripts/sources.py`.
   - ISM: 실측 무료 소스 없음 → **FRED 무료 대체 proxy로 처리(사용자 결정)**. ✅
     엠파이어스테이트(GACDISA066MSFRBNY)·댈러스(BACTSAMFRBDAL)·CFNAI 추가.
     diffusion index라 0이 확장/수축 경계 → interpret에서 레벨 기반 판정(ISM_PROXY).
     실측 ISM PMI가 아니라 대체 지표임을 카드 이름·해석문에 명시.
   - 참고: stooq는 봇 차단(PoW)으로 사용 불가. Yahoo는 비공식 API라 best-effort(실패 시 샘플 폴백).
4. ~~해석문 심화~~ ✅ 완료(2026-08-05). config.py에 `DETAILS` 딕셔너리(41개 쉬운 상세설명),
   fetch에서 `detail` 필드로 주입, 확대 모달에 '지금 상황·이 지표는?(쉽게)·읽는 법·속한 축' 4단 표시.
5. ~~인터랙티브 차트~~ ✅ 완료(2026-08-05). 카드 차트 클릭→확대 모달, 호버 툴팁+크로스헤어,
   기간 버튼(1M/3M/6M/전체), 통계바(기간변화·고점·저점·평균)·평균선·판정배지. 전부 자체 SVG.
6. **유동성 '보유증권 vs 대출' 구분** (노트 4-2): Loans 계열 series 추가.
7. ~~종합 판정 고도화(시황 브리핑)~~ ✅ 완료(2026-08-05). interpret.py `_commentary`가
   여러 지표를 엮어 축별 진단 문장 + 종합 요약을 생성 → 종합 상황판에 표시.
   (추가 정교화 여지: 노트 10장 체크리스트 가중 스코어링, 물가는 전년비 필요.)
8. **신용잔고(margin)** — 2026-08-05 조사 후 **보류 결정**(깨끗한 무료 API 없음).
   - 미국 FINRA margin debt: 월간, xlsx/HTML만("data feed 없음"), 파일경로 변동·openpyxl 필요.
     값 예: Jun-26 $1,502,072M. 페이지: finra.org/investors/.../margin-statistics.
   - 한국 신용거래융자: KRX(data.krx.co.kr) OTP 스크래핑만 가능, 매우 불안정(테스트 시 hang).
   - 재개 조건: 안정적 무료 소스가 생기면 추가. 넣게 되면 미국은 매월, 한국은 매일 탭.

작업 후 반드시: `python scripts/build.py`로 검증 → 이 파일 일일 기록에 append →
`git pull --rebase`(§6 주의) → 커밋·push. 라이브: https://britzpro.github.io/macro-dashboard/

## 6. 재개 방법 (다음 세션이 할 일)

```bash
# 1) 파이프라인이 도는지 확인
python scripts/build.py            # "완료 → docs\data\indicators.json" 나오면 OK

# 2) 화면 확인
cd docs && python -m http.server 8899   # http://localhost:8899, 4개 탭 점검

# 3) 작업 후: 이 파일 '일일 기록'에 한 줄 남기고, evaluator 기준 통과 시 커밋
```

> **주의**: 매일 Action(bot)이 `docs/data/*`를 자동 커밋한다. 로컬에서 push 하기 전
> 반드시 `git pull --rebase` 하고, 데이터 파일 충돌이 나면 `python scripts/build.py`로
> 재빌드해 덮어쓴 뒤 `git add docs/data/* && git rebase --continue` 로 해결한다.

## 7. 일일 기록 (최신이 위)

### 2026-08-05 (축 심층 해설 모달)
- 피드백: 상황판 브리핑이 얕음 → 클릭하면 상세 설명 원함(지표·과거맥락·해석).
- config.py `AXIS_GUIDE`(5축 × what/how/history, 노트+실제사건 2019repo·2020코로나·2022실질금리 기반).
  build payload에 `axis_guide`.
- index.html에 `#axis-modal`, app.js `openAxis`: 종합 상황판 축 카드 클릭 → 심층 모달
  (지금 진단 + 무엇을보나 + 어떻게해석 + 과거맥락 + 그 축 지표목록). 지표 클릭 → 차트 모달로 전환.
- 검증: 유동성 축 5섹션·지표6개·차트전환 동작 확인.

### 2026-08-05 (종합 시황 브리핑)
- 사용자 피드백: 개별 설명 말고 '여러 지표를 엮은 종합 해석문'을 원함(상황판이 한 줄뿐이라 허전).
- interpret.py에 `_commentary` 추가: 실제 지표 값으로 축별 진단문(금리·유동성·할인율·위험선호·경기)
  + 종합 요약문(우호/부담 축을 엮어 서술) 생성. `_series_dir`·`_fmt` 헬퍼.
- build payload에 `commentary`, app.js 종합 상황판에 '시황 브리핑'+축별 진단 렌더, CSS 추가.
- CPI 레벨은 항상 상승이라 macro 진단은 실업률+CFNAI로 대체(물가상승률은 전년비 필요→매월 탭 안내).

### 2026-08-05 (해석문 심화)
- 각 지표를 초보자도 이해하게 풀어쓴 상세설명 41개 작성 → config.py `DETAILS` 딕셔너리.
  (지표 블록은 안 건드리고 한곳에서 관리. content-writer가 유지.)
- fetch.py에서 `detail` 필드로 주입, app.js 확대 모달 cm-interp를 4단 구성으로:
  지금 상황(current) · 이 지표는?(쉽게, detail) · 읽는 법(read) · 이 지표가 속한 축.
- 카드는 기존대로 간결 유지(의미·읽는법). 상세는 클릭→확대 시에만.
- 검증: 41개 전부 detail 보강, 모달 렌더 확인, 신규 콘솔 에러 없음.

### 2026-08-05 (주가지수 추가)
- 매일 탭에 주가지수 3종 추가(Yahoo): 코스피(^KS11)·코스닥(^KQ11)·나스닥종합(^IXIC). risk 축, DIRECTION +1.
- sources.fetch_yahoo: 지수 심볼 '^' URL 인코딩(%5E) 처리. app.js: pt 단위 천단위 구분.
- 총 41개 지표, 41/41 실데이터 검증. 확대 차트도 지수에서 정상.
- 신용잔고(한국 KRX/KOFIA·미국 FINRA): 조사 결과 깨끗한 무료 API 없음 → **보류 결정**(TODO 8번 참고).

### 2026-08-05 (인터랙티브 차트)
- 확대 차트 모달 추가(frontend only): 카드 스파크라인 클릭 → 큰 차트.
  - 호버 크로스헤어+툴팁(날짜·값), 기간 버튼 1M/3M/6M/전체, y축/x축 라벨.
  - 편의기능: 기간 통계바(기간변화%·고점·저점·평균), 평균 점선, 헤더 판정배지. 닫기 Esc/배경/버튼.
  - 전부 자체 SVG(외부 CDN 없음). index.html에 모달 마크업, app.js 확대차트 모듈, styles.css.
- 버그 수정: 호버 핸들러에서 rect.width=0(창 미표시)일 때 idx=NaN → 크래시. `if(!r.width)return`+idx 가드.
- 검증: 모달 열기/기간전환(91→31점)/호버 툴팁/닫기 3종 DOM 테스트 통과.

### 2026-08-03 (데이터 투명성)
- "값이 가짜로 채워진 건 없나?" 확인 요청 → 전 지표 감사: **38/38 실데이터, 샘플 0**.
- 투명성 기능 추가: 지표별 `data_source`(fred/yahoo/cboe/sample) 저장, build에 `data_status` 집계.
  대시보드 상단 '실데이터 N/전체' 카운터, 카드마다 출처 표시, 샘플이면 빨간 경고 배지.
- 키 유무 양방향 테스트로 경고 UI 검증. 커밋 `6da5719`.
- 참고: FRED 키 없어도 Yahoo·Cboe 5개(금·BTC·ETH·SKEW·VIXTS)는 키 불필요라 실데이터 유지.

### 2026-08-03 (2차 지표)
- FRED 밖 소스 모듈(`scripts/sources.py`) 추가: Yahoo(금·BTC·ETH), Cboe(SKEW, VIX 만기구조).
- config에 `source`/`symbol` 필드로 소스 분기(fetch.py `_fetch_one`). 기존 FRED 경로는 그대로.
- interpret: BTC/ETH(+1), VIXTS(-1) 방향 추가. VIXTS는 추세 대신 수준(콘탱고<1/백워데이션>1) 판정.
- app.js: 큰 달러값 천단위 포맷($63,123), 비율 단위(0.84배) 추가.
- 검증: 5개 전부 실데이터. 매일 탭 카드 20개, 콘솔 에러 없음. 총 35개 지표.
- **자동화 검증**: daily.yml 수동 실행 → Actions IP에서도 Yahoo·Cboe 폴백 0건(실데이터).
- **ISM 대체 proxy 추가**(사용자 결정): 엠파이어·댈러스·CFNAI 3개, 레벨 기반 판정. 총 38개 지표.

### 2026-08-03
- 프로젝트 최초 스캐폴딩 완료. 파이프라인·대시보드·에이전트·워크플로·문서 생성.
- 샘플 데이터로 4탭 렌더 검증 완료(로컬 http.server). 콘솔 에러 없음.
- FRED 키 연결·검증: 30개 series 전부 실데이터 취득(폴백 0). `RRPONTSYD` 단위(십억$) 교정.
- `git init`(main) + 첫 커밋 `0fc082a`, PROGRESS `8e658e2`.
- **배포 완료**: `BritzPro/macro-dashboard`(public) 생성·push, FRED_API_KEY Secret 등록,
  Pages(main/docs) 활성화. https://britzpro.github.io/macro-dashboard/ 라이브 확인(실데이터).
- 다음: 2차 지표(금/코인/ISM/SKEW/VIX만기구조), 해석문 심화, 인터랙티브 차트(hover/zoom).
