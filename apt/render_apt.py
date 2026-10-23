#!/usr/bin/env python3
"""apt/apt.json -> public/apt/index.html (판세 '청약' 메뉴 페이지).

데이터 수집은 하루 몇 번(apt.yml)만 하고, 이 렌더는 판세 갱신 때마다 돌려
D-day·접수 상태가 항상 오늘 기준이 되도록 한다.
"""
import html
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from string import Template

from eligibility import eligibility_html

KST = timezone(timedelta(hours=9))
HERE = Path(__file__).parent
ROOT = HERE.parent
FAV_CITIES = ("화성", "아산")  # 관심지역: 동탄(화성·화성특례시)·아산 — 시 이름 앞부분으로 비교
REGION_GROUPS = [
    ("수도권", ["서울", "경기", "인천"]),
    ("광역시", ["부산", "대구", "광주", "대전", "울산", "세종"]),
    ("도", ["강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"]),
]
STATUS_ORDER = ["접수중", "접수예정", "발표대기", "마감", "공고"]
FLAG_NOTE = "투기과열지구·분양가상한제 여부에 따라 재당첨 제한, 전매제한, 실거주 의무가 달라집니다. 정확한 조건은 모집공고문에서 확인하세요."


def e(s):
    return html.escape(str(s or ""))


def d(s):
    try:
        return date.fromisoformat((s or "")[:10])
    except ValueError:
        return None


def md(s):
    x = d(s)
    return f"{x.month}/{x.day}({'월화수목금토일'[x.weekday()]})" if x else ""


def span_txt(sp):
    if not sp:
        return ""
    return md(sp[0]) if sp[0] == sp[1] else f"{md(sp[0])} ~ {md(sp[1])}"


def won(manwon):
    """만원 단위 -> '5억 2,340만'."""
    try:
        v = int(float(manwon))
    except (TypeError, ValueError):
        return "-"
    eok, man = divmod(v, 10000)
    if eok and man:
        return f"{eok}억 {man:,}만"
    return f"{eok}억" if eok else f"{man:,}만"


def house_type(t):
    """'084.9800A' -> '84A'."""
    t = (t or "").strip()
    num = "".join(ch for ch in t if ch.isdigit() or ch == ".")
    try:
        return f"{int(float(num))}{t[len(num):].strip() if t.startswith(num) else ''}"
    except ValueError:
        return t


def status(c, today):
    sp = c.get("receipt")
    if not sp:
        return "공고"
    b, en = d(sp[0]), d(sp[1])
    if b and today < b:
        return "접수예정"
    if en and today <= en:
        return "접수중"
    w = d(c.get("winner_date"))
    return "발표대기" if w and today <= w else "마감"


def dday(c, st, today):
    if st == "접수예정":
        n = (d(c["receipt"][0]) - today).days
        return f"D-{n}"
    if st == "접수중":
        return "오늘 마감" if d(c["receipt"][1]) == today else f"~{md(c['receipt'][1])}"
    if st == "발표대기":
        return "오늘 발표" if d(c["winner_date"]) == today else f"발표 {md(c['winner_date'])}"
    return ""


def short_area(c):
    city = (c.get("city") or "").removesuffix("특례시").removesuffix("시").removesuffix("군")
    return f"{c.get('area') or ''} {city}".strip()


def phone(p):
    """'0328348890' -> '032-834-8890', '15516881' -> '1551-6881'."""
    p = "".join(ch for ch in (p or "") if ch.isdigit())
    if len(p) == 8:
        return f"{p[:4]}-{p[4:]}"
    if p.startswith("02") and len(p) in (9, 10):
        return f"02-{p[2:-4]}-{p[-4:]}"
    if len(p) in (10, 11):
        return f"{p[:3]}-{p[3:-4]}-{p[-4:]}"
    return p


def price_range(c):
    ps = [float(m["top_price"]) for m in c.get("models", []) if m.get("top_price")]
    if not ps:
        return ""
    lo, hi = min(ps), max(ps)
    return won(hi) if lo == hi else f"{won(lo)} ~ {won(hi)}"


