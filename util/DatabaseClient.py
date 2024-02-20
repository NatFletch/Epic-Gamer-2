import json


class DatabaseClient:
    def __init__(self, connection):
        self.connection = connection

    def get_connection(self):
        return self.connection

    async def close(self):
        await self.connection.close()

    async def execute(self, string, *args):
        transaction = self.connection.transaction()
        await transaction.start()
        try:
            await self.connection.execute(string, *args)
        except:
            await transaction.rollback()
            raise
        else:
            await transaction.commit()

    async def fetchrow(self, string, *args):
        transaction = self.connection.transaction()
        await transaction.start()
        try:
            response = await self.connection.fetchrow(string, *args)
        except:
            await transaction.rollback()
            raise
        else:
            await transaction.commit()

        return response

    async def create_suggestion_table(self):
        print("Creating suggestions table")
        await self.execute("""
            CREATE TABLE suggestions (
                id serial,
                discord_message bigint,
                guild_id bigint
            )
        """)

    async def find_suggestion_table(self):
        response = await self.fetchrow("""
            SELECT to_regclass('public.suggestions')
        """)
        return dict(response)

    async def create_suggestion_channel_table(self):
        print("Creating suggestion_channels table")
        await self.execute("""
            CREATE TABLE suggestion_channels (
                guild_id bigint,
                channel_id bigint
            )
        """)

    async def find_suggestion_channel_table(self):
        response = await self.fetchrow("""
            SELECT to_regclass('public.suggestion_channels')
        """)
        return dict(response)

    async def create_suggestion_allowed_role_table(self):
        print("Creating suggestion_allowed_roles table")
        await self.execute("""
            CREATE TABLE suggestion_allowed_roles (
                guild_id bigint,
                role_id bigint
            )
        """)

    async def find_suggestion_allowed_role_table(self):
        response = await self.fetchrow("""
            SELECT to_regclass('public.suggestion_allowed_roles')
        """)
        return dict(response)
