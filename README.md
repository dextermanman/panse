# 돌아가는 판세

중동전쟁 · 반도체 · 디스플레이 · 주식 · AI · 배터리·전기차 · 세계 경제 —
일곱 갈래 뉴스와 금·은 시세, 환율을 30분마다 모아 한 페이지로 보여줍니다.

**https://daseot-news.surge.sh**

## 구성

| 파일 | 역할 |
|---|---|
| `fetch_news.py` | 구글 뉴스 RSS 수집 + 금·은 시세 + 하나은행 고시 환율 → `news.json` |
| `render.py` | `news.json` → `dashboard.html` |
| `update.sh` | 위 둘을 실행하고 surge에 배포 (로컬용) |
| `.github/workflows/update.yml` | 30분마다 같은 일을 GitHub에서 수행 |

## 데이터 출처

- 뉴스: 구글 뉴스 RSS (개인·비상업적 용도)
- 금·은 현물: api.gold-api.com
- 환율: 네이버 금융(하나은행 매매기준율), 실패 시 open.er-api.com

## 직접 돌려보기

```bash
python3 fetch_news.py && python3 render.py && open dashboard.html
```
