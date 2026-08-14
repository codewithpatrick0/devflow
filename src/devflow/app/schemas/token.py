from pydantic import BaseModel


class AccessTokenResponse(BaseModel):
    access_token: str


class RefreshTokenResponse(BaseModel):
    refresh_token: str


class TokensResponse(BaseModel):
    access_token: str
    refresh_token: str
