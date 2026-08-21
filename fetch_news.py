#!/usr/bin/env python3
"""Google 뉴스 RSS -> 주제별 뉴스 JSON 수집기."""
import concurrent.futures
import json
import re
from collections import Counter, defaultdict
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

KST = timezone(timedelta(hours=9))
BASE = "https://news.google.com/rss/search?q={q}&hl=ko&gl=KR&ceid=KR:ko"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"

TOPICS = [
    # 순서 = 색 배치 순서이자 중복 제거 우선순위 (앞 주제가 기사를 먼저 가져간다).
    # 색은 dataviz 스킬 검증 팔레트 8슬롯. 이 배열 순서로 라이트/다크 모두 검증했다.
    {
        "id": "mideast", "name": "중동전쟁", "accent": "#e34948", "accent_dark": "#e66767",
        "queries": ["중동 전쟁", "이스라엘 가자", "이란 이스라엘", "중동 정세 유가"],
    },
    {
        "id": "semi", "name": "반도체", "accent": "#2a78d6", "accent_dark": "#3987e5",
        "queries": ["반도체", "HBM 메모리", "TSMC 파운드리", "삼성전자 SK하이닉스 반도체"],
    },
    {
        "id": "display", "name": "디스플레이", "accent": "#e87ba4", "accent_dark": "#d55181",
        "queries": ["디스플레이 패널", "OLED", "LG디스플레이 삼성디스플레이", "마이크로LED 디스플레이"],
    },
    {
        "id": "stock", "name": "주식", "accent": "#008300", "accent_dark": "#008300",
        "queries": ["코스피 코스닥", "뉴욕증시", "주식 시장 전망", "기업 실적 발표"],
    },
    {
        "id": "ai", "name": "AI", "accent": "#4a3aa7", "accent_dark": "#9085e9",
        "queries": ["인공지능 AI", "생성형 AI", "엔비디아 AI", "AI 데이터센터",
                    # 구글이 "전력 수요"만 보고 일반 전력 기사를 딸려 보내므로
                    # 이 두 질의는 AI·데이터센터가 제목에 있어야 통과시킨다
                    ("AI 데이터센터 전력", r"AI|인공지능|데이터센터"),
                    ("데이터센터 전력 수요", r"AI|인공지능|데이터센터")],
    },
    {
        "id": "battery", "name": "배터리·전기차", "accent": "#1baf7a", "accent_dark": "#199e70",
        "queries": ["배터리", "전기차", "이차전지", "테슬라 전기차"],
    },
    {
        "id": "econ", "name": "세계 경제", "accent": "#eb6834", "accent_dark": "#d95926",
        "queries": ["세계 경제", "미국 연준 금리", "환율 원달러", "글로벌 인플레이션",
                    "비트코인 시세 전망", "이더리움 가상자산"],
    },
    {
        "id": "stablecoin", "name": "스테이블코인", "accent": "#008d96", "accent_dark": "#14b8a6",
        "queries": ["스테이블코인", "테더 USDT USDC", "원화 스테이블코인", "스테이블코인 법안", "디지털화폐 CBDC 스테이블코인"],
    },
]

STRIP_SOURCE = re.compile(r"\s+-\s+[^-]+$")

# 기계번역/스팸성 매체
BLOCK_SOURCES = ("vietnam.vn", "노조신문", "timess.co.kr", "앱스토리", "prnewswire",
                 "뉴스와이어", "blog", "블로그", "tistory", "brunch", "cafe", "post.naver")

# 제목 노이즈: 증시 기계 기사, 지자체 행사/홍보, 광고성
BLOCK_TITLE = re.compile(
    r"(순매수|순매도|상한가|하한가|특징주|장마감|개장|급등주|테마주|주가 ?급|"
    r"경진대회|경진 대회|성료|위촉|간담회|공모전|채용|특강|박람회|설명회|시상|수상자|"
    r"MOU 체결|업무협약|기념식|출범식|세미나 개최|포럼 개최|이벤트|할인|증정|사은품|교육생 모집|수강생 모집|아카데미|워크숍|공고)"
)

# 주제별 오탐 제거 (예: 스마트폰 배터리는 이차전지 뉴스가 아님)
TOPIC_BLOCK = {
    "battery": re.compile(r"(갤럭시|아이폰|스마트폰|노트북|이어폰|보조배터리|mAh)"),
    "ai": re.compile(r"(AI ?교육 ?수강|무료 ?강의)"),
}

