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
            response = await self.connection.execute(string, *args)
        except:
            await transaction.rollback()
            raise
        else:
            await transaction.commit()
            return response

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

    async def create_staff_roles_table(self):
        print("Creating staff_roles table")
        await self.execute("""
            CREATE TABLE staff_roles (
                guild_id bigint,
                role_id bigint
            )
        """)

    async def find_staff_roles_table(self):
        response = await self.fetchrow("""
            SELECT to_regclass('public.staff_roles')
        """)
        return dict(response)

    async def create_admin_roles_table(self):
        print("Creating admin_roles table")
        await self.execute("""
            CREATE TABLE admin_roles (
                guild_id bigint,
                role_id bigint
            )
        """)

    async def find_admin_roles_table(self):
        response = await self.fetchrow("""
            SELECT to_regclass('public.admin_roles')
        """)
        return dict(response)
