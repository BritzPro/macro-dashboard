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
    if (unit === "pt") return v >= 1000 ? v.toLocaleString("en-US", { maximumFractionDigits: 1 }) : v.toFixed(1);
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
      '<div class="spark-wrap" title="클릭하면 크게 보기 · 호버로 값 확인">' +
      '<svg class="spark" viewBox="0 0 ' + W + " " + H + '" preserveAspectRatio="none" role="img">' +
      '<polyline fill="none" stroke="' + stroke + '" stroke-width="1.6" points="' + pts + '"/>' +
      '<circle cx="' + lx.toFixed(1) + '" cy="' + ly.toFixed(1) + '" r="2.4" fill="' + stroke + '"/>' +
      "</svg>" +
      '<span class="spark-zoom">⤢</span>' +
      "</div>"
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
      '<div class="card' + (unavail ? " unavail" : "") + (isSample ? " sampled" : "") + '" data-ind="' + ind.id + '">' +
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

  // ── 확대 차트(모달): 호버 툴팁 · 기간 확대/축소 ──
  var modal = document.getElementById("chart-modal");
  var RANGES = [{ k: "1M", d: 30 }, { k: "3M", d: 90 }, { k: "6M", d: 180 }, { k: "전체", d: null }];
  var chartState = { ind: null, days: null };

  function filterSeries(series, days) {
    if (!days) return series.slice();
    var cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - days);
    var iso = cutoff.toISOString().slice(0, 10);
    var f = series.filter(function (p) { return p.date >= iso; });
    return f.length >= 2 ? f : series.slice(); // 점이 너무 적으면 전체로
  }

  function renderChart() {
    var ind = chartState.ind;
    var series = filterSeries(ind.series, chartState.days);
    var n = series.length;
    var W = 820, H = 360, padL = 64, padR = 16, padT = 16, padB = 32;
    var plotW = W - padL - padR, plotH = H - padT - padB;
    var vals = series.map(function (p) { return p.value; });
    var rawMin = Math.min.apply(null, vals), rawMax = Math.max.apply(null, vals);
    var avg = vals.reduce(function (a, b) { return a + b; }, 0) / n;
    var first = series[0], lastp = series[n - 1];
    var min = rawMin, max = rawMax;
    var span = (max - min) || Math.abs(max) || 1;
    min -= span * 0.08; max += span * 0.08; span = max - min;
    function X(i) { return padL + (n < 2 ? plotW / 2 : (i / (n - 1)) * plotW); }
    function Y(v) { return padT + (1 - (v - min) / span) * plotH; }

    // 기간 통계바 (고점·저점·평균·기간 변화)
    var pctd = first.value ? (lastp.value - first.value) / Math.abs(first.value) * 100 : 0;
    var pcls = pctd > 0.001 ? "up" : pctd < -0.001 ? "down" : "flat";
    var parrow = pctd > 0.001 ? "▲" : pctd < -0.001 ? "▼" : "—";
    document.getElementById("cm-stats").innerHTML =
      '<span class="st"><span class="k">기간 변화</span><span class="chg ' + pcls + '">' + parrow + " " + Math.abs(pctd).toFixed(2) + "%</span></span>" +
      '<span class="st"><span class="k">고점</span>' + fmtValue(chartState.ind.unit, rawMax) + "</span>" +
      '<span class="st"><span class="k">저점</span>' + fmtValue(chartState.ind.unit, rawMin) + "</span>" +
      '<span class="st"><span class="k">평균</span>' + fmtValue(chartState.ind.unit, avg) + "</span>";

    var svg = '<svg id="cm-svg" viewBox="0 0 ' + W + " " + H + '">';
    var ticks = 4, t;
    for (t = 0; t <= ticks; t++) {
      var yv = min + span * t / ticks, yy = Y(yv);
      svg += '<line class="grid" x1="' + padL + '" y1="' + yy.toFixed(1) + '" x2="' + (W - padR) + '" y2="' + yy.toFixed(1) + '"/>';
      svg += '<text class="ylab" x="' + (padL - 8) + '" y="' + (yy + 3).toFixed(1) + '">' + fmtValue(ind.unit, yv) + "</text>";
    }
    // 평균 기준선 (점선)
    var avgY = Y(avg);
    svg += '<line class="avgline" x1="' + padL + '" y1="' + avgY.toFixed(1) + '" x2="' + (W - padR) + '" y2="' + avgY.toFixed(1) + '"/>';
    svg += '<text class="avglab" x="' + (W - padR) + '" y="' + (avgY - 4).toFixed(1) + '">평균</text>';
    var steps = Math.min(5, n - 1), s;
    for (s = 0; s <= steps; s++) {
      var xi = Math.round((n - 1) * s / Math.max(1, steps));
      svg += '<text class="xlab" x="' + X(xi).toFixed(1) + '" y="' + (H - 10) + '">' + series[xi].date.slice(5) + "</text>";
    }
    var linePts = series.map(function (p, i) { return X(i).toFixed(1) + "," + Y(p.value).toFixed(1); }).join(" ");
    var area = "M " + X(0).toFixed(1) + " " + (padT + plotH);
    series.forEach(function (p, i) { area += " L " + X(i).toFixed(1) + " " + Y(p.value).toFixed(1); });
    area += " L " + X(n - 1).toFixed(1) + " " + (padT + plotH) + " Z";
    svg += '<path class="area" d="' + area + '"/>';
    svg += '<polyline class="line" fill="none" points="' + linePts + '"/>';
    svg += '<circle class="lastdot" cx="' + X(n - 1).toFixed(1) + '" cy="' + Y(series[n - 1].value).toFixed(1) + '" r="3"/>';
    svg += '<line id="cm-cross" class="cross" y1="' + padT + '" y2="' + (padT + plotH) + '" style="display:none"/>';
    svg += '<circle id="cm-hoverdot" class="hoverdot" r="4" style="display:none"/>';
    svg += "</svg>";

    var area_el = document.getElementById("cm-chart");
    area_el.innerHTML = svg + '<div id="cm-tip" class="chart-tip" style="display:none"></div>';

    var svgEl = document.getElementById("cm-svg");
    var cross = document.getElementById("cm-cross");
    var hdot = document.getElementById("cm-hoverdot");
    var tip = document.getElementById("cm-tip");

    function onMove(e) {
      var r = svgEl.getBoundingClientRect();
      if (!r.width) return; // 레이아웃 크기 없으면(미표시 등) 무시
      var cx = (e.touches ? e.touches[0].clientX : e.clientX) - r.left;
      var frac = (cx / r.width * W - padL) / plotW;
      frac = Math.max(0, Math.min(1, frac));
      var idx = Math.round(frac * (n - 1));
      if (isNaN(idx) || !series[idx]) return;
      var p = series[idx];
      var px = X(idx), py = Y(p.value);
      cross.setAttribute("x1", px); cross.setAttribute("x2", px); cross.style.display = "";
      hdot.setAttribute("cx", px); hdot.setAttribute("cy", py); hdot.style.display = "";
      tip.style.display = "";
      tip.innerHTML = "<b>" + p.date + "</b><br>" + fmtValue(ind.unit, p.value);
      var leftPx = px / W * r.width, topPx = py / H * r.height;
      tip.style.left = Math.max(4, Math.min(r.width - tip.offsetWidth - 4, leftPx + 10)) + "px";
      tip.style.top = Math.max(4, topPx - 6) + "px";
    }
    function onLeave() { cross.style.display = "none"; hdot.style.display = "none"; tip.style.display = "none"; }
    svgEl.addEventListener("mousemove", onMove);
    svgEl.addEventListener("mouseleave", onLeave);
    svgEl.addEventListener("touchmove", onMove, { passive: true });
    svgEl.addEventListener("touchend", onLeave);
  }

  function openChart(id) {
    var ind = DATA.indicators[id];
    if (!ind || !ind.series || ind.series.length < 2) return;
    chartState.ind = ind;
    chartState.days = ind.cadence === "d" ? 90 : null; // 기본: 일간 3M, 주/월간 전체
    var sg = ind.signal || "neutral";
    document.getElementById("cm-name").innerHTML =
      ind.name + ' <span class="tag ' + sg + '">' + SIGNAL_KO[sg] + "</span>";
    document.getElementById("cm-sub").innerHTML =
      ind.id + " · " + (SRC_KO[ind.data_source || "fred"] || ind.data_source) +
      " · 최신 " + (ind.latest ? ind.latest.date : "") +
      " · " + fmtValue(ind.unit, ind.latest ? ind.latest.value : null);
    document.getElementById("cm-ranges").innerHTML = RANGES.map(function (rr) {
      var active = rr.d === chartState.days ? " active" : "";
      return '<button class="rbtn' + active + '" data-days="' + (rr.d || "") + '">' + rr.k + "</button>";
    }).join("");
    document.getElementById("cm-interp").innerHTML =
      '<div class="current">' + ind.current + "</div>" +
      '<div class="mini"><span class="k">의미</span>' + ind.meaning + "</div>" +
      '<div class="mini"><span class="k">읽는 법</span>' + ind.read + "</div>";
    renderChart();
    modal.hidden = false;
    document.body.style.overflow = "hidden";
  }

  function closeChart() {
    modal.hidden = true;
    document.body.style.overflow = "";
  }

  // 카드 차트 클릭 → 확대
  view.addEventListener("click", function (e) {
    var sp = e.target.closest(".spark-wrap");
    if (!sp) return;
    var c = sp.closest(".card");
    if (c && c.dataset.ind) openChart(c.dataset.ind);
  });
  // 기간 버튼
  document.getElementById("cm-ranges").addEventListener("click", function (e) {
    var b = e.target.closest(".rbtn");
    if (!b) return;
    chartState.days = b.dataset.days ? parseInt(b.dataset.days, 10) : null;
    [].forEach.call(this.querySelectorAll(".rbtn"), function (x) { x.classList.remove("active"); });
    b.classList.add("active");
    renderChart();
  });
  // 닫기
  document.getElementById("cm-close").addEventListener("click", closeChart);
  modal.addEventListener("click", function (e) { if (e.target === modal) closeChart(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !modal.hidden) closeChart(); });

  render("overview");
})();
