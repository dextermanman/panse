#!/usr/bin/env python3
"""apt.json 의 단지 1개 -> Blogger 글 HTML, 전체 -> 청약 캘린더 페이지 HTML.

Blogger 테마와 섞여도 깨지지 않도록 스타일은 모두 인라인으로 씁니다.
"""
import html
from datetime import date

ACCENT = "#1a5fb4"
MUTED = "#6b7280"
LINE = "#e5e7eb"
TABLE = f"width:100%;border-collapse:collapse;font-size:14px;margin:8px 0 20px"
TH = f"text-align:left;padding:8px;border-bottom:2px solid {LINE};background:#f8fafc;white-space:nowrap"
TD = f"padding:8px;border-bottom:1px solid {LINE}"
TDR = TD + ";text-align:right;white-space:nowrap"
H2 = f"font-size:19px;margin:28px 0 8px;padding-left:10px;border-left:4px solid {ACCENT}"


def e(s):
    return html.escape(str(s or ""))


def d(s):
    """'2026-11-03' -> date."""
    try:
        return date.fromisoformat(s[:10])
    except (TypeError, ValueError):
        return None


def md(s):
    x = d(s)
    return f"{x.month}/{x.day}({'월화수목금토일'[x.weekday()]})" if x else ""


def span_txt(sp):
    if not sp:
        return ""
    return md(sp[0]) if sp[0] == sp[1] else f"{md(sp[0])} ~ {md(sp[1])}"


def won(manwon):
    """만원 단위 -> '5억 2,340만원'."""
    try:
        v = int(float(manwon))
    except (TypeError, ValueError):
        return "-"
    eok, man = divmod(v, 10000)
    if eok and man:
        return f"{eok}억 {man:,}만원"
    return f"{eok}억원" if eok else f"{man:,}만원"


def house_type(t):
    """'084.9800A' -> '84A'."""
    t = (t or "").strip()
    num = "".join(ch for ch in t if ch.isdigit() or ch == ".")
    suffix = t[len(num):] if t.startswith(num) else ""
    try:
        return f"{int(float(num))}{suffix.strip()}"
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
    if w and today < w:
        return "발표대기"
    return "마감"


STATUS_COLOR = {"접수예정": "#1a5fb4", "접수중": "#c01c28", "발표대기": "#9a6700", "마감": "#6b7280", "공고": "#6b7280"}


def badge(text, color):
    return (f'<span style="display:inline-block;padding:2px 8px;border-radius:10px;font-size:12px;'
            f'font-weight:600;color:#fff;background:{color};margin-right:4px;white-space:nowrap">{e(text)}</span>')


def short_area(c):
    a = c.get("area") or ""
    city = (c.get("city") or "").removesuffix("시").removesuffix("군").removesuffix("구")
    return f"{a} {city}".strip()


def title(c):
    first = c["receipt"][0] if c.get("receipt") else c.get("notice_date")
    when = f" ({md(first)} 접수)" if first else ""
    kind = "무순위 " if c["kind"] == "무순위" else ""
    return f"[{short_area(c)}] {c['name']} {kind}분양정보 | 청약일정·분양가{when}"


def labels(c, today):
    ls = {c.get("area"), c.get("city"), "무순위·잔여세대" if c["kind"] == "무순위" else "아파트 분양",
          (d(c["receipt"][0]).strftime("%Y년 %m월") if c.get("receipt") and d(c["receipt"][0]) else None)}
    return sorted(x for x in ls if x)


