#!/usr/bin/env python3
"""news.json -> dashboard.html (Apple 스타일 미니멀 프리미엄 뉴스 대시보드)."""
import html
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from string import Template

KST = timezone(timedelta(hours=9))
HERE = Path(__file__).parent

PAGE = Template(r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>돌아가는 판세</title>
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="주요 8대 산업·경제 뉴스와 금·은 시세, 환율을 30분마다 모으는 대시보드">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="판세">
<meta name="theme-color" content="#FAF9F6" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0B0B0D" media="(prefers-color-scheme: dark)">
<link rel="manifest" href="/manifest.json">
<link rel="apple-touch-icon" href="/icon.svg">
<link rel="icon" type="image/svg+xml" href="/icon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@500;600;700&display=swap">
<style>
:root{
  /* Apple 테마 & 종이 감성 결합 */
  --ground:#FAF9F6; --surface:rgba(255,255,255,0.86); --surface-solid:#FFFFFF; --surface-2:#F3F2EE; --tint:rgba(26,26,24,0.035);
  --hairline:rgba(26,26,24,0.08); --hairline-2:rgba(26,26,24,0.04); --rule:#1A1A18;
  --ink:#1D1D1F; --ink-2:#6E6E73; --ink-3:#86868B;
  --blue:#0071E3; --breaking:#FF3B30; --breaking-bg:rgba(255,59,48,0.08);
  --shadow:0 4px 24px rgba(0,0,0,0.035), 0 1px 3px rgba(0,0,0,0.02);
  --nav:rgba(250,249,246,0.84); --live:#34C759; --live-halo:rgba(52,199,89,0.16);
  --up:#FF3B30; --down:#0071E3;
$SWATCH_LIGHT
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ground:#0B0B0E; --surface:rgba(28,28,30,0.84); --surface-solid:#1C1C1E; --surface-2:#2C2C2E; --tint:rgba(255,255,255,0.05);
    --hairline:rgba(255,255,255,0.12); --hairline-2:rgba(255,255,255,0.06); --rule:#E8E8E3;
    --ink:#F5F5F7; --ink-2:#A1A1A6; --ink-3:#86868B;
    --blue:#2997FF; --breaking:#FF453A; --breaking-bg:rgba(255,69,58,0.14);
    --shadow:0 8px 32px rgba(0,0,0,0.55), 0 1px 4px rgba(0,0,0,0.3);
    --nav:rgba(11,11,14,0.84); --live:#30D158; --live-halo:rgba(48,209,88,0.2);
    --up:#FF453A; --down:#2997FF;
$SWATCH_DARK
  }
}
:root[data-theme="dark"]{
  --ground:#0B0B0E; --surface:rgba(28,28,30,0.84); --surface-solid:#1C1C1E; --surface-2:#2C2C2E; --tint:rgba(255,255,255,0.05);
  --hairline:rgba(255,255,255,0.12); --hairline-2:rgba(255,255,255,0.06); --rule:#E8E8E3;
  --ink:#F5F5F7; --ink-2:#A1A1A6; --ink-3:#86868B;
  --blue:#2997FF; --breaking:#FF453A; --breaking-bg:rgba(255,69,58,0.14);
  --shadow:0 8px 32px rgba(0,0,0,0.55), 0 1px 4px rgba(0,0,0,0.3);
  --nav:rgba(11,11,14,0.84); --live:#30D158; --live-halo:rgba(48,209,88,0.2);
  --up:#FF453A; --down:#2997FF;
$SWATCH_DARK
}
$TOPIC_CLASSES

*{box-sizing:border-box}
body{margin:0; background:var(--ground); color:var(--ink); font-size:15px; line-height:1.5;
  font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Pretendard","Apple SD Gothic Neo","Segoe UI",system-ui,sans-serif;
  -webkit-font-smoothing:antialiased; text-rendering:optimizeLegibility;
  word-break:keep-all; overflow-wrap:anywhere}
