import json
from typing import TYPE_CHECKING

import aiofiles

if TYPE_CHECKING:
    from pathlib import Path
    from yarl import URL

    from cyberdrop_dl.managers.manager import Manager


class LogManager:
    def __init__(self, manager: 'Manager'):
        self.manager = manager
        self.main_log: Path = manager.path_manager.main_log
        self.last_post_log: Path = manager.path_manager.last_post_log
        self.unsupported_urls_log: Path = manager.path_manager.unsupported_urls_log
        self.download_error_log: Path = manager.path_manager.download_error_log
        self.scrape_error_log: Path = manager.path_manager.scrape_error_log

    def startup(self) -> None:
        """Startup process for the file manager"""
        self.main_log.unlink(missing_ok=True)
        self.main_log.touch(exist_ok=True)
        self.last_post_log.unlink(missing_ok=True)
        self.last_post_log.touch(exist_ok=True)
        self.unsupported_urls_log.unlink(missing_ok=True)
        self.unsupported_urls_log.touch(exist_ok=True)
        self.download_error_log.unlink(missing_ok=True)
        self.download_error_log.touch(exist_ok=True)
        self.scrape_error_log.unlink(missing_ok=True)
        self.scrape_error_log.touch(exist_ok=True)

    async def write_last_post_log(self, url: 'URL') -> None:
        """Writes to the last post log"""
        payload = {'url': url.human_repr()}
        await self.manager.redis_manager.update_errors('last_post', url, '')
        async with aiofiles.open(self.last_post_log, 'a') as f:
            await f.write(json.dumps(payload) + "\n")

    async def write_unsupported_urls_log(self, url: 'URL') -> None:
        await self.manager.redis_manager.update_errors('unsupported', url, '')
        payload = {'url': url.human_repr()}
        """Writes to the unsupported urls log"""
        async with aiofiles.open(self.unsupported_urls_log, 'a') as f:
            await f.write(json.dumps(payload) + "\n")

    async def write_download_error_log(self, url: 'URL', error_message: str) -> None:
        """Writes to the download error log"""
        await self.manager.redis_manager.update_errors('download_error', url, error_message)
        payload = {'url': url.human_repr(), 'message': error_message}
        async with aiofiles.open(self.download_error_log, 'a') as f:
            await f.write(json.dumps(payload) + "\n")

    async def write_scrape_error_log(self, url: 'URL', error_message: str) -> None:
        """Writes to the scrape error log"""
        payload = { 'url': url.human_repr(),'message': error_message}
        await self.manager.redis_manager.update_errors('scrape_error',url,error_message)
        async with aiofiles.open(self.scrape_error_log, 'a') as f:
            await f.write(json.dumps(payload)+"\n")
            
    async def update_last_forum_post(self) -> None:
        """Updates the last forum post"""
        input_file = self.manager.path_manager.input_file
        base_urls = []
        
        async with aiofiles.open(input_file, 'r') as f:
            current_urls = await f.readlines()
            
        for url in current_urls:
            if "http" not in url:
                continue
            if "post-" in url:
                url = url.rsplit("/", 1)[0]
            if not url.endswith("\n"):
                url += "\n"
            base_urls.append(url)

        last_post_file = self.last_post_log
        if not last_post_file.exists():
            return

        async with aiofiles.open(last_post_file, 'r') as f:
            new_urls = await f.readlines()

        for url in new_urls:
            url_temp = url.rsplit("/", 1)[0] + "\n"
            if url_temp in base_urls:
                base_urls.remove(url_temp)
                base_urls.append(url)

        async with aiofiles.open(input_file, 'w') as f:
            await f.writelines(base_urls)