def per_pyeong(m):
    try:
        return f"{int(float(m['top_price']) / (float(m['supply_area']) / 3.3058)):,}만"
    except (TypeError, ValueError, ZeroDivisionError):
        return "-"


def detail_html(c, today):
    sched = []
    for label, sp in c.get("schedule", []):
        b, en = d(sp[0]), d(sp[1])
        cls = "now" if b and en and b <= today <= en else "past" if en and en < today else ""
        sched.append(f'<tr class="{cls}"><th>{e(label)}</th><td>{span_txt(sp)}</td></tr>')
    if len(c.get("move_in") or "") >= 6:
        sched.append(f'<tr><th>입주 예정</th><td>{c["move_in"][:4]}년 {int(c["move_in"][4:6])}월</td></tr>')

    models = "".join(
        f'<tr><th>{e(house_type(m["type"]))}</th><td class="r">{e(m["supply_area"])}㎡</td>'
        f'<td class="r">{e(m["supply"] or "-")}</td><td class="r">{e(m["special"] or "-")}</td>'
        f'<td class="r"><b>{won(m["top_price"])}</b></td><td class="r">{per_pyeong(m)}</td></tr>'
        for m in c.get("models", []))
    models_html = (
        '<div class="tbl-wrap"><table class="tbl"><thead><tr><th>주택형</th><th class="r">공급면적</th>'
        '<th class="r">일반</th><th class="r">특별</th><th class="r">최고 분양가</th><th class="r">평당가</th>'
        f'</tr></thead><tbody>{models}</tbody></table></div>'
        '<p class="note">주택형 = 전용면적(㎡). 평당가는 최고 분양가 ÷ 공급면적(평) 기준 추정치.</p>'
    ) if models else '<p class="note">주택형별 정보가 아직 공개되지 않았습니다.</p>'

    comp = [r for r in c.get("competition", []) if r.get("rate") or r.get("requests")]
    comp_html = ""
    if comp:
        rows = "".join(
            f'<tr><th>{e(house_type(r["type"]))}</th><td>{e(r["rank"])}순위 {e(r["reside"])}</td>'
            f'<td class="r">{e(r["supply"])}</td><td class="r">{e(r["requests"])}</td>'
            f'<td class="r"><b>{e(r["rate"])}</b></td></tr>' for r in comp)
        comp_html = ('<h4>청약 경쟁률</h4><div class="tbl-wrap"><table class="tbl"><thead><tr><th>주택형</th><th>구분</th>'
                     f'<th class="r">공급</th><th class="r">접수</th><th class="r">경쟁률</th></tr></thead><tbody>{rows}</tbody></table></div>')

    flags = [k for k, v in c.get("flags", {}).items() if v]
    flags_html = "".join(f'<span class="chip flag">{e(f)}</span>' for f in flags) or '<span class="muted">해당 없음</span>'

    info = [("위치", c.get("address")), ("주택 구분", c.get("type_name")), ("시공사", c.get("builder")),
            ("시행사", c.get("developer")), ("모집공고일", md(c.get("notice_date"))), ("문의", phone(c.get("phone")))]
    info_html = "".join(f'<tr><th>{k}</th><td>{e(v)}</td></tr>' for k, v in info if v)

    links = []
    if c.get("url"):
        links.append(f'<a href="{e(c["url"])}" target="_blank" rel="noopener">청약홈 모집공고 ↗</a>')
    if c.get("homepage"):
        hp = c["homepage"] if c["homepage"].startswith("http") else "http://" + c["homepage"]
        links.append(f'<a href="{e(hp)}" target="_blank" rel="noopener nofollow">분양 홈페이지 ↗</a>')
    if c.get("address"):
        links.append(f'<a href="https://map.naver.com/p/search/{e(c["address"])}" target="_blank" rel="noopener">네이버 지도 ↗</a>')

    return f"""<div class="detail-grid">
  <section><h4>단지 개요</h4><table class="kv">{info_html}</table></section>
  <section><h4>청약 일정</h4><table class="kv sched">{"".join(sched)}</table></section>
</div>
<h4>주택형별 분양가</h4>{models_html}
{eligibility_html(c)}
<h4>규제·지구 지정</h4><p>{flags_html}</p><p class="note">{FLAG_NOTE}</p>
{comp_html}
<p class="links">{" · ".join(links)}</p>"""


