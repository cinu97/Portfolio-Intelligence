from __future__ import annotations

import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import quote
from xml.etree import ElementTree

import requests

from analytics.intelligence.models import NewsItem


class RSSNewsProvider:
    """Fetch current macro and India-market news from RSS feeds."""

    DEFAULT_FEEDS = (
        # Broad macro/business context.
        (
            "BBC",
            "https://feeds.bbci.co.uk/news/business/rss.xml",
        ),

        # India-focused market/sector searches.
        (
            "Google News",
            "https://news.google.com/rss/search?q="
            "India+stock+market+banking+credit+growth"
            "&hl=en-IN&gl=IN&ceid=IN%3Aen",
        ),
        (
            "Google News",
            "https://news.google.com/rss/search?q="
            "India+IT+services+technology+spending"
            "&hl=en-IN&gl=IN&ceid=IN%3Aen",
        ),
        (
            "Google News",
            "https://news.google.com/rss/search?q="
            "India+FMCG+consumer+rural+demand"
            "&hl=en-IN&gl=IN&ceid=IN%3Aen",
        ),
        (
            "Google News",
            "https://news.google.com/rss/search?q="
            "India+defence+procurement+orders"
            "&hl=en-IN&gl=IN&ceid=IN%3Aen",
        ),
        (
            "Google News",
            "https://news.google.com/rss/search?q="
            "India+gold+prices+silver+prices"
            "&hl=en-IN&gl=IN&ceid=IN%3Aen",
        ),
        (
            "Google News",
            "https://news.google.com/rss/search?q="
            "India+pharma+FDA+drug+approval"
            "&hl=en-IN&gl=IN&ceid=IN%3Aen",
        ),
        (
            "Google News",
            "https://news.google.com/rss/search?q="
            "India+oil+crude+prices+energy"
            "&hl=en-IN&gl=IN&ceid=IN%3Aen",
        ),
        (
            "Google News",
            "https://news.google.com/rss/search?q="
            "India+steel+copper+aluminium+metal+prices"
            "&hl=en-IN&gl=IN&ceid=IN%3Aen",
        ),
        (
            "Google News",
            "https://news.google.com/rss/search?q="
            "India+auto+vehicle+sales+demand"
            "&hl=en-IN&gl=IN&ceid=IN%3Aen",
        ),
    )

    def __init__(
        self,
        feeds: tuple[tuple[str, str], ...] | None = None,
        timeout: int = 10,
    ) -> None:
        self.feeds = feeds or self.DEFAULT_FEEDS
        self.timeout = timeout

    def fetch(
        self,
        limit_per_feed: int = 20,
    ) -> list[NewsItem]:

        items: list[NewsItem] = []

        for source_name, feed_url in self.feeds:

            try:
                response = requests.get(
                    feed_url,
                    headers={
                        "User-Agent": (
                            "Portfolio-Intelligence/1.0 "
                            "(market research)"
                        )
                    },
                    timeout=self.timeout,
                )

                response.raise_for_status()

                root = ElementTree.fromstring(
                    response.content
                )

                feed_items = root.findall(".//item")

                for item in feed_items[:limit_per_feed]:

                    title = self._text(
                        item,
                        "title",
                    )

                    if not title:
                        continue

                    link = self._text(
                        item,
                        "link",
                    )

                    published = self._parse_date(
                        self._text(
                            item,
                            "pubDate",
                        )
                    )

                    summary = self._clean_text(
                        self._text(
                            item,
                            "description",
                        )
                    )

                    items.append(
                        NewsItem(
                            title=title,
                            source=source_name,
                            url=link,
                            published_at=published,
                            summary=summary,
                        )
                    )

            except Exception:
                # A failed feed must never break the investment pipeline.
                continue

        return self._deduplicate(items)

    @staticmethod
    def _text(
        element: ElementTree.Element,
        tag: str,
    ) -> str:

        child = element.find(tag)

        if child is None or child.text is None:
            return ""

        return child.text.strip()

    @staticmethod
    def _parse_date(
        value: str,
    ) -> datetime | None:

        if not value:
            return None

        try:

            parsed = parsedate_to_datetime(
                value
            )

            if parsed.tzinfo is None:
                parsed = parsed.replace(
                    tzinfo=timezone.utc
                )

            return parsed

        except (
            TypeError,
            ValueError,
            OverflowError,
        ):
            return None

    @staticmethod
    def _clean_text(
        value: str,
    ) -> str:

        return re.sub(
            r"<[^>]+>",
            " ",
            value,
        ).strip()

    @staticmethod
    def _deduplicate(
        items: list[NewsItem],
    ) -> list[NewsItem]:

        seen: set[tuple[str, str]] = set()
        result: list[NewsItem] = []

        for item in items:

            key = (
                item.title.strip().lower(),
                item.source,
            )

            if key in seen:
                continue

            seen.add(key)
            result.append(item)

        return result