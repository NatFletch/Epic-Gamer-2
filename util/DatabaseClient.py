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

    async def check_for_tables(self):
        db_client = self
        suggestions_channel_table = await db_client.find_suggestion_channel_table()
        suggestions_allowed_role_table = await db_client.find_staff_roles_table()

        if not suggestions_channel_table.get("to_regclass"):
            await db_client.create_suggestion_channel_table()

        if not suggestions_allowed_role_table.get("to_regclass"):
            await db_client.create_staff_roles_table()

    async def create_suggestion_table(self, guild_id):
        print(f"Creating suggestions_{guild_id} table")
        await self.execute(f"""
            CREATE TABLE suggestions_{guild_id} (
                id int,
                discord_message bigint,
                guild_id bigint
            )
        """)
        await self.execute(f"""
            CREATE SEQUENCE suggestion_id_{guild_id} START WITH 1 INCREMENT BY 1 OWNED BY suggestions_{guild_id}.id    
        """)

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
