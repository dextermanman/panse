#!/usr/bin/env python3
"""공공데이터포털 한국교통안전공단 주차정보 API -> 실시간 공영주차장 잔여 현황."""
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

KST = timezone(timedelta(hours=9))

PARKING_API = "https://apis.data.go.kr/B553881/Parking_v1/PrkSttusInfo_v1"

# 관심 지역 시군구 코드 (아산·화성·평택·천안·서울·수원)
REGIONS = [
    {"sidoCd": "44", "sigunguCd": "44200", "name": "충남 아산시"},
    {"sidoCd": "41", "sigunguCd": "41590", "name": "경기 화성시"},
    {"sidoCd": "41", "sigunguCd": "41220", "name": "경기 평택시"},
    {"sidoCd": "44", "sigunguCd": "44130", "name": "충남 천안시"},
]

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"


def _api_key():
    return os.environ.get("PARKING_API_KEY", "").strip()


def _fetch_json(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        print(f"  ! 주차 API 호출 실패: {e}", file=sys.stderr)
        return None


def fetch_region(region, api_key, num_of_rows=200):
    params = urllib.parse.urlencode({
        "serviceKey": api_key,
        "pageNo": "1",
        "numOfRows": str(num_of_rows),
        "format": "2",
        "sidoCd": region["sidoCd"],
        "sigunguCd": region["sigunguCd"],
    })
    url = f"{PARKING_API}?{params}"
    data = _fetch_json(url)
    if not data:
        return []

    items = []
    try:
        body = data.get("response", {}).get("body", {})
        raw_items = body.get("items", [])
        if isinstance(raw_items, dict):
            raw_items = raw_items.get("item", [])
        if isinstance(raw_items, dict):
            raw_items = [raw_items]
    except Exception as e:
        print(f"  ! 주차 응답 파싱 실패 ({region['name']}): {e}", file=sys.stderr)
        return []

    for it in raw_items:
        name = (it.get("pkltNm") or it.get("PKLT_NM")
                or it.get("prkplceNm") or "").strip()
        addr = (it.get("addr") or it.get("ADDR")
                or it.get("rdnmadr") or it.get("lnmadr") or "").strip()
        total = _int(it.get("tpkct") or it.get("TPKCT")
                     or it.get("prkcmprt") or 0)
        current = _int(it.get("nowPrkVhclCnt") or it.get("NOW_PRK_VHCL_CNT")
                       or it.get("curParking") or 0)
        oper_type = (it.get("operSeNm") or it.get("OPER_SE_NM")
                     or it.get("prkplceSe") or "").strip()
        pay = (it.get("payYnNm") or it.get("PAY_YN_NM")
               or it.get("parkingchrgeInfo") or "").strip()
        lat = _float(it.get("lat") or it.get("latitude") or 0)
        lng = _float(it.get("lot") or it.get("lng")
                     or it.get("longitude") or 0)
        basic_fee = _int(it.get("bscPrkCrg") or it.get("BSC_PRK_CRG")
                         or it.get("basicCharge") or 0)
        basic_min = _int(it.get("bscPrkHr") or it.get("BSC_PRK_HR")
                         or it.get("basicTime") or 0)

        if not name or total <= 0:
            continue

        available = max(total - current, 0)
        pct = round(available / total * 100) if total > 0 else 0

        items.append({
            "name": name,
            "addr": addr,
            "region": region["name"],
            "total": total,
            "current": current,
            "available": available,
            "pct": pct,
            "oper_type": oper_type,
            "pay": pay,
            "lat": lat,
            "lng": lng,
            "basic_fee": basic_fee,
            "basic_min": basic_min,
        })

    return items


def _int(v):
    try:
        return int(v)
    except (ValueError, TypeError):
        return 0


def _float(v):
    try:
        return float(v)
    except (ValueError, TypeError):
        return 0.0


def fetch_parking():
    api_key = _api_key()
    if not api_key:
        print("  주차 API 키 미설정 (PARKING_API_KEY) — 건너뜀", file=sys.stderr)
        return None

    now = datetime.now(KST)
    all_items = []
    for region in REGIONS:
        items = fetch_region(region, api_key)
        print(f"  주차 {region['name']}: {len(items)}개소")
        all_items.extend(items)
        time.sleep(0.3)

    if not all_items:
        return None

    public_only = [it for it in all_items if "공영" in it.get("oper_type", "")]
    target = public_only if public_only else all_items

    target.sort(key=lambda x: x["available"], reverse=True)

    by_region = {}
    for it in target:
        r = it["region"]
        if r not in by_region:
            by_region[r] = []
        by_region[r].append(it)

    summary = []
    for region in REGIONS:
        rname = region["name"]
        lots = by_region.get(rname, [])
        if not lots:
            continue
        total_cap = sum(l["total"] for l in lots)
        total_cur = sum(l["current"] for l in lots)
        total_avail = sum(l["available"] for l in lots)
        pct = round(total_avail / total_cap * 100) if total_cap > 0 else 0
        summary.append({
            "region": rname,
            "lot_count": len(lots),
            "total_capacity": total_cap,
            "total_parked": total_cur,
            "total_available": total_avail,
            "availability_pct": pct,
            "top_available": lots[:5],
        })

    return {
        "updated": now.isoformat(),
        "updated_ts": int(now.timestamp()),
        "regions": summary,
        "total_lots": len(target),
        "all_lots": target[:50],
    }


if __name__ == "__main__":
    print("공영주차장 실시간 현황 수집 중...")
    result = fetch_parking()
    if result:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print(f"\n완료: {result['total_lots']}개소 수집")
    else:
        print("데이터 없음 (API 키 확인 필요)")
