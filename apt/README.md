# 청약 블로그 (Google Blogger 자동 게시)

청약홈 분양정보를 하루 3번(07:10 · 12:10 · 18:10) 모아 Blogger에 단지별 글로 올리고,
「아파트 청약 캘린더」 페이지를 갱신합니다.

| 파일 | 역할 |
|---|---|
| `fetch_apt.py` | 공공데이터포털 청약홈 API → `apt.json` (공고·일정·주택형별 분양가·경쟁률) |
| `render_post.py` | 단지 글 / 캘린더 페이지 HTML 생성 (인라인 스타일) |
| `publish_blogger.py` | Blogger API로 신규 게시·변경분 수정, 기록은 `posts_state.json` |
| `preview.py` | 게시 전 미리보기 `preview.html` 생성 |
| `get_token.py` | Blogger refresh token 발급 도우미 (내 컴퓨터에서 1회 실행) |
| `sample_apt.json` | 견본 데이터 (`python3 preview.py sample_apt.json`) |

## 처음 한 번 설정

### 1. 청약홈 API 키
1. data.go.kr 로그인 → **「한국부동산원_청약홈 분양정보 조회 서비스」** 활용신청
2. (선택) **「한국부동산원_청약홈 청약 신청·당첨자 정보 조회 서비스」** 도 신청 → 경쟁률 표시
3. 마이페이지의 **일반 인증키(Decoding)** 를 GitHub Secret `DATA_GO_KR_KEY` 로 등록

### 2. Blogger 블로그
1. blogger.com 에서 블로그 생성
2. 대시보드 주소 `blogger.com/blog/posts/<숫자>` 의 숫자 → Secret `BLOGGER_BLOG_ID`

### 3. Google Cloud OAuth (자동 게시 권한)
1. console.cloud.google.com → 새 프로젝트
2. API 및 서비스 → 라이브러리 → **Blogger API v3** 사용 설정
3. OAuth 동의 화면 → 외부 → 앱 이름·이메일만 입력, 테스트 사용자에 본인 Gmail 추가
4. **게시 상태를 「프로덕션으로 푸시」** — 테스트 상태로 두면 토큰이 7일 뒤 만료됩니다
   (검증 안 된 앱 경고가 떠도 본인 계정이면 「고급 → 이동」으로 진행하면 됩니다)
5. 사용자 인증 정보 → OAuth 클라이언트 ID → **데스크톱 앱** → JSON 다운로드
6. 내 컴퓨터에서 `python3 apt/get_token.py ~/Downloads/client_secret_xxx.json`
7. 출력된 세 값을 Secret `BLOGGER_CLIENT_ID`, `BLOGGER_CLIENT_SECRET`, `BLOGGER_REFRESH_TOKEN` 으로 등록

### 4. 첫 실행
- 처음엔 저장소 Settings → Variables 에 `BLOGGER_DRAFT=1` 을 넣으면 새 글이 **임시저장**으로만 올라갑니다.
  Blogger에서 모양을 확인한 뒤 변수를 지우면 그때부터 바로 공개 게시됩니다.
- Actions → 「청약 블로그 갱신」 → Run workflow 로 수동 실행.
- 한 번에 새 글은 최대 10개까지만 올립니다 (Blogger 게시 한도 대비).
