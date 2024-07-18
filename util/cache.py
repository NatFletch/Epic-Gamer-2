class EpicCache:
    def __init__(self, bot):
        self.bot = bot
        self._suggestion_channel_cache = {}
        self._suggestion_message_cache = {}
        self._staff_cache = {}
        self._money_cache = {}

    def check_suggestion_channel_cache(self, guild_id):
        if self._suggestion_channel_cache.get(guild_id) is None:
            return False
        else:
            return True 
        
    def get_suggestion_channel_cache(self, guild_id):
        return self._suggestion_channel_cache.get(guild_id)

    def set_suggestion_channel_cache(self, guild_id, channel_id):
        self._suggestion_channel_cache[guild_id] = channel_id
        
    def check_suggestion_message_cache(self, suggestion_id):
        if self._suggestion_message_cache.get(suggestion_id) is None:
            return False
        else:
            return True 
        
    def get_suggestion_message_cache(self, suggestion_id):
        return self._suggestion_message_cache.get(suggestion_id)

    def set_suggestion_message_cache(self, suggestion_id, message_id):
        self._suggestion_message_cache[suggestion_id] = message_id
        
    def check_staff_cache(self, guild_id):
        if self._staff_cache.get(guild_id) is None:
            return False
        else:
            return True 
        
    def get_staff_cache(self, guild_id):
        return self._staff_cache.get(guild_id)

    def set_staff_cache(self, guild_id, role_id):
        self._staff_cache[guild_id] = role_id
        
    def check_money_cache(self, user_id):
        if self._money_cache.get(user_id) is None:
            return False
        else:
            return True 
        
    def get_money_cache(self, user_id):
        return self._money_cache.get(user_id)

    def set_money_cache(self, user_id, money):
        self._money_cache[user_id] = money
    