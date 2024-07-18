class EpicDatabaseClient:
    def __init__(self, connection):
        self.connection = connection

    def get_connection(self):
        return self.connection

    async def close(self):
        await self.connection.close()

    async def execute(self, string, *args):
        async with self.connection.transaction():
            return await self.connection.execute(string, *args)

    async def fetchrow(self, string, *args):
        async with self.connection.transaction():
            return await self.connection.fetchrow(string, *args)

    async def setup_tables(self):
        print("Loading database")
        await self.execute(f"""
            CREATE TABLE IF NOT EXISTS suggestion_channels (guild_id bigint, channel_id bigint);
            CREATE TABLE IF NOT EXISTS staff_roles (guild_id bigint, role_id bigint);
            CREATE TABLE IF NOT EXISTS admin_roles (guild_id bigint, role_id bigint);
            CREATE TABLE IF NOT EXISTS money (user_id bigint, money int);
        """)
