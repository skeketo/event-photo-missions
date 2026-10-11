import os
import pyotp
from fastapi import Request
from fastapi.responses import RedirectResponse

SESSION_COOKIE = "event_photo_admin_session"


def admin_user():
    return os.getenv("ADMIN_USER", "admin")


def admin_password():
    return os.getenv("ADMIN_PASSWORD", "admin")


def admin_2fa_secret():
    return os.getenv("ADMIN_2FA_SECRET", "")


def verify_login(username, password, token):
    if username != admin_user():
        return False

    if password != admin_password():
        return False

    secret = admin_2fa_secret().strip()

    # If no TOTP secret is configured, 2FA is disabled.
    # This makes first-run setup easier for Docker/Unraid users.
    if not secret:
        return True

    if not token:
        return False

    totp = pyotp.TOTP(secret)
    return totp.verify(token, valid_window=1)


def is_admin_logged(request: Request):
    return request.cookies.get(SESSION_COOKIE) == os.getenv("SECRET_KEY", "change-me")


def require_admin(request: Request):
    if not is_admin_logged(request):
        return RedirectResponse("/admin/login", status_code=303)
    return None


def login_response():
    response = RedirectResponse("/admin", status_code=303)
    response.set_cookie(
        key=SESSION_COOKIE,
        value=os.getenv("SECRET_KEY", "change-me"),
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 8,
    )
    return response


def logout_response():
    response = RedirectResponse("/admin/login", status_code=303)
    response.delete_cookie(SESSION_COOKIE)
    return response


def provisioning_uri():
    secret = admin_2fa_secret()
    if not secret:
        return ""

    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(
        name=admin_user(),
        issuer_name="Event Photo Missions"
    )

def provisioning_qr_base64():
    import base64
    import io
    import qrcode

    uri = provisioning_uri()
    if not uri:
        return ""

    img = qrcode.make(uri)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")

    return base64.b64encode(buffer.getvalue()).decode("ascii")