a{color:inherit; text-decoration:none}
button{font:inherit; color:inherit; border:0; background:transparent}
:focus-visible{outline:2px solid var(--blue); outline-offset:3px; border-radius:8px}
.hidden{display:none !important}

.hl{font-family:"Noto Serif KR","Nanum Myeongjo",Georgia,serif}
.b-title,.row-title,.f-title,.bd-teaser,.brief-title{text-wrap:pretty}

/* ---------- 상단 고정 네비게이션 ---------- */
.top{position:sticky; top:0; z-index:40; background:var(--nav);
  backdrop-filter:saturate(190%) blur(24px); -webkit-backdrop-filter:saturate(190%) blur(24px);
  border-bottom:1px solid var(--hairline); transition:border-color .2s ease}
.top-in{max-width:1180px; margin:0 auto; padding:10px 28px 0; display:flex; align-items:center; gap:12px; flex-wrap:wrap}
.brand{font-family:"Noto Serif KR",Georgia,serif; font-size:17.5px; font-weight:700; letter-spacing:-.015em}
.nav-new{display:none; align-items:center; gap:6px; font-size:11.5px; font-weight:600;
  color:var(--breaking); background:var(--breaking-bg); padding:3px 10px; border-radius:980px}
.nav-new.show{display:inline-flex}
.top-right{margin-left:auto; display:flex; align-items:center; gap:11px;
  flex-wrap:wrap; row-gap:7px; justify-content:flex-end; min-width:0}
.stamp{font-size:11.5px; color:var(--ink-2); font-variant-numeric:tabular-nums; display:flex; align-items:center; gap:6px}
.dot-live{width:6.5px; height:6.5px; border-radius:50%; background:var(--live); box-shadow:0 0 0 3px var(--live-halo)}
@media (prefers-reduced-motion: no-preference){
  .dot-live{animation:pulse 2.8s ease-in-out infinite}
  @keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}}
}
.metals{display:flex; flex-direction:column; align-items:flex-end; gap:3px;
  font-variant-numeric:tabular-nums;
  padding-right:12px; margin-right:-2px; border-right:1px solid var(--hairline)}
.metal-row{display:flex; align-items:baseline; gap:12px}
.metal{display:inline-flex; align-items:baseline; gap:5px; font-size:11.5px; white-space:nowrap}
.m-label{color:var(--ink-3); font-weight:600}
.m-value{color:var(--ink); font-weight:600; letter-spacing:-.01em}
.m-chg{font-size:10.5px; font-weight:700}
.m-chg.up{color:var(--up)}
.m-chg.down{color:var(--down)}
.m-chg.flat{color:var(--ink-3)}
.btn{border:1px solid var(--hairline); background:var(--surface); font-size:11.5px; font-weight:500;
  padding:5px 12px; border-radius:980px; cursor:pointer; transition:all .18s cubic-bezier(0.16, 1, 0.3, 1)}
.btn:hover{background:var(--surface-2); transform:scale(1.02)}
.btn:active{transform:scale(0.98)}

.menu-wrap{max-width:1180px; margin:0 auto; padding:10px 28px 12px}
.menu{display:flex; gap:8px; overflow-x:auto; scrollbar-width:none; -ms-overflow-style:none}
.menu::-webkit-scrollbar{display:none}
.m-btn{flex:none; display:inline-flex; align-items:center; gap:7px; cursor:pointer;
  border:1px solid var(--hairline); background:var(--surface); color:var(--ink-2);
  font-size:14px; font-weight:500; padding:8px 16px; border-radius:980px;
  transition:all .18s cubic-bezier(0.16, 1, 0.3, 1)}
