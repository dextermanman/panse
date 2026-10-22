# 청약 메뉴 (판세 /apt/)

판세 상단 메뉴의 「🏠 청약」 → `/apt/` 페이지. 청약홈 공고·일정·주택형별 분양가·경쟁률을 보여줍니다.

| 파일 | 역할 |
|---|---|
| `fetch_apt.py` | 공공데이터포털 청약홈 API → `apt.json` (하루 3번, `.github/workflows/apt.yml`) |
| `render_apt.py` | `apt.json` → `public/apt/index.html` (판세 갱신 때마다 — D-day·상태를 오늘 기준으로) |
| `sample_apt.json` | 견본 데이터: `python3 apt/render_apt.py apt/sample_apt.json preview.html` |

## 설정
1. data.go.kr → **「한국부동산원_청약홈 분양정보 조회 서비스」** 활용신청
2. (선택) **「한국부동산원_청약홈 청약 신청·당첨자 정보 조회 서비스」** 도 신청 → 경쟁률 표시
3. 일반 인증키(Decoding)를 GitHub Secret **`DATA_GO_KR_KEY`** 로 등록
4. Actions → 「청약 정보 수집」 → Run workflow 로 첫 수집

키가 없으면 수집은 조용히 건너뛰고, 페이지는 「청약 데이터를 준비 중입니다」로 나옵니다.
관심지역(⭐ 동탄·아산)은 `render_apt.py` 의 `FAV_CITIES` 에서 바꿉니다.
