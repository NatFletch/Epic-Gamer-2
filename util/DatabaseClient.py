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

    async def setup_tables(self):
        print("Loading database")
        await self.execute(f"""
            CREATE TABLE IF NOT EXISTS suggestion_channels (guild_id bigint, channel_id bigint);
            CREATE TABLE IF NOT EXISTS staff_roles (guild_id bigint, role_id bigint);
            CREATE TABLE IF NOT EXISTS admin_roles (guild_id bigint, role_id bigint);
        """)
