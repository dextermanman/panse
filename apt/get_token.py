#!/usr/bin/env python3
"""Blogger 자동 게시용 refresh token 을 한 번 발급받는 도우미 (내 컴퓨터에서 실행).

1) Google Cloud 콘솔에서 만든 'OAuth 클라이언트 ID(데스크톱 앱)'의 JSON 을 내려받아
2) python3 get_token.py client_secret_xxx.json
3) 브라우저에서 블로그 계정으로 로그인·허용하면 터미널에 refresh token 이 출력됩니다.
"""
import http.server
import json
import sys
import urllib.parse
import urllib.request
import webbrowser

PORT = 8765
REDIRECT = f"http://127.0.0.1:{PORT}/"
SCOPE = "https://www.googleapis.com/auth/blogger"


def main():
    if len(sys.argv) != 2:
        sys.exit("사용법: python3 get_token.py client_secret.json")
    cfg = json.load(open(sys.argv[1]))
    cfg = cfg.get("installed") or cfg.get("web")
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
        "client_id": cfg["client_id"], "redirect_uri": REDIRECT, "response_type": "code",
        "scope": SCOPE, "access_type": "offline", "prompt": "consent"})

    got = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            got.update(urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query))
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("완료! 터미널로 돌아가세요.".encode())

        def log_message(self, *a):
            pass

    print("브라우저가 열리지 않으면 아래 주소를 직접 여세요:\n" + auth_url)
    webbrowser.open(auth_url)
    http.server.HTTPServer(("127.0.0.1", PORT), Handler).handle_request()
    if "code" not in got:
        sys.exit(f"인증 실패: {got}")

    body = urllib.parse.urlencode({
        "code": got["code"][0], "client_id": cfg["client_id"], "client_secret": cfg["client_secret"],
        "redirect_uri": REDIRECT, "grant_type": "authorization_code"}).encode()
    with urllib.request.urlopen("https://oauth2.googleapis.com/token", body) as r:
        tok = json.load(r)
    print("\nBLOGGER_CLIENT_ID     =", cfg["client_id"])
    print("BLOGGER_CLIENT_SECRET =", cfg["client_secret"])
    print("BLOGGER_REFRESH_TOKEN =", tok.get("refresh_token", "(없음 — prompt=consent 로 다시 시도)"))
    print("\n위 세 값을 GitHub 저장소 Settings → Secrets and variables → Actions 에 등록하세요.")


if __name__ == "__main__":
    main()
