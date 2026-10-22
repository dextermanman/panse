#!/usr/bin/env python3
"""apt.json(또는 지정한 파일) -> preview.html : 게시 전 글 모양을 브라우저로 확인."""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from render_post import calendar_html, post_html, title

HERE = Path(__file__).parent
src = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "apt.json"
out = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / "preview.html"
data = json.loads(src.read_text())
today = datetime.now(timezone(timedelta(hours=9))).date()
day = today.isoformat()
card = "max-width:760px;margin:24px auto;background:#fff;padding:24px 28px;border-radius:12px;box-shadow:0 1px 4px #0002"
parts = [f'<div style="{card}"><h1 style="font-size:24px;margin:0 0 12px">아파트 청약 캘린더</h1>'
         f'{calendar_html(data["complexes"], {}, today, day)}</div>']
parts += [f'<div style="{card}"><h1 style="font-size:22px;margin:0 0 12px">{title(c)}</h1>{post_html(c, today, day)}</div>'
          for c in data["complexes"]]
out.write_text('<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
               f'<title>청약 블로그 미리보기</title></head><body style="background:#f1f3f5;margin:0;padding:8px 12px">{"".join(parts)}</body></html>')
print(out)