def card_html(c, today):
    st = status(c, today)
    fav = (c.get("city") or "").startswith(FAV_CITIES)
    dd = dday(c, st, today)
    meta = " · ".join(x for x in [
        f'{c["households"]}세대' if c.get("households") else "",
        f"접수 {span_txt(c['receipt'])}" if c.get("receipt") else f"공고 {md(c.get('notice_date'))}",
    ] if x)
    price = price_range(c)
    return f"""<details class="apt-card" data-status="{st}" data-area="{e(c.get('area'))}" data-fav="{1 if fav else 0}">
  <summary>
    <div class="ac-top">
      <span class="st st-{st}">{st}</span>{f'<span class="dd">{e(dd)}</span>' if dd else ""}
      <span class="chip">{e(short_area(c))}</span>{'<span class="chip">무순위</span>' if c["kind"] == "무순위" else ""}{'<span class="chip fav">⭐ 관심지역</span>' if fav else ""}
    </div>
    <div class="ac-name hl">{e(c["name"])}</div>
    <div class="ac-meta">{meta}</div>
    {f'<div class="ac-price">최고 분양가 <b>{price}</b></div>' if price else ""}
    <span class="ac-more" aria-hidden="true">상세 ▾</span>
  </summary>
  <div class="ac-body">{detail_html(c, today)}</div>
</details>"""


PAGE = Template(r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>아파트 청약 캘린더 · 판세</title>
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover, maximum-scale=5">
<meta name="description" content="전국 아파트 청약 일정과 주택형별 분양가, 경쟁률을 청약홈 데이터로 매일 정리합니다.">
<meta name="theme-color" content="#F8F6F0" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#080D1A" media="(prefers-color-scheme: dark)">
<link rel="manifest" href="/manifest.json">
<link rel="apple-touch-icon" href="/icon.svg">
<link rel="icon" type="image/svg+xml" href="/icon.svg">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@600;700&display=swap">
<script>
(function(){ try { var s = localStorage.getItem("panse-theme"); if (s) document.documentElement.setAttribute("data-theme", s); } catch(e){} })();
</script>
<style>
:root, :root[data-theme="light"]{
  --ground:#F8F6F0; --surface:#FFFFFF; --surface-2:#EFECE3; --hairline:rgba(15,23,42,0.09); --rule:#0F172A;
  --ink:#0F172A; --ink-2:#475569; --ink-3:#94A3B8; --nav:rgba(248,246,240,0.92);
  --blue:#0284C7; --gold:#B45309; --red:#E11D48; --red-bg:rgba(225,29,72,0.09); --violet:#7C3AED; --violet-bg:rgba(124,58,237,0.1);
  --blue-bg:rgba(2,132,199,0.1); --gold-bg:rgba(217,119,6,0.12);
  --shadow:0 4px 20px rgba(15,23,42,0.04), 0 1px 3px rgba(15,23,42,0.03);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ground:#080D1A; --surface:#0F172A; --surface-2:#1E293B; --hairline:rgba(148,163,184,0.15); --rule:#F8FAFC;
    --ink:#F8FAFC; --ink-2:#94A3B8; --ink-3:#64748B; --nav:rgba(8,13,26,0.92);
    --blue:#38BDF8; --gold:#F59E0B; --red:#FB7185; --red-bg:rgba(251,113,133,0.14); --violet:#A78BFA; --violet-bg:rgba(167,139,250,0.14);
    --blue-bg:rgba(56,189,248,0.12); --gold-bg:rgba(245,158,11,0.14);
    --shadow:0 8px 32px rgba(0,0,0,0.5);
  }
}
:root[data-theme="dark"]{
  --ground:#080D1A; --surface:#0F172A; --surface-2:#1E293B; --hairline:rgba(148,163,184,0.15); --rule:#F8FAFC;
  --ink:#F8FAFC; --ink-2:#94A3B8; --ink-3:#64748B; --nav:rgba(8,13,26,0.92);
  --blue:#38BDF8; --gold:#F59E0B; --red:#FB7185; --red-bg:rgba(251,113,133,0.14); --violet:#A78BFA; --violet-bg:rgba(167,139,250,0.14);
  --blue-bg:rgba(56,189,248,0.12); --gold-bg:rgba(245,158,11,0.14);
  --shadow:0 8px 32px rgba(0,0,0,0.5);
}
*{box-sizing:border-box; -webkit-tap-highlight-color:transparent}
body{margin:0; background:var(--ground); color:var(--ink); font-size:15px; line-height:1.55;
  font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Pretendard","Apple SD Gothic Neo","Segoe UI",system-ui,sans-serif;
  -webkit-font-smoothing:antialiased; word-break:keep-all; overflow-wrap:anywhere}