SOURCE_MAP = {
    "v.daum.net": "다음뉴스",
    "n.news.naver.com": "네이버뉴스",
    "네이트": "네이트뉴스",
    "edaily.co.kr": "이데일리",
    "fetv.co.kr": "FETV",
    "mk.co.kr": "매일경제",
    "hankyung.com": "한국경제",
    "yna.co.kr": "연합뉴스",
    "chosun.com": "조선일보",
    "donga.com": "동아일보",
    "khan.co.kr": "경향신문",
    "hani.co.kr": "한겨레",
    "sedaily.com": "서울경제",
    "mt.co.kr": "머니투데이",
    "etnews.com": "전자신문",
    "zdnet.co.kr": "ZDNet Korea",
    "news1.kr": "뉴스1",
    "newsis.com": "뉴시스",
    "biz.chosun.com": "조선비즈",
}

DOMAIN_RE = re.compile(r"^(www\.|v\.|m\.|n\.)?([\w-]+)\.(co\.kr|kr|com|net|org|io|news)$")


def pretty_source(src):
    s = (src or "").strip()
    if not s:
        return "Google 뉴스"
    if s in SOURCE_MAP:
        return SOURCE_MAP[s]
    m = DOMAIN_RE.match(s.lower())
    if m:
        return m.group(2).upper() if len(m.group(2)) <= 4 else m.group(2).capitalize()
    return s


STOPWORDS = {"기자", "단독", "속보", "종합", "그래픽", "포토", "영상", "인터뷰", "사설", "칼럼"}


def tokens(title):
    words = re.findall(r"[가-힣A-Za-z0-9]{2,}", title)
    return {w.lower() for w in words if w not in STOPWORDS}


def is_similar(a, b, rare=frozenset()):
    """서로 다른 매체의 같은 사건 기사 걸러내기.

    긴 제목은 겹치는 비율로, 짧은 제목은 '그 주제 안에서 희소한 단어'가
    겹치는지로 판단한다. (예: "재무차관회의" 하나만 겹쳐도 같은 사건)
    """
    if not a or not b:
        return False
    inter = a & b
    n = len(inter)
    if not n:
        return False
    ratio = n / min(len(a), len(b))
    if ratio >= 0.62 and n >= 3:
        return True
    return bool(inter & rare) and ratio >= 0.25


def fetch(url, retries=2, timeout=8):
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(1.0 * (i + 1))
    print(f"  ! 실패: {url} ({last})", file=sys.stderr)
    return None


def parse_items(xml_bytes):
    out = []
    if not xml_bytes:
        return out
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as e:
        print(f"  ! XML 파싱 실패: {e}", file=sys.stderr)
        return out
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        if not title or not link:
            continue
        src_el = item.find("source")
        source = (src_el.text or "").strip() if src_el is not None else ""
        clean = STRIP_SOURCE.sub("", title).strip() if source else title
        pub = item.findtext("pubDate") or ""
        try:
            from email.utils import parsedate_to_datetime

            dt = parsedate_to_datetime(pub).astimezone(KST)
        except Exception:  # noqa: BLE001
            dt = datetime.now(KST)
        out.append(
            {
                "title": clean or title,
                "link": link,
                "source": pretty_source(source),
                "published": dt.isoformat(),
                "ts": int(dt.timestamp()),
            }
        )
    return out


def norm(title):
    return re.sub(r"[^\w가-힣]+", "", title.lower())[:40]


# ------------------------------------------------------- 금·은 시세 / 환율
METALS_API = "https://api.gold-api.com/price/{sym}"
FX_API = "https://open.er-api.com/v6/latest/USD"          # 폴백: 하루 1회 갱신
NAVER_FX = "https://finance.naver.com/marketindex/"       # 주력: 하나은행 고시, 수시 갱신


def _fx_block(text, code):
    """네이버 금융 환율 목록에서 통화 하나를 뽑는다."""
    m = re.search(
        r'class="head ' + code + r'".*?'
        r'<span class="value">([\d,.]+)</span>.*?'
        r'<span class="change">\s*([\d,.]+)</span>.*?'
        r'<span class="blind">(상승|하락|보합)</span>',
        text, re.S)
    if not m:
        return None, None
    value = float(m.group(1).replace(",", ""))
    delta = float(m.group(2).replace(",", ""))
    way = m.group(3)
    if way == "보합" or delta == 0:
        return value, 0.0
    prev = value - delta if way == "상승" else value + delta
    if prev <= 0:
        return value, None
    pct = (value - prev) / prev * 100
    return value, round(pct, 2)


