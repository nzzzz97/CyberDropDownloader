from typing import List
import aiomysql

from cyberdrop_dl.utils.database.table_definitions import create_temp


class TempTable:
    def __init__(self, db_conn: aiomysql.Connection):
        self.db_conn: aiomysql.Connection = db_conn

    async def startup(self) -> None:
        """Startup process for the TempTable"""
        #cursor = await self.db_conn.cursor()
        #await cursor.execute("select * from temp")
        #await cursor.commit()

    async def get_temp_names(self) -> List[str]:
        """Gets the list of temp filenames"""
        async with self.db_conn.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT downloaded_filename FROM temp")
                filenames = await cursor.fetchall()
                filenames = [list(filename) for filename in filenames]
                return list(sum(filenames, ()))

    async def sql_insert_temp(self, downloaded_filename: str) -> None:
        """Inserts a temp filename into the downloads_temp table"""
        await self.db_conn.execute("""INSERT OR IGNORE INTO downloads_temp VALUES (%s)""", (downloaded_filename,))
        await self.db_conn.commit()