a{color:inherit; text-decoration:none}
button{font:inherit; color:inherit; border:0; background:transparent; cursor:pointer}
:focus-visible{outline:2px solid var(--blue); outline-offset:3px; border-radius:8px}
.hl{font-family:"Noto Serif KR",Georgia,serif}
.muted{color:var(--ink-3)}

.top{position:sticky; top:0; z-index:40; background:var(--nav); backdrop-filter:saturate(190%) blur(24px);
  -webkit-backdrop-filter:saturate(190%) blur(24px); border-bottom:1px solid var(--hairline)}
.top-main{max-width:1240px; margin:0 auto; padding:10px 24px; display:flex; align-items:center; gap:14px; justify-content:space-between}
.brand{font-size:15.5px; font-weight:850; letter-spacing:.05em}
.top-right{display:flex; align-items:center; gap:8px}
.back{font-size:13px; color:var(--ink-2); font-weight:600}
.back:hover{color:var(--ink)}
.theme-btn{border:1px solid var(--hairline); background:var(--surface); font-size:13px; padding:5px 10px; border-radius:980px}

main{max-width:1240px; margin:0 auto; padding:0 24px calc(80px + env(safe-area-inset-bottom))}
.masthead{padding:26px 0 16px; border-bottom:2px solid var(--rule); margin-bottom:18px;
  display:flex; justify-content:space-between; align-items:flex-end; gap:16px; flex-wrap:wrap}
.wordmark{font-size:34px; font-weight:700; margin:0; letter-spacing:-.02em; line-height:1.2}
.sub{margin:6px 0 0; color:var(--ink-2); font-size:14px}
.stats{display:flex; gap:18px; font-size:13px; color:var(--ink-2)}
.stats b{display:block; font-size:22px; color:var(--ink); font-variant-numeric:tabular-nums}
.stats .hot b{color:var(--red)}

.filters{display:flex; flex-wrap:wrap; gap:8px 22px; margin:0 0 8px}
.f-btn{border-bottom:2px solid transparent; color:var(--ink-3); font-size:14.5px; font-weight:550; padding:7px 0 6px}
.f-btn:hover{color:var(--ink)}
.f-btn[aria-pressed="true"]{color:var(--ink); font-weight:700; border-bottom-color:var(--ink)}
.f-btn .n{font-size:10.5px; font-weight:700; color:var(--ink-3); position:relative; top:-4px; margin-left:3px}
.areas{display:flex; flex-direction:column; gap:0; margin:6px 0 22px;
  padding:4px 14px; background:var(--surface); border:1px solid var(--hairline); border-radius:14px}
.a-group{display:flex; flex-wrap:wrap; align-items:center; gap:6px; padding:9px 0}
.a-group + .a-group{border-top:1px solid var(--hairline)}
.a-label{font-size:11px; font-weight:700; color:var(--ink-3); letter-spacing:.04em; min-width:46px}
.a-btn{font-size:12.5px; font-weight:600; padding:4px 10px; border-radius:980px; border:1px solid var(--hairline);
  background:var(--ground); color:var(--ink-2); white-space:nowrap}
