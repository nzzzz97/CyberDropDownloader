import json
from typing import TYPE_CHECKING
import redis.asyncio as redis

import aiofiles
from typing import Any
from cyberdrop_dl.utils.globals import *
from cyberdrop_dl.utils.utilities import log
from cyberdrop_dl.utils.redis_message import RedisMessage

if TYPE_CHECKING:
    from pathlib import Path
    from yarl import URL

    from cyberdrop_dl.managers.manager import Manager


class RedisManager:
    def __init__(self, manager: 'Manager',**kwargs: Any):
        self.manager = manager
        self.channel = "logs"
        self.redis_client = redis.Redis(**kwargs)

    async def activate_scrape(self):
        stats = {
            'downloaded': 0,
            'skipped': 0,
            'failed': 0,
            'previous': 0,
        }
        await log(f"Adding scrape {SCRAPE_ID} to active scrapes", 10)
        await self.redis_client.lpush('active_scrapes', '/scrapess/' + str(SCRAPE_ID))
        await self.redis_client.hset('/scrapess/' + str(SCRAPE_ID), mapping=stats)
        msg = RedisMessage("scrape_on", '/scrapess/' + str(SCRAPE_ID))
        await self.redis_client.publish(self.channel, msg.json())

    async def deactivate_scrape(self):
        await log(f"Removing scrape {SCRAPE_ID} to active scrapes", 10)
        #await self.redis_client.srem('active_scrapes', SCRAPE_ID)

    async def update_progress(self,count,type):
        if 'SCRAPE_ID' in globals() and SCRAPE_ID > 0:
            msg = RedisMessage('progress', '/scrapess/' + str(SCRAPE_ID))
            msg.data(type,count,"")
            stats = {
                count: type
            }
            await self.redis_client.hset('/scrapess/' + str(SCRAPE_ID), mapping=stats)
            await self.redis_client.publish(self.channel, msg.json())

    async def add_completed_file(self,media):
        msg = RedisMessage('downloads', '/scrapess/' + str(SCRAPE_ID))
        payload = {
            'url': media.url.human_repr(),
            'filename': media.filename,
            'filesize': media.filesize,
        }
        msg.payload = payload
        key = "/scrapess/{}:downloads".format(SCRAPE_ID)
        await self.redis_client.rpush(key, json.dumps(payload))
        await self.redis_client.publish(self.channel, msg.json())

    async def update_scrapping_links(self,type,url: 'URL' ,message: str):
        pass

    async def update_errors(self,type,url: 'URL' ,message: str):
        if 'SCRAPE_ID' in globals() and SCRAPE_ID > 0:
            msg = RedisMessage('errors', '/scrapess/' + str(SCRAPE_ID))
            payload = {
                'url': url.human_repr(),
                'message': message
            }
            msg.payload = payload
            key = "/scrapess/{}:error:{}".format(SCRAPE_ID,type)
            await self.redis_client.rpush(key, json.dumps(payload))
            await self.redis_client.publish(self.channel, msg.json())


    async def close(self):
        await self.redis_client.close()