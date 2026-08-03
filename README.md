# 매크로 대시보드

주식시장을 위한 매크로 지표를 매일 자동으로 모아 보여주는 정적 대시보드.
강의노트의 5축(금리 → 유동성 → 할인율 → 위험선호 → 경기·물가)을 종합 상황판과
매일/매주/매월 탭으로 정리하고, 각 지표에 의미·읽는 법·현재 상황 해석을 붙인다.

## 구조

```
scripts/        데이터 파이프라인 (파이썬)
  config.py       지표 목록 + 해석문 (단일 소스)
  fred.py         FRED 취득 + 샘플 폴백
  fetch.py        수집(값·변화 계산)
  interpret.py    판정(현재 상황 · 5축 신호등)
  build.py        조립 → docs/data 로 출력
docs/           대시보드 (GitHub Pages가 서빙)
  index.html / styles.css / app.js
  data/           build.py 산출물 (indicators.json, data.js)
.github/workflows/daily.yml   매일 1회 자동 갱신
.claude/        개발용 에이전트 · 개발 원칙 스킬
```

## 로컬에서 보기

```bash
python scripts/build.py                 # 데이터 생성 (키 없으면 샘플)
cd docs && python -m http.server 8899   # http://localhost:8899
```

`docs/index.html` 을 그냥 더블클릭해도 열린다(데이터를 `data.js`로도 내보내기 때문).

## 실데이터 연결 (FRED)

1. https://fred.stlouisfed.org/ 무료 가입 → API 키 발급
2. 로컬: `set FRED_API_KEY=키` (Windows) 후 `python scripts/build.py`
3. 자동화: GitHub 저장소 → Settings → Secrets → Actions 에 `FRED_API_KEY` 추가

## 배포 (GitHub Pages)

저장소 → Settings → Pages → Source: **Deploy from a branch**, Branch: **main / docs**.
이후 `https://<사용자>.github.io/<저장소>` 에서 열람. 매일 Action이 데이터를 갱신한다.

> 교육용 대시보드이며 투자조언이 아니다.