.a-btn .n{font-size:10.5px; font-weight:700; margin-left:4px; color:var(--blue); font-variant-numeric:tabular-nums}
.a-btn.zero{color:var(--ink-3); opacity:.55}
.a-btn.zero .n{display:none}
.a-btn.fav{color:var(--gold); border-color:var(--gold-bg); background:var(--gold-bg)}
.a-btn[aria-pressed="true"]{background:var(--ink); color:var(--ground); border-color:var(--ink); opacity:1}
.a-btn[aria-pressed="true"] .n{color:inherit; opacity:.75}

.list{display:grid; grid-template-columns:repeat(auto-fill, minmax(min(340px, 100%), 1fr)); gap:14px; align-items:start}
.apt-card{min-width:0; background:var(--surface); border:1px solid var(--hairline); border-radius:14px; box-shadow:var(--shadow); overflow:hidden}
.apt-card[open]{grid-column:1/-1}
.apt-card summary{list-style:none; cursor:pointer; padding:16px 18px; position:relative}
.apt-card summary::-webkit-details-marker{display:none}
.ac-top{display:flex; flex-wrap:wrap; align-items:center; gap:6px}
.st{font-size:11.5px; font-weight:700; padding:2px 8px; border-radius:6px; white-space:nowrap}
.st-접수중{background:var(--red-bg); color:var(--red)}
.st-접수예정{background:var(--blue-bg); color:var(--blue)}
.st-발표대기{background:var(--gold-bg); color:var(--gold)}
.st-마감,.st-공고{background:var(--surface-2); color:var(--ink-3)}
.dd{font-size:12px; font-weight:800; color:var(--ink); font-variant-numeric:tabular-nums}
.chip{font-size:11.5px; font-weight:600; color:var(--ink-2); background:var(--surface-2); padding:2px 8px; border-radius:6px; white-space:nowrap}
.chip.fav{color:var(--gold); background:var(--gold-bg)}
.chip.flag{color:var(--violet); background:var(--violet-bg); margin-right:4px}
.ac-name{font-size:19px; font-weight:700; margin:8px 0 2px; line-height:1.35}
.ac-meta{font-size:13px; color:var(--ink-2)}
.ac-price{font-size:13px; color:var(--ink-2); margin-top:4px}
.ac-price b{color:var(--ink); font-size:14.5px}
.ac-more{position:absolute; right:16px; bottom:14px; font-size:12px; color:var(--ink-3)}
.apt-card[open] .ac-more{visibility:hidden}
.ac-body{padding:4px 18px 18px; border-top:1px solid var(--hairline)}
.ac-body h5{font-size:13px; margin:14px 0 4px; color:var(--ink-2)}
.ac-body h4{font-size:14px; margin:18px 0 6px; padding-left:8px; border-left:3px solid var(--blue)}
.detail-grid{display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:0 28px}
.kv,.tbl{width:100%; border-collapse:collapse; font-size:13.5px}
.kv th,.kv td,.tbl th,.tbl td{padding:7px 8px; border-bottom:1px solid var(--hairline); text-align:left; vertical-align:top}
.kv th{width:32%; color:var(--ink-2); font-weight:600; white-space:nowrap}
.tbl thead th{color:var(--ink-2); font-weight:600; background:var(--surface-2); white-space:nowrap}
.tbl .r{text-align:right; white-space:nowrap; font-variant-numeric:tabular-nums}
.tbl-wrap{overflow-x:auto}
.sched tr.past{color:var(--ink-3)}
.sched tr.now th,.sched tr.now td{color:var(--red); font-weight:700}
.sched tr.now td::after{content:" ◀ 오늘"}
.note{font-size:12px; color:var(--ink-3); margin:6px 0 0}
.links{margin:18px 0 0; font-size:13.5px; font-weight:600; color:var(--blue)}
.empty{padding:40px 0; text-align:center; color:var(--ink-3)}
.foot{margin-top:28px; font-size:12px; color:var(--ink-3); border-top:1px solid var(--hairline); padding-top:12px}

