"""공고 정보(민영/국민, 규제지역, 면적, 지역)로 청약 자격 요약 HTML을 만든다.

주택공급규칙(2025년 기준)의 일반 원칙을 요약한 것이다. 공고마다 예외가 있으니
화면에는 항상 '모집공고문 우선' 안내를 붙인다.
"""
import html

METRO = {"서울", "경기", "인천"}
BIG_CITY = {"대구", "인천", "광주", "대전", "울산"}

# 민영주택 청약 예치금(만원): 전용면적 상한 -> (서울·부산, 기타 광역시, 기타 시·군)
DEPOSIT = [(85, (300, 250, 200)), (102, (600, 400, 300)), (135, (1000, 700, 400)), (9999, (1500, 1000, 500))]
DEPOSIT_LABEL = ["85㎡ 이하", "102㎡ 이하", "135㎡ 이하", "135㎡ 초과"]

SPECIAL_RULES = {
    "다자녀": "미성년 자녀 2명 이상(태아·입양 포함), 무주택 세대구성원",
    "신혼부부": "혼인 7년 이내(예비부부·한부모 포함), 무주택, 소득·자산 기준 충족",
    "생애최초": "세대 전원 주택 소유 이력 없음, 소득세 5년 이상 납부, 소득 기준 충족",
    "신생아": "공고일 기준 2년 이내 출산(임신·입양 포함), 무주택, 소득 기준 충족",
    "청년": "만 19~39세 미혼 무주택자, 소득·자산 기준 (공공분양 위주)",
    "노부모부양": "만 65세 이상 직계존속을 3년 이상 부양한 무주택 세대주, 1순위 요건 충족",
    "기관추천": "국가유공자·장애인·중소기업 근로자 등 해당 기관의 추천을 받은 자",
    "이전기관": "지방 이전 공공기관 종사자",
    "기타": "모집공고문 참조",
}


def e(s):
    return html.escape(str(s or ""))


def _area_m2(model):
    """'084.9916A' -> 84.99."""
    t = model.get("type") or ""
    num = "".join(ch for ch in t if ch.isdigit() or ch == ".")
    try:
        return float(num)
    except ValueError:
        return None


def _bucket(m2):
    return next(i for i, (cap, _) in enumerate(DEPOSIT) if m2 <= cap)


def _tier(area):
    return 0 if area in ("서울", "부산") else 1 if area in BIG_CITY else 2


def _row(k, v):
    return f"<tr><th>{k}</th><td>{v}</td></tr>"


def _select_ratio(flags, sizes):
    """민영주택 가점제/추첨제 비율 — 공급 면적대만 보여준다."""
    spec, adj = flags.get("투기과열지구"), flags.get("조정대상지역")
    small = any(s <= 60 for s in sizes)
    mid = any(60 < s <= 85 for s in sizes)
    big = any(s > 85 for s in sizes)
    out = []
    if spec or adj:
        if small:
            out.append("60㎡ 이하: 가점 40% · 추첨 60%")
        if mid:
            out.append("60~85㎡: 가점 70% · 추첨 30%")
        if big:
            out.append("85㎡ 초과: " + ("가점 80% · 추첨 20%" if spec else "가점 30% · 추첨 70%"))
    else:
        if small or mid:
            out.append("85㎡ 이하: 가점 40% 이하(지자체 결정) · 나머지 추첨")
        if big:
            out.append("85㎡ 초과: 추첨 100%")
    out.append('<span class="muted">추첨 물량은 무주택자에게 75% 이상 우선 배정, 나머지는 무주택자·1주택자가 함께 경쟁</span>')
    return "<br>".join(out)


def _residence(c):
    names = [s[0] for s in c.get("schedule", [])]
    area, flags = c.get("area"), c.get("flags", {})
    if any("경기" in n for n in names):
        txt = "경기 대규모 택지개발지구 배정: 해당 시·군 거주자 30% → 경기도 20% → 서울·인천 등 수도권 50% 순으로 공급"
    elif area == "인천" and flags.get("대규모택지"):
        txt = "인천 대규모 택지개발지구 배정: 인천 거주자 50% → 서울·경기 등 수도권 50%"
    elif area == "서울":
        txt = "서울 거주자 우선 공급 후 남는 물량을 경기·인천 거주자에게 공급"
    else:
        txt = f"{e(area)} 해당지역 거주자 우선 공급, 남는 물량은 기타지역 거주자에게 공급"
    if flags.get("투기과열지구") or flags.get("조정대상지역"):
        txt += '<br><span class="muted">규제지역은 해당지역 우선공급에 일정 거주기간(통상 1~2년) 요건이 붙을 수 있음</span>'
    return txt


def _resale(c):
    flags, area = c.get("flags", {}), c.get("area")
    regulated = flags.get("투기과열지구") or flags.get("조정대상지역")
    public = flags.get("공공주택지구")
    if area in METRO:
        resale = "3년" if regulated or public else "6개월 (과밀억제권역은 1년)"
    else:
        resale = "1년" if regulated or public else "6개월" if area in BIG_CITY else "없음"
    if flags.get("분양가상한제") and area in METRO:
        live = "있음: 최대 5년(최초 입주 가능일로부터 3년 이내에 시작하면 됨)"
    else:
        live = "없음"
    return resale, live