def _naver_gold_prev_close(text):
    """네이버 '국제 금'에서 전일 종가를 계산한다."""
    m = re.search(
        r'<span class="blind">국제 금</span>.*?'
        r'<span class="value">([\d,.]+)</span>.*?'
        r'<span class="change">\s*([\d,.]+)</span>.*?'
        r'<span class="blind">(상승|하락|보합)</span>',
        text, re.S)
    if not m:
        return None
    value = float(m.group(1).replace(",", ""))
    delta = float(m.group(2).replace(",", ""))
    way = m.group(3)
    if way == "보합" or delta == 0:
        return value
    return value - delta if way == "상승" else value + delta


def fetch_naver_fx():
    """하나은행 고시 환율(원/달러, 원/100엔)과 전일 대비 등락률."""
    raw = fetch(NAVER_FX, retries=2)
    if not raw:
        return None
    text = raw.decode("euc-kr", errors="replace")
    usd, usd_chg = _fx_block(text, "usd")
    jpy, jpy_chg = _fx_block(text, "jpy")
    if usd is None and jpy is None:
        print("  ! 네이버 환율 파싱 실패", file=sys.stderr)
        return None
    stamp = re.search(r'<span class="time">([\d.]+ [\d:]+)</span>', text)
    return {"usdkrw": usd, "jpykrw": jpy, "usdkrw_chg": usd_chg,
            "jpykrw_chg": jpy_chg, "fx_time": stamp.group(1) if stamp else None,
            "gold_prev_close": _naver_gold_prev_close(text)}
HISTORY = Path(__file__).with_name("market_history.json")
SERIES = ("gold", "silver", "usdkrw", "jpykrw")


