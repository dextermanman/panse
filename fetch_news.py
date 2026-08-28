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
        "id": "mideast", "name": "중동전쟁", "accent": "#E11D48", "accent_dark": "#E11D48",
        "queries": ["중동 전쟁", "이스라엘 가자", "이란 이스라엘", "중동 정세 유가"],
    },
    {
        "id": "semi", "name": "반도체", "accent": "#2563EB", "accent_dark": "#2563EB",
        "queries": ["반도체", "HBM 메모리", "TSMC 파운드리", "삼성전자 SK하이닉스 반도체"],
    },
    {
        "id": "display", "name": "디스플레이", "accent": "#DB2777", "accent_dark": "#DB2777",
        "queries": ["디스플레이 패널", "OLED", "LG디스플레이 삼성디스플레이", "마이크로LED 디스플레이"],
    },
    {
        "id": "stock", "name": "주식", "accent": "#059669", "accent_dark": "#059669",
        "queries": ["코스피 코스닥", "뉴욕증시", "주식 시장 전망", "기업 실적 발표"],
    },
    {
        "id": "ai", "name": "AI", "accent": "#7C3AED", "accent_dark": "#7C3AED",
        "queries": ["인공지능 AI", "생성형 AI", "엔비디아 AI", "AI 데이터센터",
                    ("AI 데이터센터 전력", r"AI|인공지능|데이터센터"),
                    ("데이터센터 전력 수요", r"AI|인공지능|데이터센터")],
    },
    {
        "id": "battery", "name": "배터리·전기차", "accent": "#0D9488", "accent_dark": "#0D9488",
        "queries": ["배터리", "전기차", "이차전지", "테슬라 전기차"],
    },
    {
        "id": "econ", "name": "세계 경제", "accent": "#EA580C", "accent_dark": "#EA580C",
        "queries": ["세계 경제", "미국 연준 금리", "환율 원달러", "글로벌 인플레이션",
                    "비트코인 시세 전망", "이더리움 가상자산"],
    },
    {
        "id": "stablecoin", "name": "스테이블코인", "accent": "#0891B2", "accent_dark": "#0891B2",
        "queries": ["스테이블코인", "테더 USDT USDC", "원화 스테이블코인", "스테이블코인 법안", "디지털화폐 CBDC 스테이블코인"],
    },
    {
        "id": "realestate", "name": "부동산", "accent": "#B45309", "accent_dark": "#D97706",
        "queries": ["아파트 매매 전세 시세", "부동산 시장 전망 정책", "부동산 청약 분양가", "재건축 재개발 부동산", "주택담보대출 금리 부동산"],
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
    r"MOU 체결|업무협약|기념식|출범식|세미나 개최|포럼 개최|이벤트|할인|증정|사은품|교육생 모집|수강생 모집|아카데미|워크숍|공고|고래사냥|내일장|오늘장|추천주|유망주|관심종목|리딩방|종목 추천|종목은|활용교육|교육 실시|수료식|> ?뉴스$|> ?보도자료)"
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


# 글자 2-gram 포함도가 이 값을 넘으면 같은 사건으로 본다.
# 실제 수집분으로 재본 결과 0.45 아래부터 서로 다른 기사가 섞이기 시작한다.
SIM_THRESHOLD = 0.45


# 신문 제목의 한자 약칭. 매체마다 "中"과 "중국"을 섞어 써서 같은 사건이 갈린다.
HANJA_ABBR = {"中": "중국", "美": "미국", "日": "일본", "韓": "한국", "北": "북한",
              "與": "여당", "野": "야당", "英": "영국", "獨": "독일", "佛": "프랑스"}


def shingles(title):
    """한국어 제목 비교용 글자 2-gram.

    어절 단위 비교는 매체마다 표현이 조금만 달라도 같은 사건을 놓친다.
    (예: "머스크가 고집한 '매립형 손잡이'…테슬라, 中서 300만대 리콜" 과
         "\"매립형 손잡이가 화근\"…테슬라, 중국서 300만대 리콜")
    """
    t = title
    for k, v in HANJA_ABBR.items():
        t = t.replace(k, v)
    # "300만 대"와 "298만대"처럼 수치만 다른 같은 사건을 묶기 위해 숫자를 지운다
    t = re.sub(r"\d[\d,.]*", "#", t)
    t = re.sub(r"[^가-힣A-Za-z0-9#]", "", t)
    return {t[i:i + 2] for i in range(len(t) - 1)}


def same_story(a, b):
    """두 제목의 2-gram 포함도로 같은 사건인지 판단."""
    if not a or not b:
        return False
    return len(a & b) / min(len(a), len(b)) >= SIM_THRESHOLD


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
        # 구글 뉴스는 " - 매체명"을 붙이는데, 간혹 두 번 붙는다
        # (예: "... - 조선비즈 - Chosunbiz"). 짧은 꼬리만 최대 두 번 잘라낸다.
        clean = title
        for _ in range(2):
            m = STRIP_SOURCE.search(clean)
            if not m or len(m.group(0)) > 27:
                break
            clean = STRIP_SOURCE.sub("", clean).strip()
        # 아래 검사는 매체명을 걷어낸 뒤에 해야 한다
        if len(re.sub(r"\s", "", clean)) < 9:
            continue  # "명확성 강화법 강화" 같은 조각 제목
        if re.search(r"\(\d{6}\)\s*$", clean):
            continue  # "SK하이닉스(000660)" — 기사가 아니라 종목 시세 페이지
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
def fetch_metals():
    """금(Gold), 은(Silver) 선물/현물 시세 (USD/oz) 및 전일 대비 변동률 (Yahoo Finance + Naver Finance)."""
    gold, gold_chg = None, None
    silver, silver_chg = None, None

    # 1. Yahoo Finance (GC=F: Gold, SI=F: Silver)
    for sym, key in (("GC=F", "gold"), ("SI=F", "silver")):
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=4) as res:
                data = json.loads(res.read().decode())
                meta = data["chart"]["result"][0]["meta"]
                price = meta["regularMarketPrice"]
                prev = meta.get("chartPreviousClose") or meta.get("previousClose") or price
                chg = (price - prev) / prev * 100
                if key == "gold":
                    gold, gold_chg = round(price, 2), round(chg, 2)
                else:
                    silver, silver_chg = round(price, 2), round(chg, 2)
        except Exception:
            pass

    # 2. Naver Finance 폴백 (국제 금)
    if gold is None:
        try:
            req = urllib.request.Request("https://finance.naver.com/marketindex/", headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=4) as res:
                raw = res.read().decode("euc-kr", errors="ignore")
                m = re.search(r'class="head gold_inter".*?<span class="value">([\d,.]+)</span>.*?<span class="change">\s*([\d,.]+)\s*</span>.*?<span class="blind">(상승|하락|보합)</span>', raw, re.DOTALL)
                if m:
                    val = float(m.group(1).replace(",", ""))
                    delta = float(m.group(2).replace(",", ""))
                    way = m.group(3)
                    prev = val - delta if way == "상승" else (val + delta if way == "하락" else val)
                    gold = round(val, 2)
                    gold_chg = round((val - prev) / prev * 100, 2)
        except Exception:
            pass

    return {"gold": gold, "gold_chg": gold_chg, "silver": silver, "silver_chg": silver_chg}