.m-btn:hover{background:var(--surface-2); color:var(--ink)}
.m-btn:active{transform:scale(0.97)}
.m-btn .swatch{width:8px; height:8px; border-radius:50%; background:var(--accent); flex:none}
.m-btn .n{font-size:11px; font-weight:700; color:var(--breaking); font-variant-numeric:tabular-nums}
.m-btn[aria-selected="true"]{background:var(--ink); color:var(--ground); border-color:var(--ink); font-weight:600}
.m-btn[aria-selected="true"] .n{color:var(--ground); opacity:.75}
.m-btn[aria-selected="true"] .swatch{box-shadow:0 0 0 2px var(--ground)}
.m-btn .pin-icon{font-size:10px; margin-left:-2px; opacity:0.8}

main{max-width:1180px; margin:0 auto; padding:0 28px 76px}

/* ---------- 제호 ---------- */
.masthead{padding:34px 0 20px; border-bottom:2px solid var(--rule); margin-bottom:2px}
.masthead-in{display:flex; align-items:flex-end; gap:16px; flex-wrap:wrap}
.wordmark{font-family:"Noto Serif KR",Georgia,serif; font-size:40px; font-weight:700;
  letter-spacing:-.025em; line-height:1.05; margin:0}
.wordmark-sub{font-size:12.5px; color:var(--ink-2); margin:9px 0 0 2px; letter-spacing:.01em}
.masthead-date{margin-left:auto; text-align:right; font-size:12px; color:var(--ink-2);
  font-variant-numeric:tabular-nums; line-height:1.6}
.masthead-date b{display:block; font-size:13.5px; font-weight:600; color:var(--ink)}
.rule-thin{height:1px; background:var(--hairline); margin-bottom:28px}

/* ---------- 섹션 라벨 ---------- */
.zone-head{display:flex; align-items:center; gap:9px; margin:0 0 13px; flex-wrap:wrap}
.zone-title{display:flex; align-items:center; gap:8px; font-size:12px; font-weight:700;
  letter-spacing:.1em; text-transform:uppercase}
.zone-title::before{content:""; width:12px; height:2px; background:var(--rule)}
.zone-note{font-size:12px; color:var(--ink-3)}
.stack{display:flex; flex-direction:column; gap:32px}

/* ---------- 카드 공통 (Apple 스타일) ---------- */
.card{background:var(--surface); border:1px solid var(--hairline); border-radius:18px;
  box-shadow:var(--shadow); overflow:hidden; backdrop-filter:blur(20px); -webkit-backdrop-filter:blur(20px);
  transition:border-color .2s ease, box-shadow .2s ease}

/* ---------- 오늘의 3줄 브리핑 카드 ---------- */
.brief-card{background:linear-gradient(135deg, var(--surface) 0%, var(--surface-2) 100%);
  border:1px solid var(--hairline); border-radius:18px; padding:20px 24px; box-shadow:var(--shadow)}
.brief-head{display:flex; align-items:center; gap:8px; margin-bottom:14px}
.brief-pill{display:inline-flex; align-items:center; gap:6px; background:var(--ink); color:var(--ground);
  font-size:11px; font-weight:600; letter-spacing:.05em; padding:4px 10px; border-radius:980px}
.brief-sub{font-size:12px; color:var(--ink-2)}
.brief-grid{display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:14px}
.brief-item{background:var(--surface); border:1px solid var(--hairline-2); border-radius:12px; padding:12px 16px;
  display:flex; flex-direction:column; gap:6px; transition:all .18s ease}
.brief-item:hover{background:var(--surface-solid); border-color:var(--hairline); transform:translateY(-2px)}
.brief-tag{display:inline-flex; align-items:center; gap:6px; font-size:11px; font-weight:600; color:var(--accent)}
.brief-tag .swatch{width:6.5px; height:6.5px; border-radius:50%; background:var(--accent)}
.brief-title{font-size:14px; font-weight:500; line-height:1.45; color:var(--ink)}