def price_table(c):
    rows = []
    for m in c.get("models", []):
        try:
            per_py = int(float(m["top_price"]) / (float(m["supply_area"]) / 3.3058))
            per_py_txt = f"{per_py:,}만원"
        except (TypeError, ValueError, ZeroDivisionError):
            per_py_txt = "-"
        rows.append(
            f'<tr><td style="{TD}"><b>{e(house_type(m["type"]))}</b></td>'
            f'<td style="{TDR}">{e(m["supply_area"])}㎡</td>'
            f'<td style="{TDR}">{e(m["supply"] or "-")}</td>'
            f'<td style="{TDR}">{e(m["special"] or "-")}</td>'
            f'<td style="{TDR}"><b>{won(m["top_price"])}</b></td>'
            f'<td style="{TDR}">{per_py_txt}</td></tr>')
    if not rows:
        return f'<p style="color:{MUTED}">주택형별 정보가 아직 공개되지 않았습니다.</p>'
    return (f'<div style="overflow-x:auto"><table style="{TABLE}"><thead><tr>'
            f'<th style="{TH}">주택형</th><th style="{TH};text-align:right">공급면적</th>'
            f'<th style="{TH};text-align:right">일반</th><th style="{TH};text-align:right">특별</th>'
            f'<th style="{TH};text-align:right">최고 분양가</th><th style="{TH};text-align:right">평당가</th>'
            f'</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'
            f'<p style="font-size:12px;color:{MUTED};margin-top:-8px">※ 주택형 = 전용면적(㎡). 평당가는 최고 분양가 ÷ 공급면적(평) 기준 추정치입니다.</p>')


def schedule_table(c, today):
    rows = []
    for label, sp in c.get("schedule", []):
        b, en = d(sp[0]), d(sp[1])
        now = b and en and b <= today <= en
        past = en and en < today
        style = TD + (";font-weight:700;color:#c01c28" if now else f";color:{MUTED}" if past else "")
        mark = " ◀ 오늘" if now else ""
        rows.append(f'<tr><td style="{style}">{e(label)}</td><td style="{style}">{span_txt(sp)}{mark}</td></tr>')
    if c.get("move_in") and len(c["move_in"]) >= 6:
        rows.append(f'<tr><td style="{TD}">입주 예정</td><td style="{TD}">{c["move_in"][:4]}년 {int(c["move_in"][4:6])}월</td></tr>')
    return f'<table style="{TABLE}"><tbody>{"".join(rows)}</tbody></table>'


def competition_table(c):
    rows = [r for r in c.get("competition", []) if r.get("rate") or r.get("requests")]
    if not rows:
        return ""
    body = "".join(
        f'<tr><td style="{TD}">{e(house_type(r["type"]))}</td><td style="{TD}">{e(r["rank"])}순위 {e(r["reside"])}</td>'
        f'<td style="{TDR}">{e(r["supply"])}</td><td style="{TDR}">{e(r["requests"])}</td>'
        f'<td style="{TDR}"><b>{e(r["rate"])}</b></td></tr>' for r in rows)
    return (f'<h2 style="{H2}">청약 경쟁률</h2><div style="overflow-x:auto"><table style="{TABLE}"><thead><tr>'
            f'<th style="{TH}">주택형</th><th style="{TH}">구분</th><th style="{TH};text-align:right">공급</th>'
            f'<th style="{TH};text-align:right">접수</th><th style="{TH};text-align:right">경쟁률</th>'
            f'</tr></thead><tbody>{body}</tbody></table></div>')


