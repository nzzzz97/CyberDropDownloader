from __future__ import annotations

from dataclasses import field
from typing import TYPE_CHECKING
import httpx

from cyberdrop_dl.clients.errors import JDownloaderFailure
from cyberdrop_dl.managers.manager import Manager
from cyberdrop_dl.utils.utilities import log
import time

if TYPE_CHECKING:
    from yarl import URL


class JDownloaderLocal:
    """Class that handles connecting and passing links to JDownloader"""
    def __init__(self, manager: Manager):
        self.enabled = manager.config_manager.settings_data['Runtime_Options']['send_unsupported_to_jdownloader']
        self.download_directory = manager.path_manager.download_dir
        self.jdownloader_agent = field(init=False)

    async def jdownloader_setup(self) -> None:
        """Setup function for JDownloader"""
        try:
            r = httpx.get('http://127.0.0.1:9666/jdcheck.js')
            if r.status_code != 200:
                raise (Exception("No jdownloader connection established\n"))

        except Exception as e:
            await log("Failed JDownloader setup", 40)
            await log(e.message, 40)
            self.enabled = False
            time.sleep(20)


    async def direct_unsupported_to_jdownloader(self, url: URL, title: str) -> None:
        """Sends links to JDownloader"""
        try:
            data = {
                'passwords': 'myPassword',
                'source': 'http://jdownloader.org/spielwiese',
                'urls': [url],
                'package': title
            }
            r = httpx.post("http://127.0.0.1:9666/flash/add", data=data)

        except Exception as e:
            await log(f"Failed to send {url} to JDownloader", 40)
            await log(e.message, 40)
