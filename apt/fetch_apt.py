#!/usr/bin/env python3
"""청약홈 분양정보(공공데이터포털 API) 수집 -> apt/apt.json.

환경변수 DATA_GO_KR_KEY 에 공공데이터포털 '일반 인증키(Decoding)'가 필요합니다.
경쟁률은 별도 서비스(청약홈 청약 신청·당첨자 정보)라 승인이 안 됐으면 건너뜁니다.
"""
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

KST = timezone(timedelta(hours=9))
HERE = Path(__file__).parent
OUT = HERE / "apt.json"

DETAIL = "https://api.odcloud.kr/api/ApplyhomeInfoDetailSvc/v1/"
CMPET = "https://api.odcloud.kr/api/ApplyhomeInfoCmpetRtSvc/v1/"
LOOKBACK_DAYS = 45  # 모집공고일 기준 이만큼 과거부터 수집 (마감 후 경쟁률 반영용)

# (구분, 상세 엔드포인트, 주택형 엔드포인트)
KINDS = [
    ("APT", "getAPTLttotPblancDetail", "getAPTLttotPblancMdl"),
    ("무순위", "getRemndrLttotPblancDetail", "getRemndrLttotPblancMdl"),
]


def call(base, op, key, cond=None, page=1, per_page=100):
    q = {"page": page, "perPage": per_page, "serviceKey": key}
    for k, v in (cond or {}).items():
        q[f"cond[{k}]"] = v
    url = base + op + "?" + urllib.parse.urlencode(q)
    req = urllib.request.Request(url, headers={"User-Agent": "panse-apt/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)


def call_all(base, op, key, cond=None):
    rows, page = [], 1
    while True:
        res = call(base, op, key, cond, page)
        data = res.get("data") or []
        rows += data
        if len(data) < res.get("perPage", 100) or page >= 20:
            return rows
        page += 1


def pick(row, *names):
    for n in names:
        v = row.get(n)
        if v not in (None, "", "-"):
            return str(v).strip()
    return ""


def span(row, b, e):
    begin, end = pick(row, b), pick(row, e)
    return [begin, end or begin] if begin else None


def yn(row, name):
    return pick(row, name).upper() == "Y"


def normalize(kind, row):
    addr = pick(row, "HSSPLY_ADRES")
    parts = addr.split()
    return {
        "id": pick(row, "HOUSE_MANAGE_NO"),
        "pblanc_no": pick(row, "PBLANC_NO"),
        "kind": kind,
        "type_name": pick(row, "HOUSE_DTL_SECD_NM", "HOUSE_SECD_NM"),
        "name": pick(row, "HOUSE_NM"),
        "area": pick(row, "SUBSCRPT_AREA_CODE_NM"),
        "city": parts[1] if len(parts) > 1 else "",
        "address": addr,
        "households": pick(row, "TOT_SUPLY_HSHLDCO"),
        "notice_date": pick(row, "RCRIT_PBLANC_DE"),
        "receipt": span(row, "RCEPT_BGNDE", "RCEPT_ENDDE") or span(row, "SUBSCRPT_RCEPT_BGNDE", "SUBSCRPT_RCEPT_ENDDE"),
        "schedule": [s for s in [
            ("특별공급", span(row, "SPSPLY_RCEPT_BGNDE", "SPSPLY_RCEPT_ENDDE")),
            ("1순위 해당지역", span(row, "GNRL_RNK1_CRSPAREA_RCPTDE", "GNRL_RNK1_CRSPAREA_ENDDE")),
            ("1순위 경기", span(row, "GNRL_RNK1_ETC_GG_RCPTDE", "GNRL_RNK1_ETC_GG_ENDDE")),
            ("1순위 기타지역", span(row, "GNRL_RNK1_ETC_AREA_RCPTDE", "GNRL_RNK1_ETC_AREA_ENDDE")),
            ("2순위 해당지역", span(row, "GNRL_RNK2_CRSPAREA_RCPTDE", "GNRL_RNK2_CRSPAREA_ENDDE")),
            ("2순위 경기", span(row, "GNRL_RNK2_ETC_GG_RCPTDE", "GNRL_RNK2_ETC_GG_ENDDE")),
            ("2순위 기타지역", span(row, "GNRL_RNK2_ETC_AREA_RCPTDE", "GNRL_RNK2_ETC_AREA_ENDDE")),
            ("일반공급 접수", span(row, "GNRL_RCEPT_BGNDE", "GNRL_RCEPT_ENDDE")),
            ("청약 접수", span(row, "SUBSCRPT_RCEPT_BGNDE", "SUBSCRPT_RCEPT_ENDDE")),
            ("당첨자 발표", span(row, "PRZWNER_PRESNATN_DE", "PRZWNER_PRESNATN_DE")),
            ("계약", span(row, "CNTRCT_CNCLS_BGNDE", "CNTRCT_CNCLS_ENDDE")),
        ] if s[1]],
        "winner_date": pick(row, "PRZWNER_PRESNATN_DE"),
        "move_in": pick(row, "MVN_PREARNGE_YM"),
        "builder": pick(row, "CNSTRCT_ENTRPS_NM"),
        "developer": pick(row, "BSNS_MBY_NM"),
        "phone": pick(row, "MDHS_TELNO"),
        "homepage": pick(row, "HMPG_ADRES"),
        "url": pick(row, "PBLANC_URL"),
        "flags": {
            "투기과열지구": yn(row, "SPECLT_RDN_EARTH_AT"),
            "조정대상지역": yn(row, "MDAT_TRGET_AREA_SECD"),
            "분양가상한제": yn(row, "PARCPRC_ULS_AT"),
            "정비사업": yn(row, "IMPRMN_BSNS_AT"),
            "공공주택지구": yn(row, "PUBLIC_HOUSE_EARTH_AT"),
            "대규모택지": yn(row, "LRSCL_BLDLND_AT"),
        },
        "models": [],
        "competition": [],
    }


def norm_model(row):
    return {
        "type": pick(row, "HOUSE_TY"),
        "supply_area": pick(row, "SUPLY_AR"),
        "supply": pick(row, "SUPLY_HSHLDCO"),
        "special": pick(row, "SPSPLY_HSHLDCO"),
        "top_price": pick(row, "LTTOT_TOP_AMOUNT"),  # 만원
    }


def norm_cmpet(row):
    return {
        "type": pick(row, "HOUSE_TY"),
        "rank": pick(row, "SUBSCRPT_RANK_CODE"),
        "reside": pick(row, "RESIDE_SENM", "RESIDE_SECD_NM"),
        "supply": pick(row, "SUPLY_HSHLDCO"),
        "requests": pick(row, "REQ_CNT"),
        "rate": pick(row, "CMPET_RATE"),
    }


def main():
    key = os.environ.get("DATA_GO_KR_KEY", "").strip()
    if not key:
        print("DATA_GO_KR_KEY 가 없어 수집을 건너뜁니다.")
        return
    since = (datetime.now(KST) - timedelta(days=LOOKBACK_DAYS)).strftime("%Y-%m-%d")
    complexes = []
    for kind, op_detail, op_model in KINDS:
        try:
            rows = call_all(DETAIL, op_detail, key, {"RCRIT_PBLANC_DE::GTE": since})
        except Exception as e:  # noqa: BLE001
            print(f"[{kind}] 상세 조회 실패: {e}")
            continue
        print(f"[{kind}] 공고 {len(rows)}건")
        for row in rows:
            c = normalize(kind, row)
            if not c["id"]:
                continue
            try:
                models = call_all(DETAIL, op_model, key, {"HOUSE_MANAGE_NO::EQ": c["id"]})
                c["models"] = [norm_model(m) for m in models if pick(m, "PBLANC_NO") in ("", c["pblanc_no"])]
            except Exception as e:  # noqa: BLE001
                print(f"  주택형 조회 실패 {c['name']}: {e}")
            complexes.append(c)

    cmpet_ok = True
    for c in complexes:
        if not cmpet_ok or c["kind"] != "APT":
            continue
        try:
            rows = call_all(CMPET, "getAPTLttotPblancCmpet", key, {"HOUSE_MANAGE_NO::EQ": c["id"]})
            c["competition"] = [norm_cmpet(r) for r in rows]
        except Exception as e:  # noqa: BLE001
            print(f"경쟁률 조회 불가 — 건너뜀 ({e})")
            cmpet_ok = False

    complexes.sort(key=lambda c: (c["receipt"] or [c["notice_date"]])[0], reverse=True)
    OUT.write_text(json.dumps({
        "updated": datetime.now(KST).isoformat(timespec="minutes"),
        "complexes": complexes,
    }, ensure_ascii=False, indent=1))
    print(f"저장: {OUT} ({len(complexes)}개 단지)")


if __name__ == "__main__":
    main()
