from jwt import ExpiredSignatureError, DecodeError
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from asgiref.sync import sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model
import jwt

User = get_user_model()


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        headers = dict(scope.get("headers", []))
        auth_header = headers.get(b"authorization", b"").decode()

        scope["user"] = AnonymousUser()  # Default

        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                decoded_data = jwt.decode(
                    token,
                    settings.SIMPLE_JWT["SIGNING_KEY"],
                    algorithms=[settings.SIMPLE_JWT["ALGORITHM"]],
                )
                user_id = decoded_data.get("user_id")
                user = await self.get_user(user_id)
                scope["user"] = user

            except ExpiredSignatureError:
                scope["auth_error"] = "Token has expired."
            except DecodeError:
                scope["auth_error"] = "Invalid token signature."
            except Exception:
                scope["auth_error"] = "Authentication failed."

        return await super().__call__(scope, receive, send)

    @staticmethod
    async def get_user(user_id):
        try:
            return await sync_to_async(User.objects.get)(id=user_id)
        except User.DoesNotExist:
            return AnonymousUser()