/* ---------- 속보 카드 ---------- */
.b-list{list-style:none; margin:0; padding:0}
.b-list li + li{border-top:1px solid var(--hairline-2)}
.b-item{display:flex; align-items:baseline; gap:14px; padding:14px 22px; transition:background .15s ease}
.b-item:hover{background:var(--tint)}
.b-time{flex:none; width:50px; font-size:11.5px; color:var(--ink-3); font-variant-numeric:tabular-nums}
.b-title{flex:1; min-width:0; font-size:15.5px; font-weight:500; line-height:1.5}
.b-list li:first-child .b-item{padding:22px 22px 24px; align-items:flex-start}
.b-list li:first-child .b-title{font-family:"Noto Serif KR","Nanum Myeongjo",Georgia,serif;
  font-size:22.5px; font-weight:600; line-height:1.45; letter-spacing:-.015em}
.b-list li:first-child .b-time{padding-top:7px}
.b-tag{flex:none; display:inline-flex; align-items:center; gap:6px; font-size:11px; color:var(--ink-2)}
.b-tag .swatch{width:7px; height:7px; border-radius:50%; background:var(--accent)}
.b-src{flex:none; font-size:11px; color:var(--ink-3); width:82px; text-align:right;
  overflow:hidden; text-overflow:ellipsis; white-space:nowrap}

/* ---------- 메뉴판 (주제별 보드) ---------- */
.board{list-style:none; margin:0; padding:0; background:var(--surface);
  border:1px solid var(--hairline); border-radius:18px; box-shadow:var(--shadow); overflow:hidden}
.board li + li{border-top:1px solid var(--hairline-2)}
.bd-row{display:grid; grid-template-columns:4px 135px 1fr auto 16px; align-items:center;
  gap:0 18px; padding:0; cursor:pointer; width:100%; text-align:left;
  border:0; background:transparent; transition:background .15s ease}
.bd-row:hover{background:var(--tint)}
.bd-bar{align-self:stretch; background:var(--accent)}
.bd-name{padding:15px 0; font-size:15.5px; font-weight:600; letter-spacing:-.015em; display:flex; align-items:center; gap:6px}
.bd-teaser{font-size:13.5px; color:var(--ink-2); overflow:hidden;
  text-overflow:ellipsis; white-space:nowrap; padding:16px 0}
.bd-nums{display:flex; align-items:center; gap:9px; padding:16px 0; white-space:nowrap}
.bd-new{font-size:11px; font-weight:700; color:var(--breaking);
  background:var(--breaking-bg); padding:3px 8px; border-radius:980px; font-variant-numeric:tabular-nums}
.bd-total{font-size:11.5px; color:var(--ink-3); font-variant-numeric:tabular-nums}
.bd-go{font-size:16px; color:var(--ink-3); padding-right:18px; transition:transform .15s ease, color .15s ease}
.bd-row:hover .bd-go{color:var(--ink-2); transform:translateX(4px)}

/* ---------- 전체 흐름 ---------- */
.feed{list-style:none; margin:0; padding:0}
.feed li + li{border-top:1px solid var(--hairline-2)}
.f-row{display:grid; grid-template-columns:50px 115px 1fr 88px; gap:14px;
  align-items:baseline; padding:10px 22px; transition:background .15s ease}
.f-row:hover{background:var(--tint)}
.f-time{font-size:11px; color:var(--ink-3); font-variant-numeric:tabular-nums}
.f-tag{display:inline-flex; align-items:center; gap:6px; font-size:11px; color:var(--ink-2);
  overflow:hidden; white-space:nowrap}
.f-tag .swatch{width:7px; height:7px; border-radius:50%; background:var(--accent); flex:none}
.f-title{font-size:14.5px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap}
.f-row:hover .f-title{color:var(--blue)}
.f-src{font-size:11px; color:var(--ink-3); text-align:right; overflow:hidden;
  text-overflow:ellipsis; white-space:nowrap}
.more{display:block; width:100%; padding:14px; border:0; border-top:1px solid var(--hairline);
  background:var(--surface); color:var(--blue); font-size:13px; font-weight:500;
  cursor:pointer; transition:background .15s ease}
.more:hover{background:var(--surface-2)}

