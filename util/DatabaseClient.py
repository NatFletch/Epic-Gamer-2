import json


class DatabaseClient:
    def __init__(self, connection):
        self.connection = connection

    def get_connection(self):
        return self.connection

    async def close(self):
        await self.connection.close()

    async def create_suggestion_table(self):
        async with self.connection.transaction():
            print("Creating suggestions table")
            await self.connection.execute("""
                CREATE TABLE suggestions (
                    id serial,
                    discord_message bigint,
                    guild_id bigint
                )
            """)

    async def find_suggestion_table(self):
        connection = self.connection
        async with connection.transaction():
            response = await connection.fetchrow("""
                SELECT to_regclass('public.suggestions')
            """)
            return dict(response)

    async def create_suggestion_channel_table(self):
        async with self.connection.transaction():
            print("Creating suggestion_channels table")
            await self.connection.execute("""
                CREATE TABLE suggestion_channels (
                    guild_id bigint,
                    channel_id bigint
                )
            """)

    async def find_suggestion_channel_table(self):
        connection = self.connection
        async with connection.transaction():
            response = await connection.fetchrow("""
                SELECT to_regclass('public.suggestion_channels')
            """)
            return dict(response)

