import asyncio
import json
import random
from datetime import datetime

from aiohttp import web

from xbuddy.api.schemas.news import News
from xbuddy.settings import PROJECT_DIR

news_list = json.loads(
    (PROJECT_DIR / "xbuddy/api/fake_server/news.json").read_text(encoding="utf=8")
)


async def websocket_news_handler(request):
    index = -1
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    print("WebSocket client connected")
    try:
        while True:
            index += 1
            news = News(
                title=news_list[index % len(news_list)]["title"],
                abstract=news_list[index % len(news_list)]["abstract"],
                cover_img="https://example.com/image.png",
                published_at=int(datetime.now().timestamp()),
                origin_url="https://example.com/original",
                news_url="https://example.com/news",
                source_id="platform-123",
                source_type=5,
                source_name="Odaily",
                sort_id=2,
                id=random.randint(1000, 9999),
            )
            print(news)
            await ws.send_str(news.model_dump_json())
            await asyncio.sleep(5)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        print("WebSocket client disconnected")

    return ws


app = web.Application()
app.router.add_get("/dev/api/v1/news/ws", websocket_news_handler)

if __name__ == "__main__":
    web.run_app(app, host="localhost", port=8080)
