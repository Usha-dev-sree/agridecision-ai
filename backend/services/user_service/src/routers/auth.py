
from backend.services.user_service.src.dependencies import get_db, get_redis
from backend.services.user_service.src.repositories.session_repository import SessionRepository
from backend.services.user_service.src.repositories.subscription_repository import (
    SubscriptionRepository,
)
from backend.services.user_service.src.repositories.user_repository import UserRepository
from backend.services.user_service.src.schemas.auth import (
    ForgotPasswordRequest,
    LoginPasswordRequest,
    OTPRequest,
    OTPVerify,
    RegisterRequest,
    RequestEmailVerificationRequest,
    ResetPasswordRequest,
    TokenResponse,
    VerifyEmailRequest,
    VerifyResetTokenRequest,
)
from backend.services.user_service.src.services.auth_service import AuthService
from fastapi import APIRouter, Depends, Form, Query, Request, status
from fastapi.responses import HTMLResponse
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/v1/auth", tags=["Authentication"])


def get_auth_service(
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> AuthService:
    user_repo = UserRepository(session)
    session_repo = SessionRepository(session, redis)
    sub_repo = SubscriptionRepository(session)
    return AuthService(user_repo, session_repo, sub_repo, redis_client=redis)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    request: Request,
    register_data: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new user with unique email/phone validation and permanent persistence."""
    return await auth_service.register_user(register_data, request)


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login_with_password(
    request: Request,
    login_data: LoginPasswordRequest | None = None,
    username: str | None = Form(None),
    password: str | None = Form(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Authenticate user via phone or email and password (supports JSON and Form input)."""
    identifier = (login_data.username or login_data.phone_number or login_data.email) if login_data else username
    pwd = login_data.password if login_data else password
    device_fp = login_data.device_fingerprint if login_data else None

    if not identifier or not pwd:
        from backend.common.exceptions import BadRequestException
        raise BadRequestException(detail="Username/phone/email and password are required.")

    return await auth_service.login_with_password(
        identifier=identifier, password=pwd, request=request, device_fingerprint=device_fp
    )


@router.post("/request-otp", status_code=status.HTTP_200_OK)
async def request_otp(
    request_data: OTPRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Request an OTP for login or registration."""
    otp_code = await auth_service.request_otp(request_data.phone_number)
    return {"message": "OTP sent successfully", "debug_otp": otp_code}


@router.post("/verify-otp", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def verify_otp(
    request: Request,
    verify_data: OTPVerify,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Verify OTP and issue JWT tokens."""
    return await auth_service.verify_otp(
        phone_number=verify_data.phone_number,
        otp_code=verify_data.otp_code,
        request=request,
        device_fingerprint=verify_data.device_fingerprint
    )


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    req: ForgotPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Request password reset code or link."""
    return await auth_service.request_forgot_password(req.email_or_phone)


@router.post("/verify-reset-token", status_code=status.HTTP_200_OK)
async def verify_reset_token(
    req: VerifyResetTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Verify password reset code or token."""
    return await auth_service.verify_reset_token(req.token)


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    req: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Reset user password using valid token."""
    return await auth_service.reset_password(req.token, req.new_password)


@router.post("/request-email-verification", status_code=status.HTTP_200_OK)
async def request_email_verification(
    req: RequestEmailVerificationRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Generate and send email verification link."""
    return await auth_service.request_email_verification(req.email)


@router.get("/verify-email", status_code=status.HTTP_200_OK)
@router.post("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(
    token: str | None = Query(None),
    req: VerifyEmailRequest | None = None,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Verify user's email address."""
    token_val = token or (req.token if req else None)
    if not token_val:
        from backend.common.exceptions import BadRequestException
        raise BadRequestException(detail="Verification token is required.")
    return await auth_service.verify_email(token_val)


# UI HTML Endpoints
@router.get("/ui/verify-email.html", response_class=HTMLResponse)
async def verify_email_ui(token: str | None = Query(None)):
    """Serves interactive HTML UI for email verification."""
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Verification - AgriDecision AI</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Plus Jakarta Sans', sans-serif; }}
        body {{
            background: linear-gradient(135deg, #07150e 0%, #0d2818 50%, #041009 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ecfdf5;
            padding: 20px;
        }}
        .card {{
            background: rgba(16, 37, 26, 0.75);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(52, 211, 153, 0.2);
            border-radius: 24px;
            padding: 40px;
            max-width: 480px;
            width: 100%;
            text-align: center;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
        }}
        .icon {{
            width: 72px; height: 72px;
            background: rgba(16, 185, 129, 0.15);
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            margin: 0 auto 24px;
            color: #34d399; font-size: 32px;
            border: 1px solid rgba(52, 211, 153, 0.3);
        }}
        h1 {{ font-size: 26px; font-weight: 700; margin-bottom: 12px; color: #ffffff; }}
        p {{ font-size: 15px; color: #a7f3d0; margin-bottom: 28px; line-height: 1.6; }}
        .input-group {{ margin-bottom: 20px; text-align: left; }}
        label {{ display: block; font-size: 13px; font-weight: 600; color: #6ee7b7; margin-bottom: 8px; }}
        input {{
            width: 100%; padding: 14px 18px;
            background: rgba(5, 20, 12, 0.6);
            border: 1px solid rgba(52, 211, 153, 0.3);
            border-radius: 12px; color: #fff; font-size: 15px;
            outline: none; transition: border-color 0.2s;
        }}
        input:focus {{ border-color: #34d399; box-shadow: 0 0 0 3px rgba(52, 211, 153, 0.2); }}
        .btn {{
            width: 100%; padding: 14px;
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            border: none; border-radius: 12px; color: white;
            font-size: 16px; font-weight: 600; cursor: pointer;
            transition: all 0.2s; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4);
        }}
        .btn:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(16, 185, 129, 0.6); }}
        .status {{
            margin-top: 20px; padding: 14px; border-radius: 12px; font-size: 14px; display: none;
        }}
        .status.success {{ background: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; color: #34d399; display: block; }}
        .status.error {{ background: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444; color: #fca5a5; display: block; }}
    </style>
</head>
<body>
    <div class="card">
        <div class="icon">✓</div>
        <h1>Email Verification</h1>
        <p>Verify your AgriDecision AI account email address to enable access to smart agricultural insights.</p>
        
        <div class="input-group">
            <label for="token">Verification Token</label>
            <input type="text" id="token" placeholder="Paste verification token here..." value="{token or ''}">
        </div>
        
        <button class="btn" onclick="verifyToken()">Verify Email Address</button>
        <div id="statusBox" class="status"></div>
    </div>

    <script>
        async function verifyToken() {{
            const token = document.getElementById('token').value.trim();
            const statusBox = document.getElementById('statusBox');
            if (!token) {{
                statusBox.className = 'status error';
                statusBox.innerText = 'Please enter a valid verification token.';
                return;
            }}
            statusBox.className = 'status';
            statusBox.innerText = 'Verifying...';
            try {{
                const res = await fetch('/v1/auth/verify-email?token=' + encodeURIComponent(token), {{ method: 'GET' }});
                const data = await res.json();
                if (res.ok) {{
                    statusBox.className = 'status success';
                    statusBox.innerText = data.message || 'Email successfully verified!';
                }} else {{
                    statusBox.className = 'status error';
                    statusBox.innerText = data.detail || 'Verification failed. Token may be invalid or expired.';
                }}
            }} catch (err) {{
                statusBox.className = 'status error';
                statusBox.innerText = 'Network error. Please try again.';
            }}
        }}
        if ("{token or ''}".length > 5) {{
            verifyToken();
        }}
    </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)


@router.get("/ui/reset-password.html", response_class=HTMLResponse)
async def reset_password_ui(token: str | None = Query(None)):
    """Serves interactive HTML UI for password reset."""
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reset Password - AgriDecision AI</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Plus Jakarta Sans', sans-serif; }}
        body {{
            background: linear-gradient(135deg, #07150e 0%, #0d2818 50%, #041009 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ecfdf5;
            padding: 20px;
        }}
        .card {{
            background: rgba(16, 37, 26, 0.75);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(52, 211, 153, 0.2);
            border-radius: 24px;
            padding: 40px;
            max-width: 480px;
            width: 100%;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
        }}
        .header {{ text-align: center; margin-bottom: 28px; }}
        .icon {{
            width: 72px; height: 72px;
            background: rgba(16, 185, 129, 0.15);
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            margin: 0 auto 20px;
            color: #34d399; font-size: 32px;
            border: 1px solid rgba(52, 211, 153, 0.3);
        }}
        h1 {{ font-size: 26px; font-weight: 700; color: #ffffff; margin-bottom: 8px; }}
        p {{ font-size: 14px; color: #a7f3d0; line-height: 1.5; }}
        .input-group {{ margin-bottom: 20px; text-align: left; }}
        label {{ display: block; font-size: 13px; font-weight: 600; color: #6ee7b7; margin-bottom: 8px; }}
        input {{
            width: 100%; padding: 14px 18px;
            background: rgba(5, 20, 12, 0.6);
            border: 1px solid rgba(52, 211, 153, 0.3);
            border-radius: 12px; color: #fff; font-size: 15px;
            outline: none; transition: border-color 0.2s;
        }}
        input:focus {{ border-color: #34d399; box-shadow: 0 0 0 3px rgba(52, 211, 153, 0.2); }}
        .btn {{
            width: 100%; padding: 14px;
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            border: none; border-radius: 12px; color: white;
            font-size: 16px; font-weight: 600; cursor: pointer;
            transition: all 0.2s; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4);
            margin-top: 10px;
        }}
        .btn:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(16, 185, 129, 0.6); }}
        .status {{
            margin-top: 20px; padding: 14px; border-radius: 12px; font-size: 14px; display: none; text-align: center;
        }}
        .status.success {{ background: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; color: #34d399; display: block; }}
        .status.error {{ background: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444; color: #fca5a5; display: block; }}
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <div class="icon">🔒</div>
            <h1>Reset Your Password</h1>
            <p>Enter your reset token and your new account password below.</p>
        </div>
        
        <div class="input-group">
            <label for="token">Reset Token or Code</label>
            <input type="text" id="token" placeholder="Enter reset token or code..." value="{token or ''}">
        </div>

        <div class="input-group">
            <label for="password">New Password</label>
            <input type="password" id="password" placeholder="Enter new password (min 6 chars)">
        </div>

        <div class="input-group">
            <label for="confirmPassword">Confirm Password</label>
            <input type="password" id="confirmPassword" placeholder="Confirm new password">
        </div>
        
        <button class="btn" onclick="submitReset()">Update Password</button>
        <div id="statusBox" class="status"></div>
    </div>

    <script>
        async function submitReset() {{
            const token = document.getElementById('token').value.trim();
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            const statusBox = document.getElementById('statusBox');

            if (!token) {{
                statusBox.className = 'status error';
                statusBox.innerText = 'Please enter a valid reset token or code.';
                return;
            }}
            if (!password || password.length < 6) {{
                statusBox.className = 'status error';
                statusBox.innerText = 'Password must be at least 6 characters long.';
                return;
            }}
            if (password !== confirmPassword) {{
                statusBox.className = 'status error';
                statusBox.innerText = 'Passwords do not match.';
                return;
            }}

            statusBox.className = 'status';
            statusBox.innerText = 'Updating password...';

            try {{
                const res = await fetch('/v1/auth/reset-password', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ token: token, new_password: password }})
                }});
                const data = await res.json();
                if (res.ok) {{
                    statusBox.className = 'status success';
                    statusBox.innerText = data.message || 'Password reset successfully! You can now log in.';
                }} else {{
                    statusBox.className = 'status error';
                    statusBox.innerText = data.detail || 'Failed to reset password.';
                }}
            }} catch (err) {{
                statusBox.className = 'status error';
                statusBox.innerText = 'Network error. Please try again.';
            }}
        }}
    </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)
