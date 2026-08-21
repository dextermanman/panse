#!/usr/bin/env python3
"""news.json -> dashboard.html (세상돌아가는 판세 - Apple 스타일 모바일/데스크톱 완벽 반응형 대시보드)."""
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
<title>세상돌아가는 판세</title>
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover, maximum-scale=5">
<meta name="description" content="주요 9대 산업·경제 뉴스와 금·은·비트코인 시세, 환율을 30분마다 모으는 대시보드">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="세상돌아가는 판세">
<meta name="theme-color" content="#FAF9F6" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0B0B0E" media="(prefers-color-scheme: dark)">
<link rel="manifest" href="/manifest.json">
<link rel="apple-touch-icon" href="/icon.svg">
<link rel="icon" type="image/svg+xml" href="/icon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@500;600;700&display=swap">
<script>
(function(){
  try {
    var saved = localStorage.getItem("panse-theme");
    if (saved) document.documentElement.setAttribute("data-theme", saved);
  } catch(e){}
})();
</script>
<style>
:root, :root[data-theme="light"]{
  /* Financial Luxury & Warm Paper (라이트) */
  --ground:#F8F6F0; --surface:rgba(255,255,255,0.95); --surface-solid:#FFFFFF; --surface-2:#EFECE3; --tint:rgba(15,23,42,0.035);
  --hairline:rgba(15,23,42,0.09); --hairline-2:rgba(15,23,42,0.045); --rule:#0F172A;
  --ink:#0F172A; --ink-2:#475569; --ink-3:#94A3B8;
  --blue:#0284C7; --gold:#D97706; --breaking:#E11D48; --breaking-bg:rgba(225,29,72,0.08);
  --shadow:0 4px 20px rgba(15,23,42,0.04), 0 1px 3px rgba(15,23,42,0.02);
  --shadow-hover:0 12px 32px -4px rgba(15,23,42,0.08), 0 2px 6px rgba(15,23,42,0.04);
  --inner-glow:inset 0 1px 1px rgba(255,255,255,0.9);
  --nav:rgba(248,246,240,0.94); --live:#10B981; --live-halo:rgba(16,185,129,0.18);
  --up:#DC2626; --down:#2563EB;
$SWATCH_LIGHT
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    /* Deep Midnight & Sapphire Luxury (다크) */
    --ground:#080D1A; --surface:rgba(15,23,42,0.92); --surface-solid:#0F172A; --surface-2:#1E293B; --tint:rgba(255,255,255,0.04);
    --hairline:rgba(148,163,184,0.15); --hairline-2:rgba(148,163,184,0.08); --rule:#F8FAFC;
    --ink:#F8FAFC; --ink-2:#94A3B8; --ink-3:#64748B;
    --blue:#38BDF8; --gold:#F59E0B; --breaking:#FB7185; --breaking-bg:rgba(251,113,133,0.14);
    --shadow:0 8px 32px rgba(0,0,0,0.6), 0 1px 4px rgba(0,0,0,0.4);
    --shadow-hover:0 16px 44px -8px rgba(0,0,0,0.8), 0 0 24px rgba(56,189,248,0.12);
    --inner-glow:inset 0 1px 1px rgba(255,255,255,0.08);
    --nav:rgba(8,13,26,0.92); --live:#34D399; --live-halo:rgba(52,211,153,0.2);
    --up:#F87171; --down:#60A5FA;
$SWATCH_DARK
  }
}
:root[data-theme="dark"]{
  --ground:#080D1A; --surface:rgba(15,23,42,0.92); --surface-solid:#0F172A; --surface-2:#1E293B; --tint:rgba(255,255,255,0.04);
  --hairline:rgba(148,163,184,0.15); --hairline-2:rgba(148,163,184,0.08); --rule:#F8FAFC;
  --ink:#F8FAFC; --ink-2:#94A3B8; --ink-3:#64748B;
  --blue:#38BDF8; --gold:#F59E0B; --breaking:#FB7185; --breaking-bg:rgba(251,113,133,0.14);
  --shadow:0 8px 32px rgba(0,0,0,0.6), 0 1px 4px rgba(0,0,0,0.4);
  --shadow-hover:0 16px 44px -8px rgba(0,0,0,0.8), 0 0 24px rgba(56,189,248,0.12);
  --inner-glow:inset 0 1px 1px rgba(255,255,255,0.08);
  --nav:rgba(8,13,26,0.92); --live:#34D399; --live-halo:rgba(52,211,153,0.2);
  --up:#F87171; --down:#60A5FA;
$SWATCH_DARK
}
:root[data-theme="light"]{
  --ground:#F8F6F0; --surface:rgba(255,255,255,0.95); --surface-solid:#FFFFFF; --surface-2:#EFECE3; --tint:rgba(15,23,42,0.035);
  --hairline:rgba(15,23,42,0.09); --hairline-2:rgba(15,23,42,0.045); --rule:#0F172A;
  --ink:#0F172A; --ink-2:#475569; --ink-3:#94A3B8;
  --blue:#0284C7; --gold:#D97706; --breaking:#E11D48; --breaking-bg:rgba(225,29,72,0.08);
  --shadow:0 4px 20px rgba(15,23,42,0.04), 0 1px 3px rgba(15,23,42,0.02);
  --shadow-hover:0 12px 32px -4px rgba(15,23,42,0.08), 0 2px 6px rgba(15,23,42,0.04);
  --inner-glow:inset 0 1px 1px rgba(255,255,255,0.9);
  --nav:rgba(248,246,240,0.94); --live:#10B981; --live-halo:rgba(16,185,129,0.18);
  --up:#DC2626; --down:#2563EB;
$SWATCH_LIGHT
}
$TOPIC_CLASSES

