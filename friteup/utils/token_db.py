class TokenDB:
    def __init__(self):
        self.db = dict()

    async def set_token(self, req_id: str, access_token: str, expires_in_seconds: int):
        self.db[req_id] = {
            "access_token": access_token,
            "expires": expires_in_seconds,
            "valid": True
        }

    async def remove_token(self, req_id: str) -> bool:
        if req_id in self.db:
            del self.db[req_id]
            return True
        return False
    
    async def invalidate_token(self, req_id: str):
        self.db[req_id] = {
            "access_token": None,
            "expires": None,
            "valid": False
        }


token_db = TokenDB()
