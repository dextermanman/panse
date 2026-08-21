#!/usr/bin/env python3
"""news.json -> dashboard.html (메뉴로 넘겨보는 뉴스 대시보드)."""
import html
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from string import Template

KST = timezone(timedelta(hours=9))
HERE = Path(__file__).parent

PAGE = Template(r"""<title>돌아가는 판세</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@500;600;700&display=swap">
<style>
:root{
  /* 종이에 가까운 따뜻한 바탕 */
  --ground:#FAF9F6; --surface:#FFFFFF; --surface-2:#F3F2EE; --tint:rgba(26,26,24,.035);
  --hairline:#E4E2DB; --hairline-2:#EFEEE9; --rule:#1A1A18;
  --ink:#1A1A18; --ink-2:#6B6B66; --ink-3:#9C9C95;
  --blue:#0B5FBF; --breaking:#B3261E; --breaking-bg:rgba(179,38,30,.08);
  --shadow:0 1px 2px rgba(26,26,24,.04), 0 10px 30px rgba(26,26,24,.055);
  --nav:rgba(250,249,246,.86); --live:#1F8F52; --live-halo:rgba(31,143,82,.16);
  --up:#C4362B; --down:#1B62C4;
$SWATCH_LIGHT
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ground:#0B0B0D; --surface:#1B1B1F; --surface-2:#26262B; --tint:rgba(255,255,255,.05);
    --hairline:#36363D; --hairline-2:#2A2A30; --rule:#E8E8E3;
    --ink:#F2F1EC; --ink-2:#A3A39C; --ink-3:#77776F;
    --blue:#6FB0FF; --breaking:#FF7A6E; --breaking-bg:rgba(255,122,110,.13);
    --shadow:0 1px 2px rgba(0,0,0,.55), 0 10px 30px rgba(0,0,0,.45);
    --nav:rgba(12,12,14,.86); --live:#3ECB7A; --live-halo:rgba(62,203,122,.18);
    --up:#FF7A6E; --down:#6FB0FF;
$SWATCH_DARK
  }
}
:root[data-theme="dark"]{
  --ground:#0B0B0D; --surface:#1B1B1F; --surface-2:#26262B; --tint:rgba(255,255,255,.05);
  --hairline:#36363D; --hairline-2:#2A2A30; --rule:#E8E8E3;
  --ink:#F2F1EC; --ink-2:#A3A39C; --ink-3:#77776F;
  --blue:#6FB0FF; --breaking:#FF7A6E; --breaking-bg:rgba(255,122,110,.13);
  --shadow:0 1px 2px rgba(0,0,0,.55), 0 10px 30px rgba(0,0,0,.45);
  --nav:rgba(12,12,14,.86); --live:#3ECB7A; --live-halo:rgba(62,203,122,.18);
  --up:#FF7A6E; --down:#6FB0FF;
$SWATCH_DARK
}
$TOPIC_CLASSES

*{box-sizing:border-box}
body{margin:0; background:var(--ground); color:var(--ink); font-size:15px; line-height:1.5;
  font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Apple SD Gothic Neo","Pretendard","Segoe UI",system-ui,sans-serif;
  -webkit-font-smoothing:antialiased; text-rendering:optimizeLegibility}
a{color:inherit; text-decoration:none}
button{font:inherit; color:inherit}
:focus-visible{outline:2px solid var(--blue); outline-offset:3px; border-radius:6px}
.hidden{display:none !important}

/* 한글은 단어 중간에서 끊기면 급격히 읽기 어려워진다 */
.hl{font-family:"Noto Serif KR","Nanum Myeongjo","Apple SD Gothic Neo",Georgia,serif}
/* 한글은 단어 중간에서 끊기면 급격히 읽기 어려워진다 */
body{word-break:keep-all; overflow-wrap:anywhere}
.b-title,.row-title,.f-title,.bd-teaser{text-wrap:pretty}

/* ---------- 상단 고정 ---------- */
.top{position:sticky; top:0; z-index:30; background:var(--nav);
  backdrop-filter:saturate(180%) blur(20px); -webkit-backdrop-filter:saturate(180%) blur(20px);
  border-bottom:1px solid var(--hairline)}
.top-in{max-width:1180px; margin:0 auto; padding:11px 28px 0; display:flex; align-items:center; gap:12px; flex-wrap:wrap}
.brand{font-family:"Noto Serif KR",Georgia,serif; font-size:17px; font-weight:700; letter-spacing:-.01em}
.nav-new{display:none; align-items:center; gap:6px; font-size:11.5px; font-weight:600;
  color:var(--breaking); background:var(--breaking-bg); padding:3px 9px; border-radius:980px}
.nav-new.show{display:inline-flex}
.top-right{margin-left:auto; display:flex; align-items:center; gap:11px;
  flex-wrap:wrap; row-gap:7px; justify-content:flex-end; min-width:0}
.stamp{font-size:11.5px; color:var(--ink-2); font-variant-numeric:tabular-nums; display:flex; align-items:center; gap:6px}
.dot-live{width:6px; height:6px; border-radius:50%; background:var(--live); box-shadow:0 0 0 3px var(--live-halo)}
@media (prefers-reduced-motion: no-preference){
  .dot-live{animation:pulse 2.8s ease-in-out infinite}
  @keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
}
.metals{display:flex; align-items:center; gap:14px; font-variant-numeric:tabular-nums;
  padding-right:13px; margin-right:-2px; border-right:1px solid var(--hairline)}
.metal{display:inline-flex; align-items:baseline; gap:5px; font-size:11.5px; white-space:nowrap}
.m-label{color:var(--ink-3); font-weight:600}
.m-value{color:var(--ink); font-weight:600; letter-spacing:-.01em}
.m-chg{font-size:10.5px; font-weight:700}
.m-chg.up{color:var(--up)}
.m-chg.down{color:var(--down)}
.m-chg.flat{color:var(--ink-3)}
.btn{border:1px solid var(--hairline); background:var(--surface); font-size:11.5px;
  padding:5px 11px; border-radius:980px; cursor:pointer; transition:background .15s ease}
.btn:hover{background:var(--surface-2)}

.menu-wrap{max-width:1180px; margin:0 auto; padding:11px 28px 13px}
.menu{display:flex; gap:8px; overflow-x:auto; scrollbar-width:none; -ms-overflow-style:none}
.menu::-webkit-scrollbar{display:none}
.m-btn{flex:none; display:inline-flex; align-items:center; gap:8px; cursor:pointer;
  border:1px solid var(--hairline); background:var(--surface); color:var(--ink-2);
  font-size:14.5px; font-weight:520; padding:9px 17px; border-radius:980px;
  transition:background .15s ease, color .15s ease, border-color .15s ease}
.m-btn:hover{background:var(--surface-2); color:var(--ink)}
.m-btn .swatch{width:9px; height:9px; border-radius:2px; background:var(--accent); flex:none}
.m-btn .n{font-size:11.5px; font-weight:700; color:var(--breaking); font-variant-numeric:tabular-nums}
.m-btn[aria-selected="true"]{background:var(--ink); color:var(--ground); border-color:var(--ink); font-weight:600}
.m-btn[aria-selected="true"] .n{color:var(--ground); opacity:.72}
.m-btn[aria-selected="true"] .swatch{box-shadow:0 0 0 1.5px var(--ground)}

main{max-width:1180px; margin:0 auto; padding:0 28px 76px}

/* ---------- 제호 ---------- */
.masthead{padding:36px 0 20px; border-bottom:2px solid var(--rule); margin-bottom:2px}
.masthead-in{display:flex; align-items:flex-end; gap:16px; flex-wrap:wrap}
.wordmark{font-family:"Noto Serif KR",Georgia,serif; font-size:39px; font-weight:700;
  letter-spacing:-.02em; line-height:1; margin:0}
.wordmark-sub{font-size:12.5px; color:var(--ink-2); margin:9px 0 0 2px; letter-spacing:.01em}
.masthead-date{margin-left:auto; text-align:right; font-size:12px; color:var(--ink-2);
  font-variant-numeric:tabular-nums; line-height:1.6}
.masthead-date b{display:block; font-size:13px; font-weight:600; color:var(--ink)}
.rule-thin{height:1px; background:var(--hairline); margin-bottom:30px}

/* ---------- 섹션 라벨 ---------- */
.zone-head{display:flex; align-items:center; gap:9px; margin:0 0 13px; flex-wrap:wrap}
.zone-title{display:flex; align-items:center; gap:8px; font-size:12px; font-weight:700;
  letter-spacing:.1em; text-transform:uppercase}
.zone-title::before{content:""; width:12px; height:2px; background:var(--rule)}
.zone-note{font-size:12px; color:var(--ink-3)}
.stack{display:flex; flex-direction:column; gap:34px}

/* ---------- 카드 공통 ---------- */
.card{background:var(--surface); border:1px solid var(--hairline); border-radius:14px;
  box-shadow:var(--shadow); overflow:hidden}
.card-head{display:flex; align-items:center; gap:10px; padding:13px 20px; border-bottom:1px solid var(--hairline)}
.pill-live{display:inline-flex; align-items:center; gap:6px; background:var(--breaking-bg); color:var(--breaking);
  font-size:10.5px; font-weight:700; letter-spacing:.09em; padding:4px 10px; border-radius:980px}
.eyebrow{font-size:10.5px; font-weight:600; letter-spacing:.09em; text-transform:uppercase; color:var(--ink-3)}
.card-count{margin-left:auto; font-size:11px; color:var(--ink-3); font-variant-numeric:tabular-nums}

/* ---------- 속보: 첫 기사를 지면 톱처럼 ---------- */
.b-list{list-style:none; margin:0; padding:0}
.b-list li + li{border-top:1px solid var(--hairline-2)}
.b-item{display:flex; align-items:baseline; gap:14px; padding:13px 20px; transition:background .15s ease}
.b-item:hover{background:var(--tint)}
.b-time{flex:none; width:50px; font-size:11.5px; color:var(--ink-3); font-variant-numeric:tabular-nums}
.b-title{flex:1; min-width:0; font-size:16px; font-weight:500; line-height:1.5}
.b-list li:first-child .b-item{padding:20px 20px 21px; align-items:flex-start}
.b-list li:first-child .b-title{font-family:"Noto Serif KR","Nanum Myeongjo",Georgia,serif;
  font-size:23px; font-weight:600; line-height:1.45; letter-spacing:-.01em}
.b-list li:first-child .b-time{padding-top:7px}
.b-tag{flex:none; display:inline-flex; align-items:center; gap:6px; font-size:11px; color:var(--ink-2)}
.b-tag .swatch{width:7px; height:7px; border-radius:2px; background:var(--accent)}
.b-src{flex:none; font-size:11px; color:var(--ink-3); width:80px; text-align:right;
  overflow:hidden; text-overflow:ellipsis; white-space:nowrap}

/* ---------- 메뉴판 ---------- */
.board{list-style:none; margin:0; padding:0; background:var(--surface);
  border:1px solid var(--hairline); border-radius:14px; box-shadow:var(--shadow); overflow:hidden}
.board li + li{border-top:1px solid var(--hairline-2)}
.bd-row{display:grid; grid-template-columns:3px 128px 1fr auto 16px; align-items:center;
  gap:0 18px; padding:0; cursor:pointer; width:100%; text-align:left;
  border:0; background:transparent; transition:background .15s ease}
.bd-row:hover{background:var(--tint)}
.bd-bar{align-self:stretch; background:var(--accent)}
.bd-name{padding:15px 0; font-size:15.5px; font-weight:600; letter-spacing:-.015em}
.bd-teaser{font-size:13.5px; color:var(--ink-2); overflow:hidden;
  text-overflow:ellipsis; white-space:nowrap; padding:16px 0}
.bd-nums{display:flex; align-items:center; gap:9px; padding:16px 0; white-space:nowrap}
.bd-new{font-size:11px; font-weight:700; color:var(--breaking);
  background:var(--breaking-bg); padding:3px 8px; border-radius:980px; font-variant-numeric:tabular-nums}
.bd-total{font-size:11.5px; color:var(--ink-3); font-variant-numeric:tabular-nums}
.bd-go{font-size:16px; color:var(--ink-3); padding-right:18px; transition:transform .15s ease, color .15s ease}
.bd-row:hover .bd-go{color:var(--ink-2); transform:translateX(3px)}

/* ---------- 전체 흐름 ---------- */
.feed{list-style:none; margin:0; padding:0}
.feed li + li{border-top:1px solid var(--hairline-2)}
.f-row{display:grid; grid-template-columns:50px 112px 1fr 88px; gap:14px;
  align-items:baseline; padding:9px 20px; transition:background .15s ease}
.f-row:hover{background:var(--tint)}
.f-time{font-size:11px; color:var(--ink-3); font-variant-numeric:tabular-nums}
.f-tag{display:inline-flex; align-items:center; gap:6px; font-size:11px; color:var(--ink-2);
  overflow:hidden; white-space:nowrap}
.f-tag .swatch{width:7px; height:7px; border-radius:2px; background:var(--accent); flex:none}
.f-title{font-size:14px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap}
.f-row:hover .f-title{color:var(--blue)}
.f-src{font-size:11px; color:var(--ink-3); text-align:right; overflow:hidden;
  text-overflow:ellipsis; white-space:nowrap}
.more{display:block; width:100%; padding:12px; border:0; border-top:1px solid var(--hairline);
  background:var(--surface); color:var(--blue); font-size:12.5px; font-weight:520;
  cursor:pointer; transition:background .15s ease}
.more:hover{background:var(--surface-2)}

/* ---------- 주제 보기 ---------- */
.detail{margin-top:30px}
.detail-head{display:flex; align-items:baseline; gap:16px; padding:22px 22px 18px;
  border-bottom:2px solid var(--rule); flex-wrap:wrap}
.detail-name{display:flex; align-items:center; gap:11px; font-size:27px; font-weight:700; letter-spacing:-.025em}
.detail-name .swatch{width:11px; height:11px; border-radius:3px; background:var(--accent)}
.detail-stat{font-size:12px; color:var(--ink-2)}
.detail-stat b{font-size:15px; font-weight:600; color:var(--ink); font-variant-numeric:tabular-nums}
.d-list{list-style:none; margin:0; padding:0; display:grid;
  grid-template-columns:repeat(auto-fill,minmax(330px,1fr))}
.group{grid-column:1/-1; padding:16px 22px 6px; font-size:10.5px; font-weight:700;
  letter-spacing:.1em; text-transform:uppercase; color:var(--ink-3); border-top:1px solid var(--hairline-2)}
.group:first-child{border-top:0; padding-top:14px}
.d-item{border-top:1px solid var(--hairline-2)}
.row{display:block; padding:13px 22px; height:100%; transition:background .15s ease}
.row:hover{background:var(--tint)}
.row-title{font-size:15.5px; font-weight:500; line-height:1.55;
  display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden}
.row:hover .row-title{color:var(--blue)}
.row-meta{margin-top:6px; font-size:11px; color:var(--ink-3); display:flex; gap:6px;
  align-items:center; font-variant-numeric:tabular-nums}
.sep{opacity:.45}
.badge{color:var(--breaking); font-weight:700; font-size:10px; letter-spacing:.05em}

footer{border-top:1px solid var(--hairline); margin-top:40px; padding-top:20px;
  font-size:11.5px; color:var(--ink-3); display:flex; gap:8px; flex-wrap:wrap}

@media (max-width:760px){
  .bd-row{grid-template-columns:3px 1fr auto 16px; gap:0 13px}
  .bd-name{padding:13px 0 2px; grid-column:2; font-size:16px}
  .bd-teaser{grid-column:2; padding:0 0 13px; font-size:12.5px; white-space:normal;
    display:-webkit-box; -webkit-line-clamp:1; -webkit-box-orient:vertical}
  .bd-nums{grid-column:3; grid-row:1/3}
  .bd-go{grid-column:4; grid-row:1/3}
  .f-row{grid-template-columns:46px 1fr; gap:3px 10px; padding:10px 20px}
  .f-tag{grid-column:2; order:3; font-size:10.5px}
  .f-title{grid-column:2; white-space:normal; line-height:1.5;
    display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical}
  .f-src{display:none}
}
@media (max-width:640px){
  main{padding:0 18px 56px}
  .top-in{padding:10px 18px 0}
  .menu-wrap{padding:9px 18px 10px}
  /* 좁은 화면: 오른쪽 묶음이 한 줄을 통째로 쓰게 해서 버튼이 잘리지 않게 */
  .top-right{flex:1 1 100%; margin-left:0; justify-content:flex-start}
  .stamp-sfx{display:none}
  .metals{order:3; flex-basis:100%; justify-content:flex-start;
    border-right:0; padding-right:0; margin-right:0; gap:13px;
    overflow-x:auto; scrollbar-width:none}
  .metals::-webkit-scrollbar{display:none}
  .stamp{font-size:11px}
  .btn{padding:5px 10px}
  .masthead{padding:26px 0 16px}
  .wordmark{font-size:31px}
  .wordmark-sub{font-size:11.5px}
  .masthead-date{margin-left:0; text-align:left}
  .stack{gap:28px}
  .b-list li:first-child .b-title{font-size:20px}
  .b-src{display:none}
  .detail-name{font-size:23px}
}
</style>

<div class="top">
  <div class="top-in">
    <span class="brand">돌아가는 판세</span>
    <span class="nav-new" id="navnew"></span>
    <span class="top-right">
$METALS
      <span class="stamp"><span class="dot-live"></span>$UPDATED_HM<span class="stamp-sfx"> 갱신 · 30분마다</span></span>
      <button class="btn" id="refresh" type="button">새로고침</button>
    </span>
  </div>
  <div class="menu-wrap">
    <div class="menu" role="tablist" aria-label="주제 메뉴">
      <button class="m-btn" type="button" role="tab" data-view="all" aria-selected="true">전체</button>
$MENU
    </div>
  </div>
</div>

<main>
  <header class="masthead">
    <div class="masthead-in">
      <div>
        <h1 class="wordmark hl">돌아가는 판세</h1>
        <p class="wordmark-sub">중동전쟁 · 반도체 · 디스플레이 · 주식 · AI · 배터리 · 세계 경제</p>
      </div>
      <div class="masthead-date">
        <b>$DATE_LONG</b>
        구글 뉴스에서 모은 $TOTAL건
      </div>
    </div>
  </header>
  <div class="rule-thin"></div>

  <div id="overview" class="stack">
    <section aria-labelledby="z2">
      <div class="zone-head">
        <span class="zone-title" id="z2">$BREAKING_LABEL</span>
        <span class="zone-note">$BREAKING_NOTE</span>
      </div>
      <div class="card">
        <ul class="b-list">
$BREAKING
        </ul>
      </div>
    </section>

    <section aria-labelledby="z1">
      <div class="zone-head">
        <span class="zone-title" id="z1">무엇을 볼까</span>
        <span class="zone-note">빨간 숫자는 최근 1시간에 새로 들어온 기사</span>
      </div>
      <ul class="board">
$BOARD
      </ul>
    </section>

    <section aria-labelledby="z3">
      <div class="zone-head">
        <span class="zone-title" id="z3">전체 흐름</span>
        <span class="zone-note">일곱 갈래를 시간순으로</span>
      </div>
      <div class="card">
        <ul class="feed">
$FEED
        </ul>
        <button class="more" id="more" type="button">나머지 $REST건 모두 보기</button>
      </div>
    </section>
  </div>

$DETAILS

  <footer>
    <span>구글 뉴스 RSS · 최근 3일</span><span>·</span>
    <span>유사 기사와 홍보성 기사는 자동으로 걸러냅니다</span><span>·</span>
    <span>다음 갱신 <span id="countdown">–</span></span>
  </footer>
</main>

<script>
(function(){
  var GEN = $GEN_TS * 1000, PERIOD = 30 * 60 * 1000;
  /* 카운트다운 기준이 모두 같으면 열려 있는 탭이 한꺼번에 새로고침된다.
     사람이 많아질수록 같은 순간에 몰리므로 탭마다 0~2분을 흩뿌린다. */
  var DEADLINE = GEN + PERIOD + Math.floor(Math.random() * 120000);
  var NAMES = $NAMES;

  function rel(ts){
    var m = Math.floor((Date.now() - ts * 1000) / 60000);
    if (m < 1) return "방금";
    if (m < 60) return m + "분 전";
    var h = Math.floor(m / 60);
    if (h < 24) return h + "시간 전";
    return Math.floor(h / 24) + "일 전";
  }
  function paintTimes(){
    document.querySelectorAll("[data-ts]").forEach(function(el){
      el.textContent = rel(Number(el.getAttribute("data-ts")));
    });
  }
  paintTimes(); setInterval(paintTimes, 60000);

  /* 지난번에 본 이후 들어온 기사 */
  try {
    var seen = Number(localStorage.getItem("news-seen") || 0), n = 0;
    if (seen) {
      document.querySelectorAll(".f-item [data-ts]").forEach(function(el){
        if (Number(el.getAttribute("data-ts")) > seen) n++;
      });
      if (n > 0) {
        var nb = document.getElementById("navnew");
        nb.textContent = "지난번 이후 " + n + "건";
        nb.classList.add("show");
      }
    }
    localStorage.setItem("news-seen", String(Math.floor(Date.now() / 1000)));
  } catch (e) {}

  /* 다음 갱신 카운트다운 */
  var cd = document.getElementById("countdown");
  function tick(){
    var left = DEADLINE - Date.now();
    if (left <= 0){ location.reload(); return; }
    var m = Math.floor(left / 60000), s = Math.floor(left % 60000 / 1000);
    cd.textContent = m + "분 " + (s < 10 ? "0" : "") + s + "초";
  }
  tick(); setInterval(tick, 1000);
  document.getElementById("refresh").addEventListener("click", function(){ location.reload(); });

  /* 전체 흐름은 기본 24건만 */
  var LIMIT = 18, expanded = false;
  var feedRows = [].slice.call(document.querySelectorAll(".f-item"));
  var more = document.getElementById("more");
  function paintFeed(){
    feedRows.forEach(function(r, i){ r.classList.toggle("hidden", !expanded && i >= LIMIT); });
    more.classList.toggle("hidden", expanded || feedRows.length <= LIMIT);
  }
  more.addEventListener("click", function(){ expanded = true; paintFeed(); });
  paintFeed();

  /* 메뉴 = 화면 전환. 전체 보기와 주제 보기는 한 번에 하나만 뜬다 */
  var overview = document.getElementById("overview");
  var details = [].slice.call(document.querySelectorAll(".detail"));
  var menu = [].slice.call(document.querySelectorAll(".m-btn"));

  function show(view){
    overview.classList.toggle("hidden", view !== "all");
    details.forEach(function(d){ d.classList.toggle("hidden", d.dataset.topic !== view); });
    menu.forEach(function(b){ b.setAttribute("aria-selected", String(b.dataset.view === view)); });
    document.title = (view === "all" ? "돌아가는 판세" : NAMES[view] + " · 돌아가는 판세");
  }
  var cur = "all";
  try { cur = localStorage.getItem("news-view") || "all"; } catch (e) {}
  if (cur !== "all" && !NAMES[cur]) cur = "all";
  show(cur);

  function go(view){
    cur = view;
    try { localStorage.setItem("news-view", view); } catch (e) {}
    show(view);
    var soft = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    window.scrollTo({ top: 0, behavior: soft ? "auto" : "smooth" });
  }
  menu.forEach(function(b){ b.addEventListener("click", function(){ go(b.dataset.view); }); });
  document.querySelectorAll(".bd-row").forEach(function(r){
    r.addEventListener("click", function(){ go(r.dataset.topic); });
  });
})();
</script>
""")


