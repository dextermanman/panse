#!/bin/bash
# 구글 뉴스 수집 -> dashboard.html 재생성 -> surge.sh 배포 (cron 30분 주기)
export PATH="/usr/local/bin:/Users/seonghoonkim/.npm-global/bin:$PATH"
cd "$(dirname "$0")" || exit 1
echo "===== $(date '+%Y-%m-%d %H:%M:%S') ====="

/Library/Frameworks/Python.framework/Versions/3.14/bin/python3 fetch_news.py && /Library/Frameworks/Python.framework/Versions/3.14/bin/python3 render.py || exit 1
cp dashboard.html public/index.html

# 로그인 후 생성되는 .surge-env 가 있으면 자동 배포
if [ -f .surge-env ]; then
  . ./.surge-env
  export SURGE_LOGIN SURGE_TOKEN
  /Users/seonghoonkim/.npm-global/bin/surge ./public --domain "$(cat public/CNAME)" 2>&1 | tail -3
else
  echo "(.surge-env 없음 — 배포 건너뜀. surge login 후 생성됩니다)"
fi

tail -n 400 update.log > update.log.tmp 2>/dev/null && mv update.log.tmp update.log