HISTORY = Path(__file__).with_name("market_history.json")
SERIES = ("gold", "silver", "btc", "usdkrw", "jpykrw")


def fetch_market():
    """금·은·비트코인(USD)과 원/달러·원/100엔 환율, 그리고 24시간 등락률."""
    now_ts = int(datetime.now(KST).timestamp())
    try:
        hist = json.loads(HISTORY.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        hist = []

    out = {}
    metals = fetch_metals()
    if metals.get("gold") is not None:
        out["gold"] = metals["gold"]
    if metals.get("silver") is not None:
        out["silver"] = metals["silver"]

    # 비트코인: CoinGecko가 24시간 변동률까지 주므로 우선 사용하고,
    # 실패하면 Coinbase 현물가(변동률 없음)로 폴백한다.
    btc_chg = None
    cg = fetch("https://api.coingecko.com/api/v3/simple/price"
               "?ids=bitcoin&vs_currencies=usd&include_24hr_change=true", retries=2, timeout=8)
    if cg:
        try:
            b = json.loads(cg)["bitcoin"]
            out["btc"] = round(float(b["usd"]), 0)
            if b.get("usd_24h_change") is not None:
                btc_chg = round(float(b["usd_24h_change"]), 2)
        except Exception as e:  # noqa: BLE001
            print(f"  ! 비트코인 파싱 실패 (CoinGecko): {e}", file=sys.stderr)
    if not out.get("btc"):
        btc_raw = fetch("https://api.coinbase.com/v2/prices/BTC-USD/spot", retries=2, timeout=6)
        if btc_raw:
            try:
                out["btc"] = round(float(json.loads(btc_raw)["data"]["amount"]), 0)
            except Exception as e:  # noqa: BLE001
                print(f"  ! 비트코인 파싱 실패 (Coinbase): {e}", file=sys.stderr)

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

    # 24시간 전 표본이 있으면 그것을, 아직 안 찼으면 가장 오래된 표본을 쓴다.
    # 실제 비교 구간은 window_h로 알려 화면 툴팁에 그대로 표시한다.
    target = now_ts - 24 * 3600
    old = min((h for h in hist if h["ts"] <= target), key=lambda h: target - h["ts"], default=None)
    if old is None and hist:
        old = hist[0]
    window_h = round((now_ts - old["ts"]) / 3600) if old else None

    def chg(key):
        # 구간이 너무 짧으면 등락률이 잡음이라 표시하지 않는다
        if not old or not out.get(key) or not old.get(key) or (window_h or 0) < 6:
            return None
        return round((out[key] - old[key]) / old[key] * 100, 2)

    print(f"  금 ${out.get('gold')} · 은 ${out.get('silver')} · 비트코인 ${out.get('btc')} · "
          f"달러 {out.get('usdkrw')}원 · 100엔 {out.get('jpykrw')}원")
    changes = {f"{k}_chg": (fx_chg[k] if k in fx_chg else chg(k)) for k in SERIES}
    if metals.get("gold_chg") is not None:
        changes["gold_chg"] = metals["gold_chg"]
    if metals.get("silver_chg") is not None:
        changes["silver_chg"] = metals["silver_chg"]
    if btc_chg is not None:
        changes["btc_chg"] = btc_chg
    return {**{k: out.get(k) for k in SERIES}, **changes,
            "fx_time": fx_time, "window_h": window_h, "stale": False}


def fetch_popular_domestic():
    """네이버 증권 실시간 검색 상위 인기 종목 TOP 10."""
    req = urllib.request.Request(
        "https://finance.naver.com/sise/lastsearch2.naver",
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as res:
            raw = res.read().decode("euc-kr", errors="ignore")
            tr_matches = re.findall(
                r"<tr>\s*<td class=\"no\">(\d+)</td>\s*<td><a href=\"/item/main\.naver\?code=(\d+)\" class=\"tltle\">(.*?)</a></td>.*?<td class=\"number\">([0-9,]+)</td>\s*<td class=\"number\">.*?</td>\s*<td class=\"number\">\s*<span class=\"tah p11 (nv01|red02|red01|nv02|)\">\s*([+\-0-9.,%]+)\s*</span>",
                raw, re.DOTALL
            )
            result = []
            for rank, code, name, price, color, chg in tr_matches[:10]:
                is_up = "red" in color or "+" in chg
                is_down = "nv" in color or "-" in chg
                chg_clean = chg.strip().replace("%", "")
                try:
                    chg_val = float(chg_clean)
                    chg_str = f"{chg_val:+.2f}%"
                except Exception:
                    chg_str = chg
                result.append({
                    "rank": int(rank),
                    "code": code,
                    "name": name.strip(),
                    "price": price.strip() + "원",
                    "chg": chg_str,
                    "is_up": is_up,
                    "is_down": is_down,
                    "link": f"https://finance.naver.com/item/main.naver?code={code}"
                })
            return result
    except Exception as e:
        print(f"  ! 국내 인기 종목 수집 실패: {e}", file=sys.stderr)
        return []


def fetch_popular_overseas():
    """해외 주요 빅테크 및 핫 종목 TOP 10."""
    US_TOP = [
        ("NVDA", "엔비디아"),
        ("TSLA", "테슬라"),
        ("AAPL", "애플"),
        ("MSFT", "마이크로소프트"),
        ("GOOGL", "알파벳"),
        ("AMZN", "아마존"),
        ("META", "메타"),
        ("PLTR", "팔란티어"),
        ("AMD", "AMD"),
        ("COIN", "코인베이스"),
    ]
    result = []
    for idx, (sym, name) in enumerate(US_TOP, 1):
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=4) as res:
                data = json.loads(res.read().decode("utf-8"))
                meta = data["chart"]["result"][0]["meta"]
                price = meta["regularMarketPrice"]
                prev = meta.get("chartPreviousClose") or meta.get("previousClose") or price
                chg = (price - prev) / prev * 100
                result.append({
                    "rank": idx,
                    "code": sym,
                    "name": f"{name} ({sym})",
                    "price": f"${price:,.2f}",
                    "chg": f"{chg:+.2f}%",
                    "is_up": chg > 0,
                    "is_down": chg < 0,
                    "link": f"https://finance.yahoo.com/quote/{sym}"
                })
        except Exception:
            pass
    return result


def fetch_popular_stocks():
    return {
        "domestic": fetch_popular_domestic(),
        "overseas": fetch_popular_overseas(),
    }


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
    seen_shingles = []
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
            sg = shingles(it["title"])
            if any(same_story(sg, prev) for prev in seen_shingles):
                continue
            seen_global.add(k)
            seen_tokens.append(tok)
            seen_shingles.append(sg)
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
    stocks = fetch_popular_stocks()
    return {"updated": now.isoformat(), "updated_ts": int(now.timestamp()),
            "market": fetch_market(), "popular_stocks": stocks, "topics": result}


if __name__ == "__main__":
    print("구글 뉴스 및 인기 종목 수집 중...")
    data = collect()
    out = Path(__file__).with_name("news.json")
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    total = sum(len(t["items"]) for t in data["topics"])
    print(f"완료: 총 {total}건 -> {out}")
