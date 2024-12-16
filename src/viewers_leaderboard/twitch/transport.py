from pydantic import BaseModel

class AuthUserTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str