def esc(s):
    return html.escape(str(s), quote=True)


# (기호, 라벨, 접두, 소수점, 설명)
TICKER = (
    ("gold",   "금",     "$", 0, "금 현물 · 미국 달러/트로이온스"),
    ("silver", "은",     "$", 2, "은 현물 · 미국 달러/트로이온스"),
    ("usdkrw", "달러",   "₩", 1, "원/달러 · 하나은행 매매기준율"),
    ("jpykrw", "엔100",  "₩", 1, "원/100엔 · 하나은행 매매기준율"),
)


def market_html(m):
    """상단 시세 티커. 등락률은 이력이 24시간 쌓인 뒤부터 나온다."""
    if not m:
        return ""
    rows = []
    for key, label, prefix, digits, tip in TICKER:
        val = m.get(key)
        if val is None:
            continue
        tip = f"{tip} ({m['fx_time']} 고시)" if key.endswith("krw") and m.get("fx_time") else tip
        chg = m.get(f"{key}_chg")
        if chg is None:
            tag = ""
        elif chg > 0:
            tag = f'<span class="m-chg up">▲{chg:.2f}%</span>'
        elif chg < 0:
            tag = f'<span class="m-chg down">▼{abs(chg):.2f}%</span>'
        else:
            tag = '<span class="m-chg flat">0.00%</span>'
        rows.append(
            '        <span class="metal" title="{tip}">'
            '<span class="m-label">{label}</span>'
            '<span class="m-value">{prefix}{val:,.{d}f}</span>{tag}</span>'.format(
                tip=tip, label=label, prefix=prefix, val=val, d=digits, tag=tag)
        )
    if not rows:
        return ""
    stale = ' title="시세를 새로 받지 못해 직전 값입니다"' if m.get("stale") else ""
    return f'      <span class="metals"{stale}>\n' + "\n".join(rows) + "\n      </span>"


WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]


def date_long(now):
    return f"{now.year}년 {now.month}월 {now.day}일 {WEEKDAYS[now.weekday()]}요일"


def build():
    data = json.loads((HERE / "news.json").read_text(encoding="utf-8"))
    now = datetime.now(KST)
    topics = data["topics"]

    # 색은 반드시 토큰으로만 참조해야 다크 모드에서 깨지지 않는다
    light = "\n".join(f'  --c-{t["id"]}:{t["accent"]};' for t in topics)
    dark = "\n".join(f'    --c-{t["id"]}:{t["accent_dark"]};' for t in topics)
    classes = "\n".join(f'.t-{t["id"]}{{--accent:var(--c-{t["id"]})}}' for t in topics)

    # ---- 속보를 먼저 정한다 (이후 블록은 여기 쓰인 기사를 피한다) ----
    flat = sorted(((it, t) for t in topics for it in t["items"]), key=lambda p: -p[0]["ts"])
    fresh = [p for p in flat if now.timestamp() - p[0]["ts"] <= 90 * 60][:5]
    label, note, picks = ("속보", "최근 90분 안에 들어온 기사", fresh) if fresh \
        else ("최신", "가장 최근에 들어온 기사", flat[:5])
    used = {it["link"] for it, _ in picks}

    breaking = "\n".join(
        '        <li><a class="b-item t-{id}" href="{link}" target="_blank" rel="noopener">'
        '<span class="b-time" data-ts="{ts}">–</span><span class="b-title">{title}</span>'
        '<span class="b-tag"><span class="swatch"></span>{topic}</span>'
        '<span class="b-src">{src}</span></a></li>'.format(
            id=t["id"], link=esc(it["link"]), ts=it["ts"], title=esc(it["title"]),
            topic=esc(t["name"]), src=esc(it["source"]))
        for it, t in picks
    )

    # ---- 메뉴 + 메뉴판 ----
    menu, board, details = [], [], []
    for t in topics:
        n = t["fresh_1h"]
        badge = f'<span class="n">+{n}</span>' if n else ""
        menu.append(
            '      <button class="m-btn t-{id}" type="button" role="tab" data-view="{id}" aria-selected="false">'
            '<span class="swatch"></span>{name}{badge}</button>'.format(
                id=t["id"], name=esc(t["name"]), badge=badge)
        )
        # 미리보기는 속보에 이미 나온 기사를 피한다
        teaser_item = next((it for it in t["items"] if it["link"] not in used), None)
        if teaser_item:
            used.add(teaser_item["link"])
        teaser = esc(teaser_item["title"]) if teaser_item else "새 기사 없음"
        board.append(
            '        <li><button class="bd-row t-{id}" type="button" data-topic="{id}">\n'
            '          <span class="bd-bar"></span>\n'
            '          <span class="bd-name">{name}</span>\n'
            '          <span class="bd-teaser">{teaser}</span>\n'
            '          <span class="bd-nums">{new}<span class="bd-total">{total}건</span></span>\n'
            '          <span class="bd-go" aria-hidden="true">›</span>\n'
            "        </button></li>".format(
                id=t["id"], name=esc(t["name"]), teaser=teaser, total=t["total"],
                new=f'<span class="bd-new">+{n}</span>' if n else "")
        )

    # ---- 전체 흐름: 위에서 이미 보여준 기사는 뺀다 ----
    rest = [(it, t) for it, t in flat if it["link"] not in used]
    feed = "\n".join(
        '          <li class="f-item" data-topic="{id}">'
        '<a class="f-row t-{id}" href="{link}" target="_blank" rel="noopener">'
        '<span class="f-time" data-ts="{ts}">–</span>'
        '<span class="f-tag"><span class="swatch"></span>{topic}</span>'
        '<span class="f-title">{title}</span>'
        '<span class="f-src">{src}</span></a></li>'.format(
            id=t["id"], link=esc(it["link"]), ts=it["ts"], topic=esc(t["name"]),
            title=esc(it["title"]), src=esc(it["source"]))
        for it, t in rest
    )

    # ---- 주제 보기 ----
    today = now.date()

    def bucket(ts):
        d = datetime.fromtimestamp(ts, KST)
        if now.timestamp() - ts <= 3600:
            return "지금 · 1시간 내"
        if d.date() == today:
            return "오늘"
        if d.date() == today - timedelta(days=1):
            return "어제"
        return "그 이전"

    for t in topics:
        rows, last = [], None
        for it in t["items"]:
            b = bucket(it["ts"])
            if b != last:
                rows.append(f'        <li class="group">{b}</li>')
                last = b
            is_new = now.timestamp() - it["ts"] <= 3600
            rows.append(
                '        <li class="d-item"><a class="row" href="{link}" target="_blank" rel="noopener">'
                '<div class="row-title">{title}</div>'
                '<div class="row-meta">{badge}<span>{src}</span>'
                '<span class="sep">·</span><span data-ts="{ts}">–</span></div></a></li>'.format(
                    link=esc(it["link"]), title=esc(it["title"]),
                    badge='<span class="badge">NEW</span><span class="sep">·</span>' if is_new else "",
                    src=esc(it["source"]), ts=it["ts"])
            )
        details.append(
            '  <section class="detail card t-{id}" data-topic="{id}" aria-label="{name}">\n'
            '    <div class="detail-head">\n'
            '      <span class="detail-name hl"><span class="swatch"></span>{name}</span>\n'
            '      <span class="detail-stat"><b>{fresh}</b>건 최근 1시간</span>\n'
            '      <span class="detail-stat"><b>{total}</b>건 오늘 수집</span>\n'
            "    </div>\n"
            '    <ul class="d-list">\n{rows}\n    </ul>\n'
            "  </section>".format(
                id=t["id"], name=esc(t["name"]), fresh=t["fresh_1h"], total=t["total"],
                rows="\n".join(rows))
        )

    out = PAGE.substitute(
        SWATCH_LIGHT=light, SWATCH_DARK=dark, TOPIC_CLASSES=classes,
        UPDATED_HM=now.strftime("%H:%M"), DATE_LONG=date_long(now),
        METALS=market_html(data.get("market")),
        MENU="\n".join(menu), BOARD="\n".join(board), BREAKING=breaking,
        BREAKING_LABEL=label, BREAKING_NOTE=note, FEED=feed, TOTAL=len(flat), REST=len(rest),
        DETAILS="\n".join(details),
        NAMES=json.dumps({t["id"]: t["name"] for t in topics}, ensure_ascii=False),
        GEN_TS=int(now.timestamp()),
    )
    path = HERE / "dashboard.html"
    path.write_text(out, encoding="utf-8")
    print(f"렌더 완료: 속보 {len(picks)} · 메뉴판 {len(topics)} · 전체흐름 {len(rest)} · 총 {len(flat)} (중복 0)")
    return path


if __name__ == "__main__":
    build()
