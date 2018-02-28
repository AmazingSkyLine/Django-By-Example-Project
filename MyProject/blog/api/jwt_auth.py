import jwt
from django.contrib.auth.models import User
from time import time


def create_token(username, user_id):
    payload = {
        'iat': int(time()),
        'exp': int(time()) + 86400 * 7,
        'user_id': user_id,
        'username': username
    }
    token = jwt.encode(payload, 'secret', algorithm='HS256')
    return token


def jwt_auth_user(jwt_token):
    payload = jwt.decode(jwt_token, 'secret', algorithm='HS256')
    print(payload)
    try:
        user = User.objects.get(id=payload['user_id'])
    except:
        user = None
    return user
