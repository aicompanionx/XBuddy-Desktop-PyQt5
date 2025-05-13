from typing import Optional


class NewsModel:
    """News，消息队列中的新闻字段"""
    """Abstract，摘要"""
    abstract: str
    """Cover Img，封面图片"""
    cover_img: str
    """Id，ID"""
    id: Optional[int]
    """News Url，文章URL, 当前也是来源URL, 之前过渡处理的冗余字段"""
    news_url: str
    """Origin Url，来源URL"""
    origin_url: str
    """Published At，发布时间戳，精确到秒"""
    published_at: int
    """Sort Id，分类id: 1 快讯 2 长文章"""
    sort_id: int
    """Source Id，平台里的ID: 平台标注+平台文章ID"""
    source_id: str
    """Source Name，平台类型名: 如 odaily, theblockbeats"""
    source_name: str
    """Source Type，平台类型id: 5 星球日报 6 区块律动"""
    source_type: int
    """Title，标题"""
    title: str
    """Type，处理类型, 当前只有 2"""
    type: Optional[int]

    def __init__(self, abstract: str, cover_img: str, id: Optional[int], news_url: str, origin_url: str, published_at: int, sort_id: int, source_id: str, source_name: str, source_type: int, title: str, type: Optional[int]) -> None:
        self.abstract = abstract
        self.cover_img = cover_img
        self.id = id
        self.news_url = news_url
        self.origin_url = origin_url
        self.published_at = published_at
        self.sort_id = sort_id
        self.source_id = source_id
        self.source_name = source_name
        self.source_type = source_type
        self.title = title
        self.type = type