from discord.ext import commands

class EpicCache:
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self._suggestion_channel_cache: dict = {}
        self._suggestion_message_cache: dict = {}
        self._staff_cache: dict = {}
        self._money_cache: dict = {}

    def check_suggestion_channel_cache(self, guild_id: float) -> bool:
        if self._suggestion_channel_cache.get(guild_id) is None:
            return False
        else:
            return True 
        
    def get_suggestion_channel_cache(self, guild_id: float) -> float:
        return self._suggestion_channel_cache.get(guild_id)

    def set_suggestion_channel_cache(self, guild_id: float, channel_id: float) -> None:
        self._suggestion_channel_cache[guild_id] = channel_id
        
    def check_suggestion_message_cache(self, suggestion_id: float) -> bool:
        if self._suggestion_message_cache.get(suggestion_id) is None:
            return False
        else:
            return True 
        
    def get_suggestion_message_cache(self, suggestion_id: float) -> float:
        return self._suggestion_message_cache.get(suggestion_id)

    def set_suggestion_message_cache(self, suggestion_id: float, message_id: float) -> None:
        self._suggestion_message_cache[suggestion_id] = message_id
        
    def check_staff_cache(self, guild_id: float) -> bool:
        if self._staff_cache.get(guild_id) is None:
            return False
        else:
            return True 
        
    def get_staff_cache(self, guild_id: float) -> float:
        return self._staff_cache.get(guild_id)

    def set_staff_cache(self, guild_id: float, role_id: float) -> None:
        self._staff_cache[guild_id] = role_id
        
    def check_money_cache(self, user_id: float) -> bool:
        if self._money_cache.get(user_id) is None:
            return False
        else:
            return True 
        
    def get_money_cache(self, user_id: float) -> int:
        return self._money_cache.get(user_id)

    def set_money_cache(self, user_id: float, money: float) -> None:
        self._money_cache[user_id] = money
    