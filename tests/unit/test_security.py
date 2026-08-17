import pytest
import jwt

from devflow.app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    decode_access_token,
    decode_refresh_token,
)

from devflow.app.core.config import settings

def test_hash_password():
    password = 'secure-password'
    password_hashed = hash_password(password)

    assert password_hashed != password
    assert verify_password(password, password_hashed) is True

def test_verify_password_rejects_wrong_password():
    hashed = hash_password('correct-password')

    assert verify_password('wrong-password', hashed) is False

def test_hash_password_generates_different_hashes():
    first_hash = hash_password('same-password')
    second_hash = hash_password('same-password')

    assert first_hash != second_hash

def test_create_and_decode_access_token():
    user_id = '9'

    token = create_access_token(user_id)
    payload = decode_access_token(token)

    assert payload['sub'] == user_id
    assert payload['type'] == 'access'
    assert 'iat' in payload
    assert payload['exp'] > payload['iat']


def test_create_and_decode_refresh_token():
    user_id = '9'

    token = create_refresh_token(user_id)
    payload = decode_refresh_token(token)

    assert payload['sub'] == user_id
    assert payload['type'] == 'refresh'
    assert 'iat' in payload
    assert payload['exp'] > payload['iat']


def test_access_decoder_rejects_refresh_token():
    refresh_token = create_refresh_token('9')

    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(refresh_token)


def test_refresh_decoder_rejects_access_token():
    access_token = create_access_token('9')

    with pytest.raises(jwt.InvalidTokenError):
        decode_refresh_token(access_token)

def test_exception_expired_access_token():
    payload = {
        'sub': '2',
        'type': 'access',
        'exp': 0
    }

    token = jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.jwt_algorithm)
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)


def test_exception_expired_refresh_token():
    payload = {
        'sub': '2',
        'type': 'refresh',
        'exp': 0,
    }

    token = jwt.encode(
        payload,
        settings.refresh_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_refresh_token(token)

def test_exception_type_decode_token():
    token = create_access_token('2')
    payload = decode_access_token(token)
    payload['type'] = 'refresh'

    token = jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.jwt_algorithm
    )

    with pytest.raises(jwt.InvalidTokenError):
        decode_token(token, 'access')
