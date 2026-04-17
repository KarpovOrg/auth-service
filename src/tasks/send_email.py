from core.config import settings

from core.httpx import httpx_client

from core.taskiq import broker


@broker.task(
    task_name="send_email_confirmation",
    max_retries=3,
    retry_delay=5,
)
async def send_email_confirmation(
        email_to: str,
        otp_code: str,
):
    html = f"<p>Ваш код подтверждения: <b>{otp_code}</b></p>"
    text = f"Ваш код подтверждения: {otp_code}"

    await httpx_client.post(
        url="https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {settings.resend.api_key}",
            "Content-Type": "application/json",
        },
        json={
            "from": settings.resend.from_email,
            "to": [email_to],
            "subject": "Код подтверждения",
            "html": html,
            "text": text,
        },

    )