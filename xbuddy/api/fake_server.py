import asyncio
import random
from datetime import datetime

from aiohttp import web

from xbuddy.api.schemas.news import News


async def websocket_news_handler(request):
    index = -1
    news_list = [
        "The Bull Case for Galaxy Digital Is AI Data Centers Not Bitcoin Mining, Research Firm Says",
        "Metaplanet Buys Another 1,004 Bitcoin, Lifts Holdings to Over $800M Worth of BTC",
        "Bulls and Bears Get Caught off Guard as Bitcoin Jumps to $106K, Then Falls Back to $103K",
        "Crypto Daybook Americas: Bitcoin Whiplash Shakes Market as U.S. Yield Spike Threatens Bull Run",
        "Elon Musk's assassination of Trump failed and died, the doge coin plummeted to almost zero, and the Trump coin soared",
    ]
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    print("WebSocket client connected")
    try:
        while True:
            index += 1
            news = News(
                title="this is title",
                abstract=news_list[index % len(news_list)],
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