def post_html(c, today, updated=""):
    st = status(c, today)
    flags = [k for k, v in c.get("flags", {}).items() if v]
    flag_html = "".join(badge(f, "#7c3aed") for f in flags) or f'<span style="color:{MUTED}">해당 없음</span>'
    info = [
        ("위치", c.get("address")), ("공급 규모", f'{c["households"]}세대' if c.get("households") else ""),
        ("주택 구분", c.get("type_name")), ("시공사", c.get("builder")), ("시행사", c.get("developer")),
        ("모집공고일", md(c.get("notice_date"))), ("문의", c.get("phone")),
    ]
    info_rows = "".join(f'<tr><th style="{TH};width:28%">{k}</th><td style="{TD}">{e(v)}</td></tr>' for k, v in info if v)
    links = []
    if c.get("url"):
        links.append(f'<a href="{e(c["url"])}" target="_blank" rel="noopener">청약홈 모집공고 보기</a>')
    if c.get("homepage"):
        hp = c["homepage"] if c["homepage"].startswith("http") else "http://" + c["homepage"]
        links.append(f'<a href="{e(hp)}" target="_blank" rel="noopener nofollow">분양 홈페이지</a>')
    map_q = e(c.get("address", "")).replace(" ", "+")
    links.append(f'<a href="https://map.naver.com/p/search/{map_q}" target="_blank" rel="noopener">네이버 지도</a>')
    return f"""<div style="font-family:-apple-system,'Apple SD Gothic Neo','Noto Sans KR',sans-serif;line-height:1.6;color:#111">
<p>{badge(st, STATUS_COLOR[st])}{badge(c["kind"], "#374151")}{badge(short_area(c), ACCENT)}</p>
<p style="font-size:16px"><b>{e(c["name"])}</b>의 청약 일정과 주택형별 분양가를 정리했습니다.
{"청약 접수는 <b>" + span_txt(c["receipt"]) + "</b>입니다." if c.get("receipt") else ""}</p>
<h2 style="{H2}">단지 개요</h2>
<table style="{TABLE}"><tbody>{info_rows}</tbody></table>
<h2 style="{H2}">청약 일정</h2>
{schedule_table(c, today)}
<h2 style="{H2}">주택형별 분양가</h2>
{price_table(c)}
<h2 style="{H2}">규제·지구 지정</h2>
<p>{flag_html}</p>
<p style="font-size:13px;color:{MUTED}">투기과열지구·분양가상한제 여부에 따라 재당첨 제한, 전매제한, 실거주 의무가 달라집니다. 정확한 조건은 반드시 모집공고문에서 확인하세요.</p>
{competition_table(c)}
<h2 style="{H2}">바로가기</h2>
<p>{" · ".join(links)}</p>
<p style="font-size:12px;color:{MUTED};border-top:1px solid {LINE};padding-top:10px;margin-top:24px">
출처: 한국부동산원 청약홈 분양정보(공공데이터포털). {e(updated[:16].replace("T", " "))} 기준 자동 정리된 글로, 실제 청약 전 모집공고문을 반드시 확인하세요.</p>
</div>"""


def calendar_html(complexes, urls, today, updated=""):
    """접수예정/접수중/발표대기 단지를 접수일 순으로 나열한 캘린더 페이지."""
    live = [c for c in complexes if c.get("receipt") and status(c, today) in ("접수예정", "접수중", "발표대기")]
    live.sort(key=lambda c: c["receipt"][0])
    rows = []
    for c in live:
        st = status(c, today)
        name = e(c["name"])
        if urls.get(c["id"]):
            name = f'<a href="{e(urls[c["id"]])}">{name}</a>'
        top = max((float(m["top_price"]) for m in c.get("models", []) if m.get("top_price")), default=None)
        rows.append(
            f'<tr><td style="{TD}">{badge(st, STATUS_COLOR[st])}<br><b>{name}</b>'
            f'<br><span style="font-size:12px;color:{MUTED}">{e(short_area(c))} · {e(c.get("households"))}세대</span></td>'
            f'<td style="{TD};white-space:nowrap">{span_txt(c["receipt"])}</td>'
            f'<td style="{TD};white-space:nowrap">{md(c.get("winner_date"))}</td>'
            f'<td style="{TDR}">{won(top) if top else "-"}</td></tr>')
    body = "".join(rows) or f'<tr><td style="{TD}" colspan="4">예정된 청약이 없습니다.</td></tr>'
    return f"""<div style="font-family:-apple-system,'Apple SD Gothic Neo','Noto Sans KR',sans-serif;line-height:1.6">
<p>접수 예정·진행 중인 아파트 청약을 접수일 순으로 모았습니다. 단지명을 누르면 상세 분양정보로 이동합니다.</p>
<div style="overflow-x:auto"><table style="{TABLE}"><thead><tr>
<th style="{TH}">단지</th><th style="{TH}">청약 접수</th><th style="{TH}">당첨 발표</th><th style="{TH};text-align:right">최고 분양가</th>
</tr></thead><tbody>{body}</tbody></table></div>
<p style="font-size:12px;color:{MUTED}">출처: 한국부동산원 청약홈 · {e(updated[:16].replace("T", " "))} 기준 자동 갱신</p>
</div>"""
