#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
12간지 띠별 오늘의 재물·투자 운세 생성 모듈
- 매일 자정(KST)을 기준으로 일관되고 깊이 있는 사주·재물 명리 운세를 생성합니다.
- 100% 무료, 무점검 영구 자동 동작
"""
import hashlib
import random
from datetime import datetime

ZODIACS = [
    {
        "id": "rat",
        "name": "쥐띠",
        "hanja": "子",
        "emoji": "🐭",
        "years": [1948, 1960, 1972, 1984, 1996, 2008],
        "keywords": ["기회의 포착", "신중한 자금 운용", "귀인의 조력", "작은 실익", "지혜로운 처세"],
    },
    {
        "id": "ox",
        "name": "소띠",
        "hanja": "丑",
        "emoji": "🐮",
        "years": [1949, 1961, 1973, 1985, 1997, 2009],
        "keywords": ["우직한 뚝심", "장기적 결실", "안정적 수익", "기반 다지기", "꾸준한 노력"],
    },
    {
        "id": "tiger",
        "name": "호랑이띠",
        "hanja": "寅",
        "emoji": "🐯",
        "years": [1950, 1962, 1974, 1986, 1998, 2010],
        "keywords": ["과감한 결단", "주도권 확보", "도전과 성취", "돌파구 마련", "리더십 발휘"],
    },
    {
        "id": "rabbit",
        "name": "토끼띠",
        "hanja": "卯",
        "emoji": "🐰",
        "years": [1951, 1963, 1975, 1987, 1999, 2011],
        "keywords": ["유연한 대처", "위기 회피", "세밀한 분석", "소통의 힘", "실속 챙기기"],
    },
    {
        "id": "dragon",
        "name": "용띠",
        "hanja": "辰",
        "emoji": "🐲",
        "years": [1952, 1964, 1976, 1988, 2000, 2012],
        "keywords": ["비상하는 기운", "큰 그림 그리기", "명예와 성과", "대담한 전략", "재물운 상승"],
    },
    {
        "id": "snake",
        "name": "뱀띠",
        "hanja": "巳",
        "emoji": "🐍",
        "years": [1953, 1965, 1977, 1989, 2001, 2013],
        "keywords": ["예리한 통찰", "타이밍 포착", "냉철한 판단", "내실 다지기", "숨은 잠재력"],
    },
    {
        "id": "horse",
        "name": "말띠",
        "hanja": "午",
        "emoji": "🐴",
        "years": [1954, 1966, 1978, 1990, 2002, 2014],
        "keywords": ["역동적 전진", "빠른 추진력", "활동 반경 확장", "새로운 제안", "목표 달성"],
    },
    {
        "id": "sheep",
        "name": "양띠",
        "hanja": "未",
        "emoji": "🐑",
        "years": [1955, 1967, 1979, 1991, 2003, 2015],
        "keywords": ["원만한 조화", "인맥 관리", "평온한 안정", "배려의 결실", "협력의 이점"],
    },
    {
        "id": "monkey",
        "name": "원숭이띠",
        "hanja": "申",
        "emoji": "🐵",
        "years": [1956, 1968, 1980, 1992, 2004, 2016],
        "keywords": ["순발력과 재치", "창의적 해법", "시장 변화 적응", "빠른 전환", "다재다능"],
    },
    {
        "id": "rooster",
        "name": "닭띠",
        "hanja": "酉",
        "emoji": "🐔",
        "years": [1957, 1969, 1981, 1993, 2005, 2017],
        "keywords": ["정확한 계산", "원칙 준수", "선제적 대응", "시간 엄수", "완벽한 마무리"],
    },
    {
        "id": "dog",
        "name": "개띠",
        "hanja": "戌",
        "emoji": "🐶",
        "years": [1958, 1970, 1982, 1994, 2006, 2018],
        "keywords": ["신뢰와 의리", "리스크 방어", "충실한 본업", "내부 결속", "정직한 보상"],
    },
    {
        "id": "pig",
        "name": "돼지띠",
        "hanja": "亥",
        "emoji": "🐷",
        "years": [1959, 1971, 1983, 1995, 2007, 2019],
        "keywords": ["풍요로운 수확", "낙관적 여유", "자산 보존", "너그러운 포용", "뜻밖의 행운"],
    },
]

OVERVIEW_TEMPLATES = [
    "묵혀두었던 일에서 긍정적인 실마리가 풀리는 날입니다. 조급하게 결론을 내리기보다는 주변 흐름을 관망하며 타이밍을 재는 지혜가 큰 이득으로 돌아옵니다.",
    "재물운의 기운이 상승곡선을 그리는 시점입니다. 기존의 계획을 충실히 밀고 나가면 기대 이상의 실속을 챙길 수 있습니다.",
    "변화의 바람이 불어오는 날이니 유연한 태도가 필수적입니다. 고집을 부리기보다는 상황에 맞게 포트폴리오나 전략을 조정하세요.",
    "주변 사람과의 신뢰와 정보 교류가 뜻밖의 재정적 기회를 가져다줍니다. 귀인의 조언에 귀를 기울이면 리스크를 사전에 차단할 수 있습니다.",
    "무리한 확장보다는 현재의 자산과 성과를 지키는 수성(守成)의 자세가 유리합니다. 꼼꼼한 지출 점검이 숨은 수익이 됩니다.",
    "직관과 판단력이 예리하게 살아나는 하루입니다. 망설이던 사안이 있다면 데이터에 기반하여 과감한 결단을 내릴 때입니다.",
    "씨앗을 뿌린 만큼 정직한 결실이 맺히는 운세입니다. 단기 시세차익보다는 중장기적 가치에 집중할 때 마음에 여유가 생깁니다.",
    "뜻밖의 지출 요인이 생길 수 있으니 계약서나 자금 출납을 재확인하세요. 원칙을 지키면 오히려 전화위복의 기회가 됩니다.",
]

ADVICE_TEMPLATES = [
    "‘빠른 승부’보다는 ‘확실한 승부’를 택하세요. 한 템포 쉬어가는 여유가 실수를 막습니다.",
    "계약이나 문서 작성 시 작은 글씨 하나까지 꼼꼼히 확인하는 치밀함이 필요합니다.",
    "감정에 휩쓸린 즉흥적 소비나 투자를 피하고, 객관적 데이터와 숫자에 집중하세요.",
    "혼자 모든 것을 짊어지려 하지 말고, 신뢰할 수 있는 동료나 전문가와 상의하세요.",
    "눈앞의 작은 손실에 일희일비하지 마세요. 큰 파도를 내다보는 넓은 시야가 요구됩니다.",
    "오늘은 지출을 최소화하고 비상 유동성을 확보해두는 것이 가장 현명한 처세입니다.",
]

YEAR_TIPS = {
    40: ["경험에서 우러나온 통찰이 빛을 발합니다. 후배나 동료에게 모범이 되는 결정을 내리세요.", "안정적인 자산 관리가 최우선입니다. 무리한 모험은 피하세요."],
    50: ["가정의 화목과 재정적 안정이 함께하는 날입니다. 건강과 재충전에 시간을 투자하세요.", "문서상의 권리 관계를 명확히 정돈해두면 향후 큰 보탬이 됩니다."],
    60: ["오랜 시간 다져온 인맥과 신뢰가 든든한 힘이 되어줍니다.", "여유로운 마음가짐으로 일상을 관조할 때 더 큰 평안이 찾아옵니다."],
    70: ["자금의 흐름이 원활해지며 그간의 노고가 결실을 맺는 시기입니다.", "새로운 프로젝트나 투자의 전환점을 맞이하니 꼼꼼히 검토하세요."],
    80: ["실무에서의 주도권과 전문성을 인정받는 날입니다. 자신감을 가지세요.", "협상이나 미팅에서 유리한 고지를 점할 수 있으니 적극적으로 어필하세요."],
    90: ["패기와 열정이 새로운 기회를 만들어냅니다. 배움과 자기계발에 투자하세요.", "작은 성공 경험을 발판 삼아 한 단계 더 도약할 수 있는 하루입니다."],
    00: ["젊은 감각과 트렌드 파악 능력이 무기입니다. 신선한 아이디어를 제안해보세요.", "첫 단추를 잘 꿰는 것이 중요합니다. 기초를 단단히 다지세요."],
}

LUCKY_COLORS = ["골드 앰버", "네이비 블루", "에메랄드 그린", "클래식 버건디", "스노우 화이트", "차콜 그레이", "소프트 베이지", "스카이 블루"]
LUCKY_DIRECTIONS = ["동남쪽", "정남쪽", "서북쪽", "동북쪽", "정동쪽", "남서쪽"]


def get_deterministic_rng(date_obj, topic_id):
    """날짜와 띠 ID를 조합하여 하루 동안 고정된 난수 생성기를 반환합니다."""
    date_str = date_obj.strftime("%Y-%m-%d")
    seed_str = f"{date_str}:{topic_id}:panse_fortune_seed"
    seed_int = int(hashlib.md5(seed_str.encode("utf-8")).hexdigest()[:8], 16)
    return random.Random(seed_int)


def generate_zodiac_fortune(zodiac, now):
    rng = get_deterministic_rng(now, zodiac["id"])
    
    wealth_score = rng.randint(75, 98)
    stars = "★" * (wealth_score // 20) + "☆" * (5 - (wealth_score // 20))
    keyword = rng.choice(zodiac["keywords"])
    overview = rng.choice(OVERVIEW_TEMPLATES)
    advice = rng.choice(ADVICE_TEMPLATES)
    
    lucky_num = f"{rng.randint(1, 9)}, {rng.randint(11, 45)}"
    lucky_color = rng.choice(LUCKY_COLORS)
    lucky_dir = rng.choice(LUCKY_DIRECTIONS)
    
    # 연도별 한 줄 운세
    year_fortunes = []
    for yr in zodiac["years"]:
        decade = (yr % 100) // 10 * 10
        pool = YEAR_TIPS.get(decade, YEAR_TIPS[70])
        tip = rng.choice(pool)
        year_fortunes.append({"year": yr, "tip": tip})
        
    return {
        "id": zodiac["id"],
        "name": zodiac["name"],
        "hanja": zodiac["hanja"],
        "emoji": zodiac["emoji"],
        "wealth_score": wealth_score,
        "stars": stars,
        "keyword": keyword,
        "overview": overview,
        "advice": advice,
        "lucky_num": lucky_num,
        "lucky_color": lucky_color,
        "lucky_dir": lucky_dir,
        "years": year_fortunes,
    }


def render_fortune_html(now):
    """12간지 띠별 오늘의 운세 섹션 HTML 생성"""
    date_str = f"{now.year}년 {now.month}월 {now.day}일"
    
    cards_html = []
    chip_buttons = []
    
    for z in ZODIACS:
        data = generate_zodiac_fortune(z, now)
        
        chip_buttons.append(
            f'<button class="z-chip-btn" type="button" data-target="zodiac-{z["id"]}">{z["emoji"]} {z["name"]}</button>'
        )
        
        year_rows = "".join(
            f'<div class="z-year-row"><span class="z-yr">{yf["year"]}년생 ({now.year - yf["year"] + 1}세)</span><span class="z-yr-tip">{yf["tip"]}</span></div>'
            for yf in data["years"]
        )
        
        card = f'''
      <div class="z-card" id="zodiac-{data["id"]}" data-zodiac="{data["id"]}">
        <div class="z-card-head">
          <div class="z-badge-wrap">
            <span class="z-emoji">{data["emoji"]}</span>
            <div class="z-name-block">
              <h3 class="z-name">{data["name"]} <span class="z-hanja">({data["hanja"]})</span></h3>
              <span class="z-keyword">🎯 오늘의 키워드: <b>{data["keyword"]}</b></span>
            </div>
          </div>
          <div class="z-score-block">
            <span class="z-score-label">재물·투자운</span>
            <div class="z-score-val"><span class="z-stars">{data["stars"]}</span> <b>{data["wealth_score"]}점</b></div>
          </div>
        </div>

        <div class="z-body">
          <div class="z-section">
            <div class="z-sec-title">📜 오늘의 총평 &amp; 재물 흐름</div>
            <p class="z-desc">{data["overview"]}</p>
          </div>

          <div class="z-section">
            <div class="z-sec-title">💡 오늘의 처세와 조언</div>
            <p class="z-desc z-advice">{data["advice"]}</p>
          </div>

          <div class="z-section">
            <div class="z-sec-title">🎂 출생 연도대별 한 줄 운세</div>
            <div class="z-years-grid">
              {year_rows}
            </div>
          </div>

          <div class="z-lucky-bar">
            <span class="z-lucky-item">🍀 행운의 숫자: <b>{data["lucky_num"]}</b></span>
            <span class="z-lucky-sep">·</span>
            <span class="z-lucky-item">🎨 행운의 색상: <b>{data["lucky_color"]}</b></span>
            <span class="z-lucky-sep">·</span>
            <span class="z-lucky-item">🧭 행운의 방위: <b>{data["lucky_dir"]}</b></span>
          </div>

          <div class="z-card-foot">
            <button class="z-copy-btn" type="button" data-copy-zodiac="{data["id"]}" data-name="{data["name"]}">📋 {data["name"]} 운세 복사</button>
            <button class="z-pin-btn" type="button" data-set-my-zodiac="{data["id"]}" data-name="{data["name"]}">⭐ 내 띠로 설정</button>
          </div>
        </div>
      </div>'''
        cards_html.append(card)

    chips_bar = "\n        ".join(chip_buttons)
    all_cards = "\n".join(cards_html)

    return f'''
  <!-- 🔮 12간지 띠별 오늘의 재물·투자 운세 전용 섹션 -->
  <section class="detail card hidden" data-topic="fortune" aria-label="오늘의 띠별 운세">
    <div class="fortune-hero">
      <div class="fortune-hero-in">
        <div class="fortune-title-wrap">
          <span class="fortune-pill">🔮 12간지 매일 자정 갱신</span>
          <h2 class="fortune-main-title hl">오늘의 띠별 재물 &amp; 투자 운세</h2>
          <p class="fortune-sub">세상의 판세를 읽고 나의 재물운을 점치는 <b>{date_str}</b> 명리 처세 가이드</p>
        </div>
        <div class="my-zodiac-banner" id="my-zodiac-banner" style="display:none;">
          <span class="my-z-tag">⭐ 나의 띠</span>
          <span class="my-z-text" id="my-z-text">등록된 내 띠가 없습니다.</span>
          <button class="my-z-jump" id="my-z-jump" type="button">바로가기 ›</button>
        </div>
      </div>

      <!-- 빠른 띠 선택 칩 바 -->
      <div class="z-chips-scroll">
        <div class="z-chips-in">
          {chips_bar}
        </div>
      </div>
    </div>

    <div class="zodiacs-grid">
{all_cards}
    </div>
  </section>
'''
