import smtplib
from email.mime.text import MIMEText
from app.config import settings


def send_email(to_email: str, subject: str, body: str):
    """
    이메일 전송 함수
    """
    smtp_server = settings.smtp_server
    smtp_port = settings.smtp_port
    sender_email = settings.smtp_user  # 발신자 이메일
    sender_password = settings.smtp_password  # 발신자 이메일 비밀번호
    # 이메일 메시지 작성
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    try:
        # SMTP 연결
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.set_debuglevel(1)  # 디버깅 활성화
            server.starttls()  # TLS 보안 활성화
            server.login(sender_email, sender_password)  # 로그인
            print("[DEBUG] SMTP 로그인 성공")

            # 이메일 전송
            server.sendmail(sender_email, to_email, msg.as_string())
            print("[DEBUG] 이메일 전송 성공")

    except smtplib.SMTPAuthenticationError as e:
        print("불러온이메일페스워드", settings.smtp_user,sender_password)

        print("[ERROR] SMTP 인증 실패: 이메일 또는 비밀번호를 확인하세요.")
        print(f"[DEBUG] 상세 정보: {e}")
        raise
    except smtplib.SMTPException as e:
        print("[ERROR] SMTP 오류 발생")
        print(f"[DEBUG] 상세 정보: {e}")
        raise
    finally:
        print("[DEBUG] 이메일 전송 프로세스 종료")