def _rewin(c):
    flags = c.get("flags", {})
    if flags.get("투기과열지구") or flags.get("분양가상한제"):
        return "10년 (투기과열지구·분양가상한제 주택)"
    if flags.get("조정대상지역"):
        return "7년 (조정대상지역)"
    return "일반 민영주택은 없음 (특별공급·규제지역 주택 당첨 이력은 별도 제한)"


def _special_table(c):
    total = {}
    for m in c.get("models", []):
        for k, n in (m.get("special_by") or {}).items():
            try:
                total[k] = total.get(k, 0) + int(n)
            except ValueError:
                pass
    if not total:
        return ""
    rows = "".join(
        f'<tr><th>{e(k)}</th><td class="r">{n:,}</td><td>{e(SPECIAL_RULES.get(k, ""))}</td></tr>'
        for k, n in sorted(total.items(), key=lambda kv: -kv[1]))
    return ('<h5>특별공급 유형별 물량·자격</h5><div class="tbl-wrap"><table class="tbl"><thead><tr>'
            '<th>유형</th><th class="r">세대</th><th>주요 자격</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div>'
            '<p class="note">특별공급은 평생 1회만 당첨될 수 있고, 무주택 세대구성원이어야 합니다. 소득·자산 기준은 매년 바뀌므로 공고문 표를 확인하세요.</p>')


def eligibility_html(c):
    flags = c.get("flags", {})
    area = c.get("area")
    regulated = flags.get("투기과열지구") or flags.get("조정대상지역")
    tname = c.get("type_name") or ""

    if c.get("kind") == "무순위":
        if "재공급" in tname:
            who = "공고일 기준 해당 지역에 거주하는 무주택 세대구성원 (계약취소 주택 재공급)"
        else:
            who = "성년인 무주택 세대구성원. 거주지역 요건은 공고마다 다름 (2025년 무순위 제도 개편 이후 기준)"
        rows = [
            _row("공급 유형", f"{e(tname)} · 청약통장 없이 신청 가능"),
            _row("신청 자격", who),
            _row("당첨자 선정", "추첨"),
            _row("재당첨 제한", _rewin(c) if regulated or flags.get("분양가상한제") else "공고문 확인"),
        ]
        return ('<h4>청약 자격</h4><table class="kv">' + "".join(rows) + "</table>"
                '<p class="note">무순위·재공급은 공고별로 거주지·무주택 요건이 달라 반드시 모집공고문을 확인하세요.</p>')

    sizes = sorted({s for s in (_area_m2(m) for m in c.get("models", [])) if s})
    period = "24개월" if regulated else "12개월" if area in METRO else "6개월"
    rows = []
    if tname == "국민":
        count = "24회" if regulated else "12회" if area in METRO else "6회"
        rows.append(_row("공급 유형", "국민주택 (공공분양)"))
        rows.append(_row("1순위 통장", f"주택청약종합저축 가입 {period} 이상 · 월 납입 {count} 이상"))
        rows.append(_row("세대·주택", "무주택 세대구성원" + (" · 1순위는 세대주만" if regulated else "")))
        rows.append(_row("당첨자 선정", "40㎡ 초과: 납입 인정금액 많은 순 · 40㎡ 이하: 납입 횟수 많은 순"))
    else:
        tier = _tier(area)
        buckets = sorted({_bucket(s) for s in sizes}) or [0]
        dep = " · ".join(f"{DEPOSIT_LABEL[b]} {DEPOSIT[b][1][tier]:,}만원" for b in buckets)
        rows.append(_row("공급 유형", "민영주택"))
        rows.append(_row("1순위 통장", f"가입 {period} 이상 + 지역별 예치금<br><b>{dep}</b>"
                         f'<br><span class="muted">예치금 기준 지역: {e(["서울·부산", "기타 광역시", "기타 시·군"][tier])} (모집공고일까지 납입)</span>'))
        if regulated:
            rows.append(_row("세대·주택", "1순위는 세대주만 가능 · 5년 이내 세대원 당첨 이력이 있으면 1순위 제외 · 2주택 이상 소유 세대는 1순위 제외"))
        else:
            rows.append(_row("세대·주택", "세대주·세대원 모두 1순위 가능, 유주택자도 신청 가능 (가점제는 무주택 기간 점수가 커서 무주택자에게 유리)"))
        rows.append(_row("당첨자 선정", _select_ratio(flags, sizes)))
    rows.append(_row("거주지 우선", _residence(c)))
    resale, live = _resale(c)
    rows.append(_row("재당첨 제한", _rewin(c)))
    rows.append(_row("전매 제한", resale))
    rows.append(_row("실거주 의무", live))
    return ('<h4>청약 자격</h4><table class="kv">' + "".join(rows) + "</table>" + _special_table(c) +
            '<p class="note">주택공급규칙(2025년 기준)에 따라 공고 정보로 자동 요약한 내용입니다. 실제 자격과 예외는 모집공고문이 우선합니다.</p>')