@media (max-width:640px){
  .top-main,main{padding-left:16px; padding-right:16px}
  .masthead{padding:18px 0 12px}
  .wordmark{font-size:26px}
  .stats{gap:14px} .stats b{font-size:19px}
  .filters{gap:0 14px}
  .areas{padding:2px 12px}
  .a-group{flex-wrap:nowrap; overflow-x:auto; scrollbar-width:none; -webkit-overflow-scrolling:touch}
  .a-group::-webkit-scrollbar{display:none}
  .a-label{min-width:40px; flex:none}
  .list{grid-template-columns:1fr}
  .detail-grid{grid-template-columns:minmax(0,1fr)}
  .masthead .sub{font-size:13px}
}
</style>
</head>
<body>
<div class="top">
  <div class="top-main">
    <a class="brand" href="/">◈ PANSE</a>
    <div class="top-right">
      <a class="back" href="/">← 뉴스 판세</a>
      <button class="theme-btn" id="theme-toggle" type="button" aria-label="테마 전환">🌓</button>
    </div>
  </div>
</div>
<main>
  <header class="masthead">
    <div>
      <h1 class="wordmark hl">아파트 청약 캘린더</h1>
      <p class="sub">청약홈 공고 기준 · 일정·분양가·경쟁률 $UPDATED</p>
    </div>
    <div class="stats">
      <div class="hot"><b>$N_NOW</b>접수 중</div>
      <div><b>$N_WEEK</b>7일 내 접수</div>
      <div><b>$N_WAIT</b>발표 대기</div>
    </div>
  </header>

  <nav class="filters" aria-label="상태">
$STATUS_BTNS
  </nav>
  <div class="areas" aria-label="지역">
$AREA_BTNS
  </div>

  <div class="list" id="list">
$CARDS
  </div>
  <p class="empty" id="empty" hidden>$EMPTY</p>

  <p class="foot">출처: 한국부동산원 청약홈 분양정보(공공데이터포털). 자동 정리된 정보이므로 실제 청약 전 반드시 모집공고문을 확인하세요.</p>