*{box-sizing:border-box; -webkit-tap-highlight-color:transparent}
body{margin:0; background:var(--ground); color:var(--ink); font-size:15px; line-height:1.55;
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
.top-in{max-width:1180px; margin:0 auto; padding:10px 24px 0; display:flex; align-items:center; gap:12px; flex-wrap:wrap}
.brand{font-family:"Noto Serif KR",Georgia,serif; font-size:18px; font-weight:700; letter-spacing:-.015em; white-space:nowrap}
.nav-new{display:none; align-items:center; gap:6px; font-size:11.5px; font-weight:600;
  color:var(--breaking); background:var(--breaking-bg); padding:3px 10px; border-radius:980px}
.nav-new.show{display:inline-flex}
.top-right{margin-left:auto; display:flex; align-items:center; gap:8px;
  flex-wrap:wrap; justify-content:flex-end; min-width:0}
.stamp{font-size:11.5px; color:var(--ink-2); font-variant-numeric:tabular-nums; display:flex; align-items:center; gap:6px; white-space:nowrap}
.dot-live{width:6.5px; height:6.5px; border-radius:50%; background:var(--live); box-shadow:0 0 0 3px var(--live-halo); flex:none}
@media (prefers-reduced-motion: no-preference){
  .dot-live{animation:pulse 2.8s ease-in-out infinite}
  @keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}}
}

/* 금융 시세 바 */
.metals{display:flex; align-items:center; gap:6px; font-variant-numeric:tabular-nums;
  padding-right:10px; margin-right:2px; border-right:1px solid var(--hairline); flex-wrap:wrap}
.metal-row{display:flex; align-items:center; gap:6px}
.metal{display:inline-flex; align-items:center; gap:5px; font-size:11.5px; white-space:nowrap;
  background:var(--surface-2); border:1px solid var(--hairline); padding:3px 9px; border-radius:980px}
.m-label{color:var(--ink-3); font-weight:600}
.m-value{color:var(--ink); font-weight:600; letter-spacing:-.01em}
.m-chg{font-size:10.5px; font-weight:700}
.m-chg.up{color:var(--up)}
.m-chg.down{color:var(--down)}
.m-chg.flat{color:var(--ink-3)}

.btn{border:1px solid var(--hairline); background:var(--surface); font-size:11.5px; font-weight:500;
  padding:5px 11px; border-radius:980px; cursor:pointer; transition:all .18s cubic-bezier(0.16, 1, 0.3, 1); white-space:nowrap}
.btn:hover{background:var(--surface-2); transform:scale(1.02)}
.btn:active{transform:scale(0.96)}

.menu-wrap{max-width:1180px; margin:0 auto; padding:8px 24px 10px; display:flex; align-items:center; gap:10px}
.menu{display:flex; gap:7px; overflow-x:auto; scrollbar-width:none; -ms-overflow-style:none; flex:1; -webkit-overflow-scrolling:touch}
.menu::-webkit-scrollbar{display:none}
.m-btn{flex:none; display:inline-flex; align-items:center; gap:6px; cursor:pointer;
  border:1px solid var(--hairline); background:var(--surface); color:var(--ink-2);
  font-size:13.5px; font-weight:500; padding:6px 14px; border-radius:980px;
  transition:all .18s cubic-bezier(0.16, 1, 0.3, 1); white-space:nowrap}
.m-btn:hover{background:var(--surface-2); color:var(--ink)}
.m-btn:active{transform:scale(0.96)}
.m-btn .swatch{width:7.5px; height:7.5px; border-radius:50%; background:var(--accent); flex:none}
.m-btn .n{font-size:11px; font-weight:700; color:var(--breaking); font-variant-numeric:tabular-nums}
.m-btn[aria-selected="true"]{background:var(--ink); color:var(--ground); border-color:var(--ink); font-weight:600}
.m-btn[aria-selected="true"] .n{color:var(--ground); opacity:.8}
.m-btn[aria-selected="true"] .swatch{box-shadow:0 0 0 2px var(--ground)}

main{max-width:1180px; margin:0 auto; padding:0 24px calc(76px + env(safe-area-inset-bottom))}

/* ---------- 제호 & 검색바 ---------- */
.masthead{padding:30px 0 16px; border-bottom:2px solid var(--rule); margin-bottom:2px}
.masthead-in{display:flex; align-items:flex-end; gap:16px; flex-wrap:wrap}
.wordmark{font-family:"Noto Serif KR",Georgia,serif; font-size:38px; font-weight:700;
  letter-spacing:-.025em; line-height:1.05; margin:0}
.wordmark-sub{font-size:12.5px; color:var(--ink-2); margin:8px 0 0 2px; letter-spacing:.01em}
.masthead-date{margin-left:auto; text-align:right; font-size:12px; color:var(--ink-2);
  font-variant-numeric:tabular-nums; line-height:1.6}
.masthead-date b{display:block; font-size:13.5px; font-weight:600; color:var(--ink)}
.rule-thin{height:1px; background:var(--hairline); margin-bottom:22px}

/* 검색창 */
.search-bar{margin-bottom:22px; position:relative; display:flex; align-items:center}
.search-in{width:100%; display:flex; align-items:center; background:var(--surface);
  border:1px solid var(--hairline); border-radius:14px; padding:10px 16px; gap:10px;
  box-shadow:var(--shadow); transition:all .18s ease}
.search-in:focus-within{border-color:var(--blue); box-shadow:0 0 0 3px rgba(0,113,227,0.15)}
.search-icon{width:16px; height:16px; color:var(--ink-3); flex:none}
.search-input{flex:1; border:0; background:transparent; font-size:14.5px; color:var(--ink); outline:none}
.search-input::placeholder{color:var(--ink-3)}
.search-clear{color:var(--ink-3); font-size:14px; cursor:pointer; padding:3px 7px; border-radius:50%}
.search-clear:hover{color:var(--ink); background:var(--surface-2)}