/* ---------- 주제 보기 (상세 페이지) ---------- */
.detail{margin-top:30px}
.detail-head{display:flex; align-items:center; gap:16px; padding:22px 24px 18px;
  border-bottom:2px solid var(--rule); flex-wrap:wrap}
.detail-name{display:flex; align-items:center; gap:11px; font-size:28px; font-weight:700; letter-spacing:-.025em}
.detail-name .swatch{width:12px; height:12px; border-radius:50%; background:var(--accent)}
.detail-stat{font-size:12px; color:var(--ink-2)}
.detail-stat b{font-size:15.5px; font-weight:600; color:var(--ink); font-variant-numeric:tabular-nums}
.pin-toggle{margin-left:auto; display:inline-flex; align-items:center; gap:6px; font-size:12px; font-weight:500;
  padding:5px 12px; border-radius:980px; border:1px solid var(--hairline); background:var(--surface); cursor:pointer;
  transition:all .15s ease}
.pin-toggle:hover{background:var(--surface-2)}
.pin-toggle.pinned{background:var(--ink); color:var(--ground); border-color:var(--ink)}
.d-list{list-style:none; margin:0; padding:0; display:grid;
  grid-template-columns:repeat(auto-fill,minmax(330px,1fr))}
.group{grid-column:1/-1; padding:16px 24px 6px; font-size:11px; font-weight:700;
  letter-spacing:.09em; text-transform:uppercase; color:var(--ink-3); border-top:1px solid var(--hairline-2)}
.group:first-child{border-top:0; padding-top:14px}
.d-item{border-top:1px solid var(--hairline-2)}
.row{display:block; padding:14px 24px; height:100%; transition:background .15s ease}
.row:hover{background:var(--tint)}
.row-title{font-size:15.5px; font-weight:500; line-height:1.55;
  display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden}
.row:hover .row-title{color:var(--blue)}
.row-meta{margin-top:6px; font-size:11px; color:var(--ink-3); display:flex; gap:6px;
  align-items:center; font-variant-numeric:tabular-nums}
.sep{opacity:.45}
.badge{color:var(--breaking); font-weight:700; font-size:10px; letter-spacing:.05em}

footer{border-top:1px solid var(--hairline); margin-top:40px; padding-top:20px;
  font-size:11.5px; color:var(--ink-3); display:flex; gap:8px; flex-wrap:wrap; align-items:center}

@media (max-width:760px){
  .bd-row{grid-template-columns:4px 1fr auto 16px; gap:0 13px}
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
  .menu-wrap{padding:8px 18px 10px}
  .top-right{flex:1 1 100%; margin-left:0; justify-content:flex-start}
  .stamp-sfx{display:none}
  .metals{order:3; flex-basis:100%; align-items:flex-start;
    border-right:0; padding-right:0; margin-right:0; gap:4px}
  .metal-row{gap:12px}
  .stamp{font-size:11px}
  .btn{padding:5px 10px}
  .masthead{padding:24px 0 16px}
  .wordmark{font-size:32px}
  .wordmark-sub{font-size:11.5px}
  .masthead-date{margin-left:0; text-align:left}
  .stack{gap:26px}
  .b-list li:first-child .b-title{font-size:19.5px}
  .b-src{display:none}
  .detail-name{font-size:24px}
}
</style>
</head>
<body>

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
    <div class="menu" id="tabmenu" role="tablist" aria-label="주제 메뉴">
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
        <p class="wordmark-sub">$SUBTITLE</p>
      </div>
      <div class="masthead-date">
        <b>$DATE_LONG</b>
        구글 뉴스에서 모은 $TOTAL건
      </div>
    </div>
  </header>
  <div class="rule-thin"></div>

  <div id="overview" class="stack">
    <!-- 오늘의 판세 3줄 브리핑 -->
    <section class="brief-card" aria-label="오늘의 판세 브리핑">
      <div class="brief-head">
        <span class="brief-pill">✨ 오늘의 3줄 판세</span>
        <span class="brief-sub">현재 가장 주목받는 핵심 헤드라인</span>
      </div>
      <div class="brief-grid">
