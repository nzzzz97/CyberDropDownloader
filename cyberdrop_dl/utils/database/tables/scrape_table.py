from __future__ import annotations
import pathlib
import json

from sqlite3 import Row, IntegrityError

import asyncio
import aiomysql

from typing import TYPE_CHECKING, Iterable, Any
from yarl import URL

from cyberdrop_dl.utils.database.table_definitions import create_history, create_fixed_history
from cyberdrop_dl.utils.utilities import log


if TYPE_CHECKING:
    from cyberdrop_dl.utils.dataclasses.url_objects import MediaItem

class ScrapeTable:
    def __init__(self, db_conn: aiomysql.Connection):
        self.db_conn: aiomysql.Connection = db_conn
        self.ignore_history: bool = False

    async def startup(self) -> None:
        pass

    async def update_scrape(self, scrape_id, downloaded, previous, skipped, failed, scrape_failures,download_failures,download_log,scrape_errors_log,last_scraped,
                            download_error_urls,unsupported_url,completed):


        async with self.db_conn.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    sf = json.dumps(scrape_failures)
                    df = json.dumps(download_failures)
                    await cursor.execute("""UPDATE scrapes SET downloaded = %s,
                        previous = %s,
                        skipped = %s,
                        failed = %s,
                        scrape_failures = %s,
                        download_failures = %s,
                        download_logs = %s,
                        scrape_errors_log = %s,
                        last_scraped_post = %s,
                        download_error_urls = %s,
                        unsupported_urls = %s,
                        completed = %s
                        WHERE id = %s
                            """,(downloaded, previous, skipped, failed, sf, df,download_log,scrape_errors_log,last_scraped,
                                download_error_urls,unsupported_url,completed, scrape_id))
                except Exception as e:
                    await log(f"Error updated scrape: {e}",20)
                    return []