def fetch_market():
    """금·은 현물(USD/온스)과 원/달러·원/100엔 환율, 그리고 24시간 등락률.

    어느 API도 등락률을 주지 않으므로 30분마다 값을 이력에 쌓아 직접 계산한다.
    """
    now_ts = int(datetime.now(KST).timestamp())
    try:
        hist = json.loads(HISTORY.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        hist = []

    out = {}
    for key, sym in (("gold", "XAU"), ("silver", "XAG")):
        raw = fetch(METALS_API.format(sym=sym), retries=2)
        if raw:
            try:
                out[key] = round(float(json.loads(raw)["price"]), 2)
            except Exception as e:  # noqa: BLE001
                print(f"  ! 시세 파싱 실패 {sym}: {e}", file=sys.stderr)

    fx = fetch_naver_fx()
    fx_chg, fx_time = {}, None
    if fx:
        for k in ("usdkrw", "jpykrw"):
            if fx.get(k) is not None:
                out[k] = fx[k]
                fx_chg[k] = fx.get(f"{k}_chg")
        fx_time = fx.get("fx_time")
    else:  # 네이버가 막히면 하루 1회 갱신 API로 폴백
        raw = fetch(FX_API, retries=2)
        if raw:
            try:
                rates = json.loads(raw)["rates"]
                krw, jpy = float(rates["KRW"]), float(rates["JPY"])
                out["usdkrw"] = round(krw, 2)
                out["jpykrw"] = round(krw / jpy * 100, 2)  # 한국은 100엔 기준으로 본다
            except Exception as e:  # noqa: BLE001
                print(f"  ! 환율 폴백 실패: {e}", file=sys.stderr)

    if not out:
        if hist:  # 이번엔 실패 -> 마지막으로 받은 값을 그대로
            last = hist[-1]
            return {**{k: last.get(k) for k in SERIES},
                    **{f"{k}_chg": None for k in SERIES}, "stale": True}
        return None

    hist.append({"ts": now_ts, **out})
    hist = [h for h in hist if h["ts"] >= now_ts - 8 * 24 * 3600]
    HISTORY.write_text(json.dumps(hist), encoding="utf-8")

    target = now_ts - 24 * 3600
    old = min((h for h in hist if h["ts"] <= target), key=lambda h: target - h["ts"], default=None)

    def chg(key):
        if not old or not out.get(key) or not old.get(key):
            return None
        return round((out[key] - old[key]) / old[key] * 100, 2)

    print(f"  금 ${out.get('gold')} · 은 ${out.get('silver')} · "
          f"달러 {out.get('usdkrw')}원 · 100엔 {out.get('jpykrw')}원")
    changes = {f"{k}_chg": (fx_chg[k] if k in fx_chg else chg(k)) for k in SERIES}
    prev_gold = (fx or {}).get("gold_prev_close")
    if prev_gold and out.get("gold"):
        # 전일 종가는 고정값이라, 실시간 금값에 적용해도 전일 대비가 정확하다
        changes["gold_chg"] = round((out["gold"] - prev_gold) / prev_gold * 100, 2)
    return {**{k: out.get(k) for k in SERIES}, **changes,
            "fx_time": fx_time, "stale": False}


def pick_balanced(items, limit):
    """검색어별로 한 건씩 돌아가며 채운 뒤 시간순으로 되돌린다.

    그냥 최신순으로 자르면 그날 화제가 큰 소재 하나가 주제를 통째로
    차지한다(예: 비트코인 급등일의 세계 경제).
    """
    groups = defaultdict(list)
    for it in items:  # items는 이미 최신순
        groups[it.get("_q", 0)].append(it)
    picked, depth = [], 0
    while len(picked) < limit:
        added = False
        for qi in sorted(groups):
            if depth < len(groups[qi]):
                picked.append(groups[qi][depth])
                added = True
                if len(picked) == limit:
                    break
        if not added:
            break
        depth += 1
    picked.sort(key=lambda x: -x["ts"])
    return [{k: v for k, v in it.items() if k != "_q"} for it in picked]


def _fetch_one_query(args):
    t_id, qi, q = args
    require = None
    if isinstance(q, tuple):
        q, require = q[0], re.compile(q[1])
    url = BASE.format(q=urllib.parse.quote(q))
    raw = fetch(url, retries=2, timeout=8)
    items = parse_items(raw)
    return t_id, qi, require, items


def collect():
    now = datetime.now(KST)
    cutoff = int((now - timedelta(days=3)).timestamp())

    # 모든 쿼리를 병렬로 수집
    query_tasks = []
    for topic in TOPICS:
        for qi, q in enumerate(topic["queries"]):
            query_tasks.append((topic["id"], qi, q))

    topic_items_map = defaultdict(list)
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        for t_id, qi, require, items in executor.map(_fetch_one_query, query_tasks):
            topic_items_map[t_id].append((qi, require, items))

    result = []
    seen_global = set()
    seen_tokens = []
    for topic in TOPICS:
        bucket = {}
        topic_block = TOPIC_BLOCK.get(topic["id"])
        for qi, require, items in topic_items_map[topic["id"]]:
            for it in items:
                if it["ts"] < cutoff:
                    continue
                if require and not require.search(it["title"]):
                    continue
                if any(b in it["source"].lower() for b in BLOCK_SOURCES):
                    continue
                if BLOCK_TITLE.search(it["title"]):
                    continue
                if topic_block and topic_block.search(it["title"]):
                    continue
                k = norm(it["title"])
                if not k or k in bucket:
                    continue
                it["_q"] = qi
                bucket[k] = it
        items = sorted(bucket.values(), key=lambda x: -x["ts"])
        # 이 주제 안에서 드물게 등장하는 단어 = 특정 사건을 가리키는 단어
        df = Counter()
        for it in items:
            df.update(tokens(it["title"]))
        rare = frozenset(w for w, c in df.items() if c <= 5 and len(w) >= 3)
        # 주제 간 중복 제거(먼저 잡은 주제 우선)
        deduped = []
        for it in items:
            k = norm(it["title"])
            if k in seen_global:
                continue
            tok = tokens(it["title"])
            if any(is_similar(tok, prev, rare) for prev in seen_tokens):
                continue
            seen_global.add(k)
            seen_tokens.append(tok)
            deduped.append(it)
        # 최근 24시간 시간대별 기사 흐름 (한 칸 = 1시간, 마지막 칸이 현재 시각)
        hour0 = now.replace(minute=0, second=0, microsecond=0)
        hist = [0] * 24
        for it in deduped:
            delta = int((hour0.timestamp() - it["ts"]) // 3600)
            if 0 <= delta < 24:
                hist[23 - delta] += 1
        fresh_1h = sum(1 for it in deduped if now.timestamp() - it["ts"] <= 3600)
        print(f"  {topic['name']}: {len(deduped)}건 (1시간 내 {fresh_1h})")
        picked = pick_balanced(deduped, 14)
        for it in deduped:
            it.pop("_q", None)
        result.append(
            {
                "id": topic["id"],
                "name": topic["name"],
                "accent": topic["accent"],
                "accent_dark": topic["accent_dark"],
                "total": len(deduped),
                "fresh_1h": fresh_1h,
                "hist24": hist,
                "items": picked,
            }
        )
    return {"updated": now.isoformat(), "updated_ts": int(now.timestamp()),
            "market": fetch_market(), "topics": result}


if __name__ == "__main__":
    print("구글 뉴스 수집 중...")
    data = collect()
    out = Path(__file__).with_name("news.json")
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    total = sum(len(t["items"]) for t in data["topics"])
    print(f"완료: 총 {total}건 -> {out}")
