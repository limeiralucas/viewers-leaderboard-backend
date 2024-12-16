from pydantic import BaseModel


class AuthUserTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str


class TokenValidationResponse(BaseModel):
    client_id: str
    login: str
    scopes: list[str] | None
    user_id: str
    expires_in: int


class AppTokenResponse(BaseModel):
    access_token: str
    expires_in: int
    token_type: str