</main>
<script>
(function(){
  var KEY = "panse-apt-filter";
  var state = { status: "live", area: "all" };
  try { var s = JSON.parse(localStorage.getItem(KEY) || "null"); if (s) state = s; } catch(e){}
  var cards = [].slice.call(document.querySelectorAll(".apt-card"));
  var sBtns = [].slice.call(document.querySelectorAll(".f-btn"));
  var aBtns = [].slice.call(document.querySelectorAll(".a-btn"));
  if (!sBtns.some(function(b){ return b.dataset.s === state.status; })) state.status = "live";
  if (!aBtns.some(function(b){ return b.dataset.a === state.area; })) state.area = "all";

  function okStatus(c){
    var st = c.dataset.status;
    if (state.status === "live") return st === "접수중" || st === "접수예정";
    if (state.status === "all") return true;
    return st === state.status;
  }
  function okArea(c){
    if (state.area === "all") return true;
    if (state.area === "fav") return c.dataset.fav === "1";
    return c.dataset.area === state.area;
  }
  function apply(){
    var shown = 0;
    cards.forEach(function(c){ var ok = okStatus(c) && okArea(c); c.hidden = !ok; if (ok) shown++; });
    sBtns.forEach(function(b){ b.setAttribute("aria-pressed", b.dataset.s === state.status ? "true" : "false"); });
    aBtns.forEach(function(b){ b.setAttribute("aria-pressed", b.dataset.a === state.area ? "true" : "false"); });
    document.getElementById("empty").hidden = shown > 0;
    aBtns.forEach(function(b){
      var key = b.dataset.a, n = 0;
      cards.forEach(function(c){
        if (!okStatus(c)) return;
        if (key === "all" || (key === "fav" ? c.dataset.fav === "1" : c.dataset.area === key)) n++;
      });
      b.querySelector(".n").textContent = n;
      b.classList.toggle("zero", n === 0);
    });
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch(e){}
  }
  sBtns.forEach(function(b){ b.addEventListener("click", function(){ state.status = b.dataset.s; apply(); }); });
  aBtns.forEach(function(b){ b.addEventListener("click", function(){ state.area = b.dataset.a; apply(); }); });
  apply();

  var btn = document.getElementById("theme-toggle");
  function cur(){
    var s = document.documentElement.getAttribute("data-theme");
    return s || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  }
  function set(t){
    document.documentElement.setAttribute("data-theme", t);
    try { localStorage.setItem("panse-theme", t); } catch(e){}
    btn.textContent = t === "dark" ? "☀️" : "🌙";
  }
  set(cur());
  btn.addEventListener("click", function(){ set(cur() === "dark" ? "light" : "dark"); });
})();
</script>
</body>
</html>
""")


def build(src=HERE / "apt.json", out=ROOT / "public" / "apt" / "index.html"):
    now = datetime.now(KST)
    today = now.date()
    try:
        data = json.loads(Path(src).read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        data = {"complexes": [], "updated": ""}
    cs = data["complexes"]
    for c in cs:
        c["_st"] = status(c, today)

    def sort_key(c):
        st = c["_st"]
        first = (c.get("receipt") or [c.get("notice_date") or "9999"])[0]
        # 진행·예정은 가까운 날짜순, 지난 것은 최근 것부터
        return (STATUS_ORDER.index(st), first if st in ("접수중", "접수예정") else "", "" if st in ("접수중", "접수예정") else ''.join(chr(255 - ord(ch)) for ch in first))

    cs.sort(key=sort_key)
    count = {s: sum(c["_st"] == s for c in cs) for s in STATUS_ORDER}
    week = sum(1 for c in cs if c["_st"] == "접수예정" and (d(c["receipt"][0]) - today).days <= 7)

    status_btns = [("live", "진행·예정", count["접수중"] + count["접수예정"]), ("발표대기", "발표 대기", count["발표대기"]),
                   ("마감", "마감", count["마감"]), ("all", "전체", len(cs))]
    def a_btn(key, label, cls="a-btn"):
        return (f'<button class="{cls}" type="button" data-a="{e(key)}" aria-pressed="false">'
                f'{e(label)}<span class="n"></span></button>')

    known = {a for _, g in REGION_GROUPS for a in g}
    extra = sorted({c.get("area") for c in cs if c.get("area")} - known)  # 혹시 모를 새 지역명
    groups = [("빠른 선택", [a_btn("all", "전국"), a_btn("fav", "⭐ 동탄·아산", "a-btn fav")])]
    groups += [(name, [a_btn(a, a) for a in g]) for name, g in REGION_GROUPS]
    if extra:
        groups.append(("기타", [a_btn(a, a) for a in extra]))
    area_html = "\n".join(
        f'    <div class="a-group">{f"<span class=a-label>{name}</span>" if name else ""}{"".join(btns)}</div>'
        for name, btns in groups)

    updated = data.get("updated", "")
    page = PAGE.substitute(
        UPDATED=f"· {e(updated[:16].replace('T', ' '))} 수집" if updated else "",
        N_NOW=count["접수중"], N_WEEK=week, N_WAIT=count["발표대기"],
        STATUS_BTNS="\n".join(
            f'    <button class="f-btn" type="button" data-s="{k}" aria-pressed="false">{v}<span class="n">{n}</span></button>'
            for k, v, n in status_btns),
        AREA_BTNS=area_html,
        CARDS="\n".join(card_html(c, today) for c in cs),
        EMPTY="조건에 맞는 청약이 없습니다." if cs else "청약 데이터를 준비 중입니다.",
    )
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print(f"청약 페이지: {out} ({len(cs)}개 단지, 접수중 {count['접수중']} · 예정 {count['접수예정']})")


if __name__ == "__main__":
    build(*sys.argv[1:3]) if len(sys.argv) > 1 else build()
