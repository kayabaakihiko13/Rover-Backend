from pydantic import EmailStr
from fastapi_mail import FastMail, MessageSchema
from src.core.config import get_email_conf


async def send_reset_email(email: EmailStr, reset_link: str):
    message = MessageSchema(
        subject="Reset Password - Rover App",
        recipients=[email],
        body=f"""
        Halo,

        Klik link berikut untuk reset password:

        {reset_link}

        Link berlaku selama 15 menit.
        """,
        subtype="plain",
    )

    fm = FastMail(get_email_conf())
    await fm.send_message(message)
