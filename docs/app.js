/* 매크로 대시보드 렌더러
   데이터는 build.py가 생성한 window.__MACRO_DATA__ 에서 읽는다. */
(function () {
  var DATA = window.__MACRO_DATA__;
  var view = document.getElementById("view");
  var SIGNAL_KO = { good: "우호적", neutral: "중립", bad: "부담" };
  var CADENCE_KO = { d: "매일", w: "매주", m: "매월" };

  if (!DATA) {
    view.innerHTML = '<p style="color:var(--muted)">데이터를 불러오지 못했습니다. <code>python scripts/build.py</code>를 먼저 실행하세요.</p>';
    return;
  }

  // ── 상단 배지: 실데이터/샘플 카운터 ──
  var SRC_KO = { fred: "FRED", yahoo: "Yahoo", cboe: "Cboe", sample: "샘플(추정)" };
  var badge = document.getElementById("source-badge");
  var ds = DATA.data_status || { real: 0, total: 0, sample: 0 };
  if (ds.sample === 0) {
    badge.textContent = "실데이터 " + ds.real + "/" + ds.total;
    badge.className = "badge fred";
  } else {
    badge.textContent = "⚠ 샘플 " + ds.sample + "개 포함 (" + ds.real + "/" + ds.total + " 실데이터)";
    badge.className = "badge sample";
  }
  try {
    var dt = new Date(DATA.generated_at);
    document.getElementById("updated").textContent =
      "업데이트 " + dt.toLocaleString("ko-KR", { dateStyle: "medium", timeStyle: "short" });
  } catch (e) {}

  // ── 값 포맷 ──
  function fmtValue(unit, v) {
    if (v == null || isNaN(v)) return "—";
    if (unit === "백만$") return (v / 1e6).toFixed(2) + "조$";
    if (unit === "십억$") return v >= 1000 ? (v / 1000).toFixed(2) + "조$" : v.toFixed(1) + "십억$";
    if (unit === "%") return v.toFixed(2) + "%";
    if (unit === "천명") return Math.round(v).toLocaleString("ko-KR") + "천명";
    if (unit === "원") return v.toFixed(1) + "원";
    if (unit === "$") return v >= 1000 ? "$" + Math.round(v).toLocaleString("en-US") : "$" + v.toFixed(1);
    if (unit === "ratio") return v.toFixed(2) + "배";
    if (unit === "pt") return v.toFixed(1);
    return v.toFixed(1);
  }

  function changeHtml(ind) {
    var p = ind.change_pct;
    if (p == null || isNaN(p)) return '<span class="chg flat">—</span>';
    var cls = p > 0.001 ? "up" : p < -0.001 ? "down" : "flat";
    var arrow = p > 0.001 ? "▲" : p < -0.001 ? "▼" : "—";
    return '<span class="chg ' + cls + '">' + arrow + " " + Math.abs(p).toFixed(2) + "%</span>";
  }

  // ── 스파크라인 (자체 SVG, 외부 라이브러리 없음) ──
  function sparkline(series, signal) {
    if (!series || series.length < 2) return "";
    var W = 300, H = 56, pad = 4;
    var vals = series.map(function (p) { return p.value; });
    var min = Math.min.apply(null, vals), max = Math.max.apply(null, vals);
    var span = max - min || 1;
    var n = series.length;
    var pts = series.map(function (p, i) {
      var x = pad + (i / (n - 1)) * (W - 2 * pad);
      var y = pad + (1 - (p.value - min) / span) * (H - 2 * pad);
      return x.toFixed(1) + "," + y.toFixed(1);
    }).join(" ");
    var stroke = "var(--line)";
    var last = series[n - 1];
    var lx = W - pad, ly = pad + (1 - (last.value - min) / span) * (H - 2 * pad);
    return (
      '<svg class="spark" viewBox="0 0 ' + W + " " + H + '" preserveAspectRatio="none" role="img">' +
      '<polyline fill="none" stroke="' + stroke + '" stroke-width="1.6" points="' + pts + '"/>' +
      '<circle cx="' + lx.toFixed(1) + '" cy="' + ly.toFixed(1) + '" r="2.4" fill="' + stroke + '"/>' +
      "</svg>"
    );
  }

  // ── 지표 카드 ──
  function card(ind) {
    var unavail = ind.status !== "ok";
    var latest = ind.latest ? ind.latest.value : null;
    var sig = ind.signal || "neutral";
    var source = ind.data_source || "fred";
    var isSample = source === "sample";
    var sampleWarn = isSample
      ? '<div class="sample-warn">⚠ 이 값은 소스 연결 실패로 <b>샘플(추정)</b>입니다 — 실제 값 아님</div>'
      : "";
    return (
      '<div class="card' + (unavail ? " unavail" : "") + (isSample ? " sampled" : "") + '">' +
        '<div class="card-head">' +
          '<div><div class="card-name">' + ind.name + '</div>' +
          '<div class="card-id">' + ind.id + " · " + (SRC_KO[source] || source) +
            " · " + (ind.latest ? ind.latest.date : "") + "</div></div>" +
          '<div class="card-val"><span class="v">' + fmtValue(ind.unit, latest) + "</span>" +
          "<div>" + changeHtml(ind) + "</div></div>" +
        "</div>" +
        sampleWarn +
        sparkline(ind.series, sig) +
        '<div class="signal-row">현재 판정: <span class="tag ' + sig + '">' + SIGNAL_KO[sig] + "</span></div>" +
        '<div class="interp">' +
          '<div class="current">' + ind.current + "</div>" +
          "<details><summary>지표 설명 보기</summary>" +
            '<div class="block"><span class="k">의미</span>' + ind.meaning + "</div>" +
            '<div class="block"><span class="k">읽는 법</span>' + ind.read + "</div>" +
          "</details>" +
        "</div>" +
      "</div>"
    );
  }

  // ── 종합 상황판 ──
  function renderOverview() {
    var o = DATA.overall;
    var html =
      '<div class="headline">' +
        '<div class="lbl">오늘의 종합 판정</div>' +
        '<div class="big"><span class="dot ' + o.label + '"></span>' + SIGNAL_KO[o.label] + " 국면</div>" +
        '<div class="desc">' + o.headline + "</div>" +
      "</div>";

    html += '<div class="axis-grid">';
    ["rates", "liquidity", "discount", "risk", "macro"].forEach(function (a) {
      var s = DATA.axis_signal[a];
      if (!s) return;
      html +=
        '<div class="axis-card ' + s.label + '">' +
          '<div class="name">' + s.title + "</div>" +
          '<div class="state ' + s.label + '"><span class="dot ' + s.label + '"></span>' + SIGNAL_KO[s.label] + "</div>" +
        "</div>";
    });
    html += "</div>";
    html += '<p class="section-title">각 축을 눌러 상세 지표는 매일·매주·매월 탭에서 확인하세요.</p>';
    view.innerHTML = html;
  }

  // ── 주기별 탭 ──
  var AXIS_ORDER = ["rates", "liquidity", "discount", "risk", "macro"];
  function renderCadence(cad) {
    var inds = Object.keys(DATA.indicators)
      .map(function (k) { return DATA.indicators[k]; })
      .filter(function (i) { return i.cadence === cad; });

    var html = '<p class="section-title">' + CADENCE_KO[cad] + " 확인할 지표 · " + inds.length + "개</p>";
    AXIS_ORDER.forEach(function (axis) {
      var group = inds.filter(function (i) { return i.axis === axis; });
      if (!group.length) return;
      html += '<p class="section-title">' + DATA.axes[axis] + "</p>";
      html += '<div class="cards">' + group.map(card).join("") + "</div>";
    });
    view.innerHTML = html;
  }

  // ── 탭 전환 ──
  function render(tab) {
    if (tab === "overview") renderOverview();
    else renderCadence(tab);
  }
  document.getElementById("tabs").addEventListener("click", function (e) {
    var btn = e.target.closest(".tab");
    if (!btn) return;
    document.querySelectorAll(".tab").forEach(function (t) { t.classList.remove("active"); });
    btn.classList.add("active");
    render(btn.dataset.tab);
  });

  render("overview");
})();