$BRIEFING
      </div>
    </section>

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
        <span class="zone-note">$TOPIC_COUNT를 시간순으로</span>
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

  /* 지난번에 본 이후 들어온 기사 카운트 */
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

  /* 다음 갱신 카운트다운 & 스마트 리로드 */
  var cd = document.getElementById("countdown");
  var reloading = false;
  function doReload(){
    if (reloading) return;
    reloading = true;
    var url = new URL(window.location.href);
    url.searchParams.set("t", String(Date.now()));
    window.location.replace(url.toString());
  }
  function tick(){
    var left = DEADLINE - Date.now();
    if (left <= 0){
      cd.textContent = "새 소식 확인 중...";
      if (!window._reloadScheduled) {
        window._reloadScheduled = true;
        setTimeout(doReload, 3000);
        setTimeout(function(){ window._reloadScheduled = false; }, 60000);
      }
      return;
    }
    var m = Math.floor(left / 60000), s = Math.floor(left % 60000 / 1000);
    cd.textContent = m + "분 " + (s < 10 ? "0" : "") + s + "초";
  }
  tick(); setInterval(tick, 1000);
  document.getElementById("refresh").addEventListener("click", function(){ doReload(); });

  /* 전체 흐름 더보기 */
  var LIMIT = 18, expanded = false;
  var feedRows = [].slice.call(document.querySelectorAll(".f-item"));
  var more = document.getElementById("more");
  function paintFeed(){
    feedRows.forEach(function(r, i){ r.classList.toggle("hidden", !expanded && i >= LIMIT); });
    more.classList.toggle("hidden", expanded || feedRows.length <= LIMIT);
  }
  more.addEventListener("click", function(){ expanded = true; paintFeed(); });
  paintFeed();

  /* 핀(Pin) 즐겨찾기 상태 관리 */
  var PINS_KEY = "panse-pins";
  function getPins(){
    try { return JSON.parse(localStorage.getItem(PINS_KEY)) || []; } catch(e){ return []; }
  }
  function togglePin(topicId){
    var pins = getPins();
    var idx = pins.indexOf(topicId);
    if (idx >= 0) pins.splice(idx, 1);
    else pins.push(topicId);
    try { localStorage.setItem(PINS_KEY, JSON.stringify(pins)); } catch(e){}
    applyPins();
  }
  function applyPins(){
    var pins = getPins();
    document.querySelectorAll(".pin-toggle").forEach(function(btn){
      var t = btn.dataset.topic;
      var isPinned = pins.indexOf(t) >= 0;
      btn.classList.toggle("pinned", isPinned);
      btn.textContent = isPinned ? "★ 핀 해제" : "☆ 핀 고정";
    });
  }
  document.querySelectorAll(".pin-toggle").forEach(function(btn){
    btn.addEventListener("click", function(){ togglePin(btn.dataset.topic); });
  });
  applyPins();

  /* 화면 뷰 전환 */
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
</body>
</html>
""")


def esc(s):
    return html.escape(str(s), quote=True)


TICKER = (
    (
        ("gold",   "금",     "$", 0, "금 현물 · 미국 달러/트로이온스"),
        ("silver", "은",     "$", 2, "은 현물 · 미국 달러/트로이온스"),
    ),
    (
        ("usdkrw", "달러",   "₩", 1, "원/달러 · 하나은행 매매기준율"),
        ("jpykrw", "엔100",  "₩", 1, "원/100엔 · 하나은행 매매기준율"),
    ),
)


def market_html(m):
    if not m:
        return ""
    lines = []
    for group in TICKER:
        cells = []
        for key, label, prefix, digits, tip in group:
            val = m.get(key)
            if val is None:
                continue
            fx_t = m.get("fx_time")
            tip_str = f"{tip} ({fx_t} 고시)" if key.endswith("krw") and fx_t else tip
            chg = m.get(f"{key}_chg")
            if chg is None:
                tag = ""
            elif chg > 0:
                tag = f'<span class="m-chg up">▲{chg:.2f}%</span>'
            elif chg < 0:
                tag = f'<span class="m-chg down">▼{abs(chg):.2f}%</span>'
            else:
                tag = '<span class="m-chg flat">0.00%</span>'
            cells.append(
                f'<span class="metal" title="{tip_str}"><span class="m-label">{label}</span><span class="m-value">{prefix}{val:,.{digits}f}</span>{tag}</span>'
            )
        if cells:
            lines.append("        <span class=\"metal-row\">" + "".join(cells) + "</span>")
    rows = lines
    if not rows:
        return ""
    stale = ' title="시세를 새로 받지 못해 직전 값입니다"' if m.get("stale") else ""
    return f'      <span class="metals"{stale}>\n' + "\n".join(rows) + '\n      </span>'


WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]


def date_long(now):
    return f"{now.year}년 {now.month}월 {now.day}일 {WEEKDAYS[now.weekday()]}요일"


def build():
    data = json.loads((HERE / "news.json").read_text(encoding="utf-8"))
    now = datetime.now(KST)
    topics = data["topics"]

    light = "\n".join(f"  --c-{t['id']}:{t['accent']};" for t in topics)
    dark = "\n".join(f"    --c-{t['id']}:{t['accent_dark']};" for t in topics)
    classes = "\n".join(f".t-{t['id']}{{{{--accent:var(--c-{t['id']})}}}}" for t in topics)

    flat = sorted(((it, t) for t in topics for it in t["items"]), key=lambda p: -p[0]["ts"])
    fresh = [p for p in flat if now.timestamp() - p[0]["ts"] <= 90 * 60][:5]
    label, note, picks = ("속보", "최근 90분 안에 들어온 기사", fresh) if fresh \
        else ("최신", "가장 최근에 들어온 기사", flat[:5])
    used = {it["link"] for it, _ in picks}

    breaking = "\n".join(
        f'        <li><a class="b-item t-{t["id"]}" href="{esc(it["link"])}" target="_blank" rel="noopener">'
        f'<span class="b-time" data-ts="{it["ts"]}">–</span><span class="b-title">{esc(it["title"])}</span>'
        f'<span class="b-tag"><span class="swatch"></span>{esc(t["name"])}</span>'
        f'<span class="b-src">{esc(it["source"])}</span></a></li>'
        for it, t in picks
    )

    # 오늘의 3줄 브리핑 (서로 다른 주요 카테고리에서 1개씩 추출)
    brief_picks = []
    seen_brief_topics = set()
    for it, t in flat:
        if t["id"] not in seen_brief_topics and it["link"] not in used:
            brief_picks.append((it, t))
            seen_brief_topics.add(t["id"])
            if len(brief_picks) >= 3:
                break
    briefing = "\n".join(
        f'        <a class="brief-item t-{t["id"]}" href="{esc(it["link"])}" target="_blank" rel="noopener">'
        f'<span class="brief-tag"><span class="swatch"></span>{esc(t["name"])}</span>'
        f'<span class="brief-title">{esc(it["title"])}</span>'
        f'</a>'
        for it, t in brief_picks
    )

    menu, board, details = [], [], []
    for t in topics:
        n = t["fresh_1h"]
        badge = f'<span class="n">+{n}</span>' if n else ""
        menu.append(
            f'      <button class="m-btn t-{t["id"]}" type="button" role="tab" data-view="{t["id"]}" aria-selected="false">'
            f'<span class="swatch"></span>{esc(t["name"])}{badge}</button>'
        )
        teaser_item = next((it for it in t["items"] if it["link"] not in used), None)
        if teaser_item:
            used.add(teaser_item["link"])
        teaser = esc(teaser_item["title"]) if teaser_item else "새 기사 없음"
        new_tag = f'<span class="bd-new">+{n}</span>' if n else ""
        board.append(
            f'        <li><button class="bd-row t-{t["id"]}" type="button" data-topic="{t["id"]}">\n'
            f'          <span class="bd-bar"></span>\n'
            f'          <span class="bd-name">{esc(t["name"])}</span>\n'
            f'          <span class="bd-teaser">{teaser}</span>\n'
            f'          <span class="bd-nums">{new_tag}<span class="bd-total">{t["total"]}건</span></span>\n'
            f'          <span class="bd-go" aria-hidden="true">›</span>\n'
            f'        </button></li>'
        )

    rest = [(it, t) for it, t in flat if it["link"] not in used]
    feed = "\n".join(
        f'          <li class="f-item" data-topic="{t["id"]}">'
        f'<a class="f-row t-{t["id"]}" href="{esc(it["link"])}" target="_blank" rel="noopener">'
        f'<span class="f-time" data-ts="{it["ts"]}">–</span>'
        f'<span class="f-tag"><span class="swatch"></span>{esc(t["name"])}</span>'
        f'<span class="f-title">{esc(it["title"])}</span>'
        f'<span class="f-src">{esc(it["source"])}</span></a></li>'
        for it, t in rest
    )

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
            badge_html = '<span class="badge">NEW</span><span class="sep">·</span>' if is_new else ""
            rows.append(
                f'        <li class="d-item"><a class="row" href="{esc(it["link"])}" target="_blank" rel="noopener">'
                f'<div class="row-title">{esc(it["title"])}</div>'
                f'<div class="row-meta">{badge_html}<span>{esc(it["source"])}</span>'
                f'<span class="sep">·</span><span data-ts="{it["ts"]}">–</span></div></a></li>'
            )
        details.append(
            f'  <section class="detail card t-{t["id"]}" data-topic="{t["id"]}" aria-label="{esc(t["name"])}">\n'
            f'    <div class="detail-head">\n'
            f'      <span class="detail-name hl"><span class="swatch"></span>{esc(t["name"])}</span>\n'
            f'      <span class="detail-stat"><b>{t["fresh_1h"]}</b>건 최근 1시간</span>\n'
            f'      <span class="detail-stat"><b>{t["total"]}</b>건 오늘 수집</span>\n'
            f'      <button class="pin-toggle" data-topic="{t["id"]}" type="button">☆ 핀 고정</button>\n'
            f'    </div>\n'
            f'    <ul class="d-list">\n' + "\n".join(rows) + '\n    </ul>\n'
            f'  </section>'
        )

    subtitle = " · ".join(t["name"] for t in topics)
    topic_count = f"{len(topics)}개 갈래"

    out = PAGE.substitute(
        SWATCH_LIGHT=light, SWATCH_DARK=dark, TOPIC_CLASSES=classes,
        UPDATED_HM=now.strftime("%H:%M"), DATE_LONG=date_long(now),
        METALS=market_html(data.get("market")),
        SUBTITLE=subtitle,
        TOPIC_COUNT=topic_count,
        BRIEFING=briefing,
        MENU="\n".join(menu), BOARD="\n".join(board), BREAKING=breaking,
        BREAKING_LABEL=label, BREAKING_NOTE=note, FEED=feed, TOTAL=len(flat), REST=len(rest),
        DETAILS="\n".join(details),
        NAMES=json.dumps({t["id"]: t["name"] for t in topics}, ensure_ascii=False),
        GEN_TS=int(now.timestamp()),
    )
    path = HERE / "dashboard.html"
    path.write_text(out, encoding="utf-8")
    print(f"렌더 완료: 브리핑 {len(brief_picks)} · 속보 {len(picks)} · 메뉴판 {len(topics)} · 전체흐름 {len(rest)} · 총 {len(flat)} (중복 0)")
    return path


if __name__ == "__main__":
    build()