/* ---------- 섹션 라벨 ---------- */
.zone-head{display:flex; align-items:center; gap:9px; margin:0 0 12px; flex-wrap:wrap}
.zone-title{display:flex; align-items:center; gap:8px; font-size:12px; font-weight:700;
  letter-spacing:.08em; text-transform:uppercase}
.zone-title::before{content:""; width:12px; height:2px; background:var(--rule)}
.zone-note{font-size:12px; color:var(--ink-3)}
.stack{display:flex; flex-direction:column; gap:28px}

/* ---------- 카드 공통 (Financial Luxury 스타일) ---------- */
.card{background:var(--surface); border:1px solid var(--hairline); border-radius:20px;
  box-shadow:var(--shadow), var(--inner-glow); overflow:hidden; backdrop-filter:blur(24px); -webkit-backdrop-filter:blur(24px);
  transition:all .2s cubic-bezier(0.16, 1, 0.3, 1)}
.card-head{display:flex; align-items:center; gap:10px; padding:14px 22px; border-bottom:1px solid var(--hairline)}
.eyebrow{font-size:11px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; color:var(--ink-3)}

/* ---------- 오늘의 3줄 브리핑 카드 ---------- */
.brief-card{background:linear-gradient(135deg, var(--surface) 0%, var(--surface-2) 100%);
  border:1px solid var(--hairline); border-radius:20px; padding:20px 24px; box-shadow:var(--shadow), var(--inner-glow)}
