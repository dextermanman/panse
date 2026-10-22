#!/usr/bin/env python3
"""apt.json -> Blogger 자동 게시.

- 단지마다 글 1개. 이미 올린 단지는 내용이 바뀌었을 때만 수정(경쟁률 추가, 상태 변경 등).
- '청약 캘린더' 페이지 1개를 만들고 매번 갱신.
- 올린 글의 ID·주소는 apt/posts_state.json 에 기록 (워크플로가 커밋).

필요한 환경변수: BLOGGER_BLOG_ID, BLOGGER_CLIENT_ID, BLOGGER_CLIENT_SECRET, BLOGGER_REFRESH_TOKEN
선택: BLOGGER_DRAFT=1 이면 새 글을 임시저장으로만 올림, DRY_RUN=1 이면 게시하지 않고 출력만.
"""
import hashlib
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

from render_post import calendar_html, labels, post_html, title

KST = timezone(timedelta(hours=9))
HERE = Path(__file__).parent
STATE = HERE / "posts_state.json"
API = "https://www.googleapis.com/blogger/v3/blogs/"
MAX_NEW_PER_RUN = 10  # Blogger 일일 게시 한도 대비 여유


def access_token():
    body = urllib.parse.urlencode({
        "client_id": os.environ["BLOGGER_CLIENT_ID"],
        "client_secret": os.environ["BLOGGER_CLIENT_SECRET"],
        "refresh_token": os.environ["BLOGGER_REFRESH_TOKEN"],
        "grant_type": "refresh_token",
    }).encode()
    with urllib.request.urlopen("https://oauth2.googleapis.com/token", body, timeout=15) as r:
        return json.load(r)["access_token"]


def api(method, path, token, payload=None, query=None):
    url = API + path + ("?" + urllib.parse.urlencode(query) if query else "")
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as err:
        raise RuntimeError(f"{method} {path} -> {err.code} {err.read()[:300]!r}") from None


def digest(*parts):
    return hashlib.sha256(json.dumps(parts, ensure_ascii=False).encode()).hexdigest()[:16]


def main():
    data = json.loads((HERE / "apt.json").read_text())
    state = json.loads(STATE.read_text()) if STATE.exists() else {"posts": {}, "calendar": {}}
    today = datetime.now(KST).date()
    day = today.isoformat()
    dry = os.environ.get("DRY_RUN") == "1"
    draft = os.environ.get("BLOGGER_DRAFT") == "1"
    blog = os.environ.get("BLOGGER_BLOG_ID", "")
    token = None if dry else access_token()

    created = updated = 0
    for c in data["complexes"]:
        t, html_, lbl = title(c), post_html(c, today, day), labels(c, today)
        h = digest(t, html_, lbl)
        prev = state["posts"].get(c["id"])
        if prev and prev.get("hash") == h:
            continue
        if dry:
            print(("수정" if prev else "신규"), t)
            continue
        body = {"title": t, "content": html_, "labels": lbl}
        try:
            if prev:
                res = api("PATCH", f"{blog}/posts/{prev['post_id']}", token, body)
                updated += 1
            else:
                if created >= MAX_NEW_PER_RUN:
                    continue
                res = api("POST", f"{blog}/posts", token, {"kind": "blogger#post", **body},
                          {"isDraft": "true" if draft else "false"})
                created += 1
        except RuntimeError as err:
            print("실패:", t, err)
            continue
        state["posts"][c["id"]] = {"post_id": res["id"], "url": res.get("url", ""), "title": t, "hash": h}
        print(("수정" if prev else "신규"), t, res.get("url", "(임시저장)"))

    urls = {k: v.get("url") for k, v in state["posts"].items()}
    cal = calendar_html(data["complexes"], urls, today, day)
    h = digest(cal)
    if not dry and state["calendar"].get("hash") != h:
        body = {"title": "아파트 청약 캘린더", "content": cal}
        page_id = state["calendar"].get("page_id")
        res = (api("PATCH", f"{blog}/pages/{page_id}", token, body) if page_id
               else api("POST", f"{blog}/pages", token, {"kind": "blogger#page", **body}))
        state["calendar"] = {"page_id": res["id"], "url": res.get("url", ""), "hash": h}
        print("캘린더 갱신", res.get("url", ""))

    if not dry:
        STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1))
    print(f"신규 {created} · 수정 {updated}")


if __name__ == "__main__":
    sys.exit(main())