.brief-head{display:flex; align-items:center; gap:10px; margin-bottom:14px; flex-wrap:wrap}
.brief-pill{display:inline-flex; align-items:center; gap:6px; background:linear-gradient(135deg, #B45309, #D97706); color:#FFFFFF;
  font-size:11px; font-weight:700; letter-spacing:.05em; padding:4px 11px; border-radius:980px; box-shadow:0 2px 8px rgba(180,83,9,0.25)}
.brief-sub{font-size:12px; color:var(--ink-2)}
.brief-copy{margin-left:auto; display:inline-flex; align-items:center; gap:5px; font-size:11.5px;
  font-weight:600; color:var(--ink-2); background:var(--surface); border:1px solid var(--hairline);
  padding:4px 11px; border-radius:980px; cursor:pointer; transition:all .15s ease}
.brief-copy:hover{background:var(--surface-solid); color:var(--ink); transform:scale(1.02)}
.brief-grid{display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:12px}
.brief-item{background:var(--surface); border:1px solid var(--hairline-2); border-radius:14px; padding:14px 18px;
  box-shadow:var(--inner-glow); display:flex; flex-direction:column; gap:8px; transition:all .18s cubic-bezier(0.16, 1, 0.3, 1)}
.brief-item:hover{background:var(--surface-solid); border-color:var(--hairline); transform:translateY(-2px); box-shadow:var(--shadow-hover)}
.brief-tag{display:inline-flex; align-items:center; gap:6px; font-size:11.5px; font-weight:700; color:var(--accent)}
.brief-tag .swatch{width:7px; height:7px; border-radius:50%; background:var(--accent)}
.brief-title{font-size:14.5px; font-weight:600; line-height:1.45; color:var(--ink)}

/* ---------- 속보 카드 ---------- */
.b-list{list-style:none; margin:0; padding:0}
.b-list li + li{border-top:1px solid var(--hairline-2)}
.b-item{display:flex; align-items:center; gap:14px; padding:13px 22px; transition:background .15s ease}
.b-item:hover{background:var(--tint)}
.b-title{flex:1; min-width:0; font-size:15.5px; font-weight:550; line-height:1.5; overflow:hidden; text-overflow:ellipsis; white-space:nowrap}
.b-list li:first-child .b-item{padding:20px 22px 22px; align-items:flex-start}
.b-list li:first-child .b-title{font-family:"Noto Serif KR","Nanum Myeongjo",Georgia,serif;
  font-size:21px; font-weight:600; line-height:1.45; letter-spacing:-.015em; white-space:normal}
.b-tag-wrap{flex:none; display:flex; align-items:center; gap:8px; font-size:11.5px; color:var(--ink-3)}
.b-tag{display:inline-flex; align-items:center; gap:6px; font-size:11px; font-weight:600;
  color:var(--ink-2); background:var(--surface-2); padding:3px 8px; border-radius:6px}
.b-tag .swatch{width:6.5px; height:6.5px; border-radius:50%; background:var(--accent)}
.b-src{font-size:11.5px; color:var(--ink-3); max-width:90px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap}
.b-time{font-size:11.5px; color:var(--ink-3); font-variant-numeric:tabular-nums; white-space:nowrap}
.b-item .bm-btn{flex:none; opacity:0.4; font-size:15px; cursor:pointer; padding:6px 8px; border-radius:8px; transition:all .15s ease}
.b-item .bm-btn:hover{opacity:1; background:var(--surface-2)}
.b-item .bm-btn.active{opacity:1; color:#FF9500}

/* ---------- 메뉴판 (주제별 보드 & 스파크라인) ---------- */
.board{list-style:none; margin:0; padding:0; background:var(--surface);
  border:1px solid var(--hairline); border-radius:18px; box-shadow:var(--shadow); overflow:hidden}
.board li + li{border-top:1px solid var(--hairline-2)}
.bd-row{display:grid; grid-template-columns:4px 135px 1fr auto 60px 16px; align-items:center;
  gap:0 16px; padding:0; cursor:pointer; width:100%; text-align:left;
  border:0; background:transparent; transition:background .15s ease}
.bd-row:hover{background:var(--tint)}
.bd-bar{align-self:stretch; background:var(--accent)}
.bd-name{padding:15px 0; font-size:15.5px; font-weight:600; letter-spacing:-.015em; display:flex; align-items:center; gap:6px}
.bd-teaser{font-size:13.5px; color:var(--ink-2); overflow:hidden;
  text-overflow:ellipsis; white-space:nowrap; padding:16px 0}
.bd-nums{display:flex; align-items:center; gap:8px; padding:16px 0; white-space:nowrap}
.bd-new{font-size:11px; font-weight:700; color:var(--breaking);
  background:var(--breaking-bg); padding:3px 8px; border-radius:980px; font-variant-numeric:tabular-nums}
.bd-total{font-size:11.5px; color:var(--ink-3); font-variant-numeric:tabular-nums}
.sparkline{display:flex; align-items:flex-end; gap:1.5px; height:20px; padding:2px 0}
.sp-bar{width:2px; background:var(--accent); border-radius:1px; opacity:0.75; min-height:2px}
.bd-go{font-size:16px; color:var(--ink-3); padding-right:18px; transition:transform .15s ease, color .15s ease}
.bd-row:hover .bd-go{color:var(--ink-2); transform:translateX(4px)}

/* ---------- 전체 흐름 ---------- */
.feed{list-style:none; margin:0; padding:0}
.feed li + li{border-top:1px solid var(--hairline-2)}
.f-row{display:flex; align-items:center; gap:14px; padding:13px 22px; transition:background .15s ease}
.f-row:hover{background:var(--tint)}
.f-title{flex:1; min-width:0; font-size:15px; font-weight:550; overflow:hidden; text-overflow:ellipsis; white-space:nowrap}
.f-row:hover .f-title{color:var(--blue)}
.f-meta-wrap{flex:none; display:flex; align-items:center; gap:8px; font-size:11.5px; color:var(--ink-3)}
.f-tag{display:inline-flex; align-items:center; gap:6px; font-size:11px; font-weight:600;
  color:var(--ink-2); background:var(--surface-2); padding:2px 8px; border-radius:6px; width:fit-content}
.f-tag .swatch{width:6.5px; height:6.5px; border-radius:50%; background:var(--accent); flex:none}
.f-src{font-size:11.5px; color:var(--ink-3); max-width:90px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap}
.f-time{font-size:11.5px; color:var(--ink-3); font-variant-numeric:tabular-nums; white-space:nowrap}
.f-row .bm-btn{flex:none; opacity:0.4; font-size:15px; cursor:pointer; padding:6px 8px; border-radius:8px; transition:all .15s ease}
.f-row .bm-btn:hover{opacity:1; background:var(--surface-2)}
.f-row .bm-btn.active{opacity:1; color:#FF9500}
.more{display:block; width:100%; padding:15px; border:0; border-top:1px solid var(--hairline);
  background:var(--surface); color:var(--blue); font-size:13.5px; font-weight:500;
  cursor:pointer; transition:background .15s ease}
.more:hover{background:var(--surface-2)}

/* ---------- 주제 보기 & 스크랩 상세 ---------- */
.detail{margin-top:28px}
.detail-head{display:flex; align-items:center; gap:14px; padding:20px 22px 16px;
  border-bottom:2px solid var(--rule); flex-wrap:wrap}
.detail-name{display:flex; align-items:center; gap:11px; font-size:26px; font-weight:700; letter-spacing:-.025em}
.detail-name .swatch{width:11px; height:11px; border-radius:50%; background:var(--accent)}
.detail-stat{font-size:12px; color:var(--ink-2)}
.detail-stat b{font-size:15px; font-weight:600; color:var(--ink); font-variant-numeric:tabular-nums}
.pin-toggle{margin-left:auto; display:inline-flex; align-items:center; gap:6px; font-size:12px; font-weight:500;
  padding:5px 12px; border-radius:980px; border:1px solid var(--hairline); background:var(--surface); cursor:pointer;
  transition:all .15s ease}
.pin-toggle:hover{background:var(--surface-2)}
.pin-toggle.pinned{background:var(--ink); color:var(--ground); border-color:var(--ink)}
.d-list{list-style:none; margin:0; padding:0; display:grid;
  grid-template-columns:repeat(auto-fill,minmax(320px,1fr))}
.group{grid-column:1/-1; padding:15px 22px 6px; font-size:11px; font-weight:700;
  letter-spacing:.09em; text-transform:uppercase; color:var(--ink-3); border-top:1px solid var(--hairline-2)}
.group:first-child{border-top:0; padding-top:12px}
.d-item{border-top:1px solid var(--hairline-2); position:relative}
.row{display:block; padding:14px 22px; height:100%; transition:background .15s ease}
.row:hover{background:var(--tint)}
.row-title{font-size:15.5px; font-weight:550; line-height:1.55;
  display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden}
.row:hover .row-title{color:var(--blue)}
.row-meta{margin-top:8px; font-size:11.5px; color:var(--ink-3); display:flex; gap:6px;
  align-items:center; font-variant-numeric:tabular-nums; flex-wrap:wrap}
.meta-chip{display:inline-flex; align-items:center; gap:4px; background:var(--surface-2);
  padding:2px 7px; border-radius:6px; font-size:11px; font-weight:500; color:var(--ink-2)}
.sep{opacity:.45}
.badge{color:var(--breaking); font-weight:700; font-size:10.5px; letter-spacing:.05em}

/* 토스트 알림 */
.toast{position:fixed; bottom:24px; left:50%; transform:translateX(-50%) translateY(100px);
  background:var(--ink); color:var(--ground); font-size:13px; font-weight:600;
  padding:10px 20px; border-radius:980px; box-shadow:0 10px 30px rgba(0,0,0,0.35);
  z-index:100; transition:transform .25s cubic-bezier(0.16, 1, 0.3, 1); pointer-events:none}
.toast.show{transform:translateX(-50%) translateY(0)}

footer{border-top:1px solid var(--hairline); margin-top:36px; padding-top:18px;
  font-size:11.5px; color:var(--ink-3); display:flex; gap:8px; flex-wrap:wrap; align-items:center}

/* ========================================================
   📱 스마트폰 (모바일 화면) 최적화 스타일 (iOS / Android)
   ======================================================== */
@media (max-width:768px){
  /* 상단 헤더 슬림화 & 시세 가로 스와이프 */
  .top-in{padding:8px 14px 4px; gap:8px}
  .brand{font-size:16.5px}
  .top-right{gap:6px}
  .stamp-sfx{display:none}
  .stamp{font-size:11px}
  
  /* 시세 바: 2단 가로 스크롤바로 전환 */
  .metals{order:3; flex-basis:100%; border-right:0; padding:4px 0 6px; margin:0;
    overflow-x:auto; scrollbar-width:none; -ms-overflow-style:none; flex-wrap:nowrap; -webkit-overflow-scrolling:touch}
  .metals::-webkit-scrollbar{display:none}
  .metal-row{gap:5px; flex:none}
  .metal{font-size:11px; padding:3px 8px}

  /* 메뉴 탭바 */
  .menu-wrap{padding:6px 14px 8px}
  .m-btn{font-size:13px; padding:6px 12px}

  main{padding:0 14px calc(60px + env(safe-area-inset-bottom))}

  /* 제호 */
  .masthead{padding:20px 0 14px}
  .wordmark{font-size:30px}
  .wordmark-sub{font-size:11.5px; margin-top:5px}
  .masthead-date{margin-left:0; text-align:left; font-size:11.5px; margin-top:8px}

  /* 검색바 */
  .search-in{padding:8px 12px; border-radius:12px}
  .search-input{font-size:13.5px}

  /* 브리핑 */
  .brief-card{padding:14px 16px; border-radius:16px}
  .brief-item{padding:11px 13px; border-radius:12px}
  .brief-title{font-size:14px}

  /* 메뉴판 (보드) 모바일 뷰 */
  .bd-row{grid-template-columns:4px 1fr auto 16px; gap:0 10px}
  .bd-name{padding:12px 0 2px; grid-column:2; font-size:15.5px}
  .bd-teaser{grid-column:2; padding:0 0 12px; font-size:12.5px; white-space:normal;
    display:-webkit-box; -webkit-line-clamp:1; -webkit-box-orient:vertical}
  .sparkline{display:none}
  .bd-nums{grid-column:3; grid-row:1/3; padding:12px 0}
  .bd-go{grid-column:4; grid-row:1/3; padding-right:12px}

  /* 속보 & 피드: 모바일 맞춤 세로 배치 (제목 100% 확보) */
  .b-item{display:grid; grid-template-columns:1fr 36px; grid-template-rows:auto auto;
    gap:6px 8px; padding:12px 14px}
  .b-title{grid-column:1; grid-row:1; font-size:15.5px; line-height:1.48; white-space:normal;
    display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical}
  .b-time{display:none}
  .b-list li:first-child .b-item{padding:16px 14px}
  .b-list li:first-child .b-title{font-size:18px; line-height:1.45}
  .b-item .bm-btn{grid-column:2; grid-row:1/3; align-self:center; font-size:18px;
    padding:8px; opacity:0.55; border-radius:8px}
  .b-tag-wrap{grid-column:1; grid-row:2; display:flex; align-items:center; gap:6px; font-size:11px}
  .b-src{display:inline-block; font-size:11px; color:var(--ink-3)}

  .f-row{display:grid; grid-template-columns:1fr 36px; grid-template-rows:auto auto;
    gap:5px 8px; padding:11px 14px}
  .f-title{grid-column:1; grid-row:1; font-size:15px; line-height:1.45; white-space:normal;
    display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical}
  .f-row .bm-btn{grid-column:2; grid-row:1/3; align-self:center; font-size:18px;
    padding:8px; opacity:0.55; border-radius:8px}
  .f-meta-wrap{grid-column:1; grid-row:2; display:flex; align-items:center; gap:6px; font-size:11px}
  .f-time{font-size:11px}
  .f-src{display:inline-block; font-size:11px; text-align:left; color:var(--ink-3)}

  /* 주제 상세 */
  .detail-head{padding:16px 14px 12px}
  .detail-name{font-size:22px}
  .row{padding:12px 14px}
  .row-title{font-size:15px; line-height:1.5}
}
</style>
</head>
<body>

<div class="top">
  <div class="top-in">
    <a class="brand" href="/" id="brand-refresh" title="세상돌아가는 판세 (새로고침)">세상돌아가는 판세</a>
    <span class="nav-new" id="navnew"></span>
    <span class="top-right">
      <span class="stamp"><span class="dot-live"></span>$UPDATED_HM<span class="stamp-sfx"> 갱신 · 30분마다</span></span>
      <button class="btn" id="theme-toggle" type="button" aria-label="테마 전환">🌓 모드</button>
    </span>
$METALS
  </div>
  <div class="menu-wrap">
    <div class="menu" id="tabmenu" role="tablist" aria-label="주제 메뉴">
      <button class="m-btn" type="button" role="tab" data-view="all" aria-selected="true">전체</button>
      <button class="m-btn" type="button" role="tab" data-view="bookmarks" aria-selected="false">🔖 스크랩 <span class="n" id="bm-badge">0</span></button>
$MENU
    </div>
  </div>
</div>

<main>
  <header class="masthead">
    <div class="masthead-in">
      <div>
        <h1 class="wordmark hl"><a href="/" id="wordmark-refresh" title="세상돌아가는 판세 (새로고침)">세상돌아가는 판세</a></h1>
        <p class="wordmark-sub">$SUBTITLE</p>
      </div>
      <div class="masthead-date">
        <b>$DATE_LONG</b>
        구글 뉴스에서 모은 $TOTAL건
      </div>
    </div>
  </header>
  <div class="rule-thin"></div>

  <!-- 실시간 검색바 -->
  <div class="search-bar">
    <div class="search-in">
      <svg class="search-icon" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd"/>
      </svg>
      <input id="search-input" class="search-input" type="search" placeholder="기사 검색 (예: 금리, 엔비디아, 아파트, 테더...)" autocomplete="off">
      <button id="search-clear" class="search-clear hidden" type="button" aria-label="검색어 지우기">✕</button>
    </div>
  </div>

  <!-- 검색 결과 영역 -->
  <div id="search-section" class="card hidden" style="margin-bottom:24px;">
    <div class="card-head">
      <span class="eyebrow" id="search-count">검색 결과 0건</span>
    </div>
    <ul class="feed" id="search-list"></ul>
  </div>

  <div id="overview" class="stack">
    <!-- 오늘의 판세 3줄 브리핑 -->
    <section class="brief-card" aria-label="오늘의 판세 브리핑">
      <div class="brief-head">
        <span class="brief-pill">✨ 오늘의 3줄 판세</span>
        <span class="brief-sub">현재 주목받는 핵심 헤드라인</span>
        <button class="brief-copy" id="copy-briefing" type="button">📋 브리핑 복사</button>
      </div>
      <div class="brief-grid" id="briefing-container">
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
        <span class="zone-note">주제별 주요 흐름</span>
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

  <!-- 스크랩(북마크) 전용 상세 섹션 -->
  <section class="detail card hidden" data-topic="bookmarks" aria-label="스크랩한 기사">
    <div class="detail-head">
      <span class="detail-name hl">🔖 스크랩한 기사</span>
      <span class="detail-stat"><b id="bm-total">0</b>건 저장됨</span>
    </div>
    <ul class="feed" id="bm-list" style="min-height:80px;"></ul>
  </section>

$DETAILS

  <footer>
    <span>구글 뉴스 RSS · 최근 3일</span><span>·</span>
    <span>유사·홍보성 기사는 자동 필터링</span><span>·</span>
    <span>다음 갱신 <span id="countdown">–</span></span>
  </footer>
</main>

<div class="toast" id="toast">알림</div>

<script>
(function(){
  var GEN = $GEN_TS * 1000, PERIOD = 30 * 60 * 1000;
  var DEADLINE = GEN + PERIOD + Math.floor(Math.random() * 120000);
  var NAMES = $NAMES;
  NAMES["bookmarks"] = "스크랩";

  function showToast(msg){
    var t = document.getElementById("toast");
    t.textContent = msg;
    t.classList.add("show");
    setTimeout(function(){ t.classList.remove("show"); }, 2000);
  }

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

  var brandEl = document.getElementById("brand-refresh");
  var wordmarkEl = document.getElementById("wordmark-refresh");
  if (brandEl) brandEl.addEventListener("click", function(e){ e.preventDefault(); doReload(); });
  if (wordmarkEl) wordmarkEl.addEventListener("click", function(e){ e.preventDefault(); doReload(); });

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

  /* 테마(다크/라이트) 토글 */
  var themeBtn = document.getElementById("theme-toggle");
  function getEffectiveTheme(){
    var explicit = document.documentElement.getAttribute("data-theme");
    if (explicit) return explicit;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  function updateThemeButton(){
    var curTheme = getEffectiveTheme();
    themeBtn.textContent = curTheme === "dark" ? "☀️ 라이트" : "🌙 다크";
  }
  function toggleTheme(){
    var curTheme = getEffectiveTheme();
    var nextTheme = curTheme === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", nextTheme);
    try { localStorage.setItem("panse-theme", nextTheme); } catch(e){}
    updateThemeButton();
  }
  if (themeBtn) {
    updateThemeButton();
    themeBtn.addEventListener("click", toggleTheme);
  }

  /* 🔖 북마크(스크랩) 관리 */
  var BM_KEY = "panse-bookmarks";
  function getBookmarks(){
    try { return JSON.parse(localStorage.getItem(BM_KEY)) || []; } catch(e){ return []; }
  }
  function toggleBookmark(item){
    var bms = getBookmarks();
    var idx = bms.findIndex(function(b){ return b.link === item.link; });
    if (idx >= 0) {
      bms.splice(idx, 1);
      showToast("북마크가 해제되었습니다");
    } else {
      bms.unshift(item);
      showToast("스크랩 탭에 저장되었습니다 🔖");
    }
    try { localStorage.setItem(BM_KEY, JSON.stringify(bms)); } catch(e){}
    renderBookmarks();
    updateBookmarkButtons();
  }
  function updateBookmarkButtons(){
    var bms = getBookmarks();
    var bmMap = {};
    bms.forEach(function(b){ bmMap[b.link] = true; });
    document.querySelectorAll(".bm-btn").forEach(function(btn){
      var l = btn.dataset.link;
      btn.classList.toggle("active", !!bmMap[l]);
      btn.title = bmMap[l] ? "스크랩 취소" : "기사 스크랩";
    });
    var badge = document.getElementById("bm-badge");
    var total = document.getElementById("bm-total");
    if (badge) badge.textContent = bms.length;
    if (total) total.textContent = bms.length;
  }
  function renderBookmarks(){
    var bms = getBookmarks();
    var list = document.getElementById("bm-list");
    if (!list) return;
    if (bms.length === 0) {
      list.innerHTML = "<li style=\"padding:30px; text-align:center; color:var(--ink-3); font-size:14px;\">스크랩한 기사가 없습니다. 기사 옆 🔖 버튼을 눌러 저장해 보세요!</li>";
      return;
    }
    list.innerHTML = bms.map(function(it){
      return "<li class=\"f-item\" data-topic=\"" + it.topicId + "\">" +
        "<div class=\"f-row t-" + it.topicId + "\">" +
        "<a class=\"f-title\" href=\"" + it.link + "\" target=\"_blank\" rel=\"noopener\">" + it.title + "</a>" +
        "<div class=\"f-meta-wrap\">" +
        "<span class=\"f-tag\"><span class=\"swatch\"></span>" + (it.topicName || "기사") + "</span>" +
        "<span class=\"f-src\">" + it.src + "</span><span class=\"sep\">·</span>" +
        "<span class=\"f-time\" data-ts=\"" + it.ts + "\">" + rel(it.ts) + "</span>" +
        "</div>" +
        "<button class=\"bm-btn active\" data-link=\"" + it.link + "\" type=\"button\" aria-label=\"북마크 토글\">🔖</button>" +
        "</div></li>";
    }).join("");
    list.querySelectorAll(".bm-btn").forEach(function(btn){
      btn.addEventListener("click", function(e){
        e.preventDefault(); e.stopPropagation();
        var l = btn.dataset.link;
        var bms = getBookmarks();
        var it = bms.find(function(b){ return b.link === l; });
        if (it) toggleBookmark(it);
      });
    });
  }
  document.querySelectorAll(".bm-btn").forEach(function(btn){
    btn.addEventListener("click", function(e){
      e.preventDefault(); e.stopPropagation();
      var item = {
        link: btn.dataset.link,
        title: btn.dataset.title,
        src: btn.dataset.src,
        ts: Number(btn.dataset.ts),
        topicId: btn.dataset.topic,
        topicName: btn.dataset.topicname
      };
      toggleBookmark(item);
    });
  });
  renderBookmarks();
  updateBookmarkButtons();

  /* 📋 오늘의 3줄 브리핑 복사 */
  var copyBtn = document.getElementById("copy-briefing");
  if (copyBtn) {
    copyBtn.addEventListener("click", function(){
      var items = [].slice.call(document.querySelectorAll(".brief-item"));
      var text = "[세상돌아가는 판세 - 오늘의 핵심 요약]\n";
      items.forEach(function(it){
        var tag = it.querySelector(".brief-tag").textContent.trim();
        var title = it.querySelector(".brief-title").textContent.trim();
        text += "• [" + tag + "] " + title + "\n";
      });
      text += "\n🔗 https://daseot-news.surge.sh";
      navigator.clipboard.writeText(text).then(function(){
        showToast("✓ 오늘의 브리핑이 복사되었습니다!");
      }).catch(function(){
        showToast("복사에 실패했습니다.");
      });
    });
  }

  /* 🔍 실시간 기사 검색 */
  var searchInput = document.getElementById("search-input");
  var searchClear = document.getElementById("search-clear");
  var searchSection = document.getElementById("search-section");
  var searchList = document.getElementById("search-list");
  var searchCount = document.getElementById("search-count");

  var allArticles = [];
  document.querySelectorAll(".feed .f-item, .d-list .d-item").forEach(function(el){
    var a = el.querySelector("a");
    if (!a) return;
    var titleEl = el.querySelector(".f-title, .row-title");
    var srcEl = el.querySelector(".f-src, .meta-chip");
    var timeEl = el.querySelector("[data-ts]");
    var topic = el.dataset.topic || el.closest("section")?.dataset.topic || "";
    if (titleEl && a.href && !allArticles.some(function(x){ return x.link === a.href; })) {
      allArticles.push({
        title: titleEl.textContent.trim(),
        link: a.href,
        src: srcEl ? srcEl.textContent.trim() : "",
        ts: timeEl ? Number(timeEl.dataset.ts) : 0,
        topic: topic,
        topicName: NAMES[topic] || "뉴스"
      });
    }
  });

  function doSearch(kw){
    kw = (kw || "").trim().toLowerCase();
    searchClear.classList.toggle("hidden", !kw);
    if (!kw) {
      searchSection.classList.add("hidden");
      return;
    }
    var matches = allArticles.filter(function(it){
      return it.title.toLowerCase().indexOf(kw) >= 0 ||
             it.src.toLowerCase().indexOf(kw) >= 0 ||
             it.topicName.toLowerCase().indexOf(kw) >= 0;
    });
    searchCount.textContent = "검색 결과 " + matches.length + "건";
    searchSection.classList.remove("hidden");
    if (matches.length === 0) {
      searchList.innerHTML = "<li style=\"padding:30px; text-align:center; color:var(--ink-3); font-size:14px;\">검색 결과가 없습니다.</li>";
      return;
    }
    searchList.innerHTML = matches.map(function(it){
      return "<li class=\"f-item\" data-topic=\"" + it.topic + "\">" +
        "<div class=\"f-row t-" + it.topic + "\">" +
        "<a class=\"f-title\" href=\"" + it.link + "\" target=\"_blank\" rel=\"noopener\">" + it.title + "</a>" +
        "<div class=\"f-meta-wrap\">" +
        "<span class=\"f-tag\"><span class=\"swatch\"></span>" + it.topicName + "</span>" +
        "<span class=\"f-src\">" + it.src + "</span><span class=\"sep\">·</span>" +
        "<span class=\"f-time\" data-ts=\"" + it.ts + "\">" + rel(it.ts) + "</span>" +
        "</div>" +
        "<button class=\"bm-btn\" data-link=\"" + it.link + "\" data-title=\"" + it.title.replace(/\"/g, "&quot;") + "\" data-src=\"" + it.src + "\" data-ts=\"" + it.ts + "\" data-topic=\"" + it.topic + "\" data-topicname=\"" + it.topicName + "\" type=\"button\" aria-label=\"북마크\">🔖</button>" +
        "</div></li>";
    }).join("");
    searchList.querySelectorAll(".bm-btn").forEach(function(btn){
      btn.addEventListener("click", function(e){
        e.preventDefault(); e.stopPropagation();
        toggleBookmark({
          link: btn.dataset.link, title: btn.dataset.title, src: btn.dataset.src,
          ts: Number(btn.dataset.ts), topicId: btn.dataset.topic, topicName: btn.dataset.topicname
        });
      });
    });
    updateBookmarkButtons();
  }

  if (searchInput) {
    searchInput.addEventListener("input", function(){ doSearch(searchInput.value); });
    searchInput.addEventListener("keydown", function(e){
      if (e.key === "Escape") {
        searchInput.value = "";
        doSearch("");
      }
    });
  }
  if (searchClear) {
    searchClear.addEventListener("click", function(){
      searchInput.value = "";
      doSearch("");
      searchInput.focus();
    });
  }

  /* 화면 뷰 전환 */
  var overview = document.getElementById("overview");
  var details = [].slice.call(document.querySelectorAll(".detail"));
  var menu = [].slice.call(document.querySelectorAll(".m-btn"));

  function show(view){
    overview.classList.toggle("hidden", view !== "all");
    details.forEach(function(d){ d.classList.toggle("hidden", d.dataset.topic !== view); });
    menu.forEach(function(b){ b.setAttribute("aria-selected", String(b.dataset.view === view)); });
    document.title = (view === "all" ? "세상돌아가는 판세" : (NAMES[view] || "주제") + " · 세상돌아가는 판세");
    if (view === "bookmarks") renderBookmarks();
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
        ("gold",   "금",      "$", 0, "금 현물 · 미국 달러/트로이온스"),
        ("silver", "은",      "$", 2, "은 현물 · 미국 달러/트로이온스"),
        ("btc",    "비트코인", "$", 0, "비트코인 (BTC/USD) · 24시간 변동률"),
    ),
    (
        ("usdkrw", "달러",    "₩", 1, "원/달러 · 하나은행 매매기준율"),
        ("jpykrw", "엔100",   "₩", 1, "원/100엔 · 하나은행 매매기준율"),
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
    return f'    <div class="metals"{stale}>\n' + "\n".join(rows) + '\n    </div>'


def render_sparkline(hist24):
    if not hist24 or not any(hist24):
        return ""
    m = max(hist24) or 1
    bars = []
    for count in hist24:
        pct = max(10, int(count / m * 100)) if count > 0 else 10
        bars.append(f'<span class="sp-bar" style="height:{pct}%;" title="{count}건"></span>')
    return f'<span class="sparkline" title="지난 24시간 기사 발생 추이">{"".join(bars)}</span>'


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
        f'        <li><div class="b-item t-{t["id"]}">'
        f'<a class="b-title" href="{esc(it["link"])}" target="_blank" rel="noopener">{esc(it["title"])}</a>'
        f'<div class="b-tag-wrap">'
        f'<span class="b-tag"><span class="swatch"></span>{esc(t["name"])}</span>'
        f'<span class="b-src">{esc(it["source"])}</span><span class="sep">·</span>'
        f'<span class="b-time" data-ts="{it["ts"]}">–</span>'
        f'</div>'
        f'<button class="bm-btn" data-link="{esc(it["link"])}" data-title="{esc(it["title"])}" data-src="{esc(it["source"])}" data-ts="{it["ts"]}" data-topic="{t["id"]}" data-topicname="{esc(t["name"])}" type="button" aria-label="북마크">🔖</button>'
        f'</div></li>'
        for it, t in picks
    )

    # 오늘의 3줄 브리핑
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
        spark = render_sparkline(t.get("hist24", []))
        board.append(
            f'        <li><button class="bd-row t-{t["id"]}" type="button" data-topic="{t["id"]}">\n'
            f'          <span class="bd-bar"></span>\n'
            f'          <span class="bd-name">{esc(t["name"])}</span>\n'
            f'          <span class="bd-teaser">{teaser}</span>\n'
            f'          <span class="bd-nums">{new_tag}<span class="bd-total">{t["total"]}건</span></span>\n'
            f'          {spark}\n'
            f'          <span class="bd-go" aria-hidden="true">›</span>\n'
            f'        </button></li>'
        )

    rest = [(it, t) for it, t in flat if it["link"] not in used]
    feed = "\n".join(
        f'          <li class="f-item" data-topic="{t["id"]}">'
        f'<div class="f-row t-{t["id"]}">'
        f'<a class="f-title" href="{esc(it["link"])}" target="_blank" rel="noopener">{esc(it["title"])}</a>'
        f'<div class="f-meta-wrap">'
        f'<span class="f-tag"><span class="swatch"></span>{esc(t["name"])}</span>'
        f'<span class="f-src">{esc(it["source"])}</span><span class="sep">·</span>'
        f'<span class="f-time" data-ts="{it["ts"]}">–</span>'
        f'</div>'
        f'<button class="bm-btn" data-link="{esc(it["link"])}" data-title="{esc(it["title"])}" data-src="{esc(it["source"])}" data-ts="{it["ts"]}" data-topic="{t["id"]}" data-topicname="{esc(t["name"])}" type="button" aria-label="북마크">🔖</button>'
        f'</div></li>'
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
                f'        <li class="d-item"><div class="row">'
                f'<a class="row-title" href="{esc(it["link"])}" target="_blank" rel="noopener">{esc(it["title"])}</a>'
                f'<div class="row-meta">{badge_html}<span class="meta-chip">{esc(it["source"])}</span>'
                f'<span class="sep">·</span><span data-ts="{it["ts"]}">–</span>'
                f'<button class="bm-btn" style="margin-left:auto;" data-link="{esc(it["link"])}" data-title="{esc(it["title"])}" data-src="{esc(it["source"])}" data-ts="{it["ts"]}" data-topic="{t["id"]}" data-topicname="{esc(t["name"])}" type="button" aria-label="북마크">🔖</button>'
                f'</div></div></li>'
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
