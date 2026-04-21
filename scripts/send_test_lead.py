import argparse
import json
import os
import random
import smtplib
import ssl
import sys
import time
import uuid
from pathlib import Path
from datetime import datetime, UTC
from email.message import EmailMessage
from email.utils import formataddr


FIRST_NAMES = [
    "John",
    "Emily",
    "Michael",
    "Sarah",
    "David",
    "Anna",
    "Daniel",
    "Olivia",
    "Robert",
    "Julia",
]

LAST_NAMES = [
    "Carter",
    "Miller",
    "Wilson",
    "Clark",
    "Lewis",
    "Walker",
    "Young",
    "Hall",
    "Allen",
    "King",
]

COMPANIES = [
    "BrightPath Logistics",
    "Northstar Dental",
    "Vertex Legal Group",
    "BluePeak Realty",
    "Summit Home Services",
    "Atlas Staffing",
    "Oakline Medical",
    "Pulse Commerce",
    "Greenfield Finance",
    "Apex Manufacturing",
]

SERVICES = [
    "n8n lead routing",
    "CRM integration",
    "Gmail automation",
    "Telegram alerts",
    "AI lead qualification",
    "proposal automation",
    "webhook integration",
    "sales pipeline automation",
]

BUDGETS = [
    "$1,500 - $3,000",
    "$3,000 - $5,000",
    "$5,000 - $10,000",
    "$10,000+",
]

TIMELINES = [
    "this week",
    "within 2 weeks",
    "this month",
    "next month",
]

PAIN_POINTS = [
    "we are losing leads because nobody responds fast enough",
    "our team manually copies emails into the CRM",
    "lead qualification is slow and inconsistent",
    "we need instant notifications when a qualified lead arrives",
    "our current process breaks when multiple requests arrive together",
]


def env_or_default(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def load_config_file(config_path: str) -> dict:
    path = Path(config_path)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Config file must contain a JSON object: {path}")
    return data


def resolve_config_path(argv: list[str]) -> str:
    default_path = str(Path(__file__).with_name("config.json"))
    for index, arg in enumerate(argv):
        if arg == "--config" and index + 1 < len(argv):
            return argv[index + 1]
        if arg.startswith("--config="):
            return arg.split("=", 1)[1]
    return default_path


def random_identity() -> dict:
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    company = random.choice(COMPANIES)
    domain = company.lower().replace(" ", "").replace("-", "") + ".com"
    lead_email = f"{first.lower()}.{last.lower()}{random.randint(10, 99)}@{domain}"
    services = random.sample(SERVICES, k=random.randint(2, 4))
    budget = random.choice(BUDGETS)
    timeline = random.choice(TIMELINES)
    pain_point = random.choice(PAIN_POINTS)
    phone = f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
    return {
        "first": first,
        "last": last,
        "name": f"{first} {last}",
        "company": company,
        "email": lead_email,
        "phone": phone,
        "services": services,
        "budget": budget,
        "timeline": timeline,
        "pain_point": pain_point,
    }


def build_message(to_email: str, smtp_user: str, subject_prefix: str = "Lead Test") -> EmailMessage:
    person = random_identity()
    request_id = uuid.uuid4().hex[:8]
    now_utc = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

    subject = (
        f"{subject_prefix} | {person['company']} | "
        f"{random.choice(['Automation', 'CRM', 'Lead Intake', 'Workflow'])} | {request_id}"
    )

    body = f"""Hello,

We are looking for help with automation for our company.

Name: {person['name']}
Email: {person['email']}
Phone: {person['phone']}
Company: {person['company']}
Budget: {person['budget']}
Timeline: {person['timeline']}
Services Needed: {", ".join(person['services'])}

Message:
We need help with {person['services'][0]} and {person['services'][1]}.
Right now {person['pain_point']}.
Please let us know if you can build this in n8n and connect it with our CRM.

Meta:
Generated-At: {now_utc}
Request-Id: {request_id}
Source: Python SMTP test script
"""

    msg = EmailMessage()
    msg["To"] = to_email
    msg["From"] = formataddr((person["name"], smtp_user))
    msg["Reply-To"] = person["email"]
    msg["Subject"] = subject
    msg["X-Test-Lead"] = "1"
    msg.set_content(body)
    return msg


def create_ssl_context(insecure: bool) -> ssl.SSLContext:
    if insecure:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context
    return ssl.create_default_context()


def send_message(
    host: str,
    port: int,
    user: str,
    password: str,
    to_email: str,
    use_ssl: bool,
    subject_prefix: str,
    insecure_tls: bool,
) -> str:
    msg = build_message(to_email=to_email, smtp_user=user, subject_prefix=subject_prefix)
    context = create_ssl_context(insecure_tls)

    if use_ssl:
        with smtplib.SMTP_SSL(host, port, context=context, timeout=30) as server:
            server.login(user, password)
            server.send_message(msg)
    else:
        with smtplib.SMTP(host, port, timeout=30) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(user, password)
            server.send_message(msg)

    return msg["Subject"]

def parse_args() -> argparse.Namespace:
    config_path = resolve_config_path(sys.argv[1:])
    config = load_config_file(config_path)

    def cfg(name: str, env_name: str, default=""):
        if name in config and config[name] not in (None, ""):
            return config[name]
        return env_or_default(env_name, default)

    parser = argparse.ArgumentParser(
        description="Send random lead-test emails to exercise the n8n Gmail Trigger workflow."
    )
    parser.add_argument("--config", default=config_path)
    parser.add_argument("--to", default=cfg("TEST_TO_EMAIL", "TEST_TO_EMAIL"))
    parser.add_argument("--smtp-host", default=cfg("SMTP_HOST", "SMTP_HOST", "smtp.gmail.com"))
    parser.add_argument("--smtp-port", type=int, default=int(str(cfg("SMTP_PORT", "SMTP_PORT", "587"))))
    parser.add_argument("--smtp-user", default=cfg("SMTP_USER", "SMTP_USER"))
    parser.add_argument("--smtp-pass", default=cfg("SMTP_PASS", "SMTP_PASS"))
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--delay-sec", type=float, default=2.0)
    parser.add_argument("--subject-prefix", default="Lead Test")
    parser.add_argument("--ssl", action="store_true", help="Use implicit SSL instead of STARTTLS.")
    parser.add_argument(
        "--insecure",
        action="store_true",
        default=str(cfg("SMTP_INSECURE_TLS", "SMTP_INSECURE_TLS", "")).lower() in {"1", "true", "yes", "y"},
        help="Disable TLS certificate verification for SMTP. Use only for local testing.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    required = {
        "to": args.to,
        "smtp_user": args.smtp_user,
        "smtp_pass": args.smtp_pass,
        "smtp_host": args.smtp_host,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        print(
            "Missing required values: "
            + ", ".join(missing)
            + ". Set CLI args or env vars TEST_TO_EMAIL / SMTP_HOST / SMTP_PORT / SMTP_USER / SMTP_PASS.",
            file=sys.stderr,
        )
        return 2

    for index in range(args.count):
        subject = send_message(
            host=args.smtp_host,
            port=args.smtp_port,
            user=args.smtp_user,
            password=args.smtp_pass,
            to_email=args.to,
            use_ssl=args.ssl,
            subject_prefix=args.subject_prefix,
            insecure_tls=args.insecure,
        )
        print(f"[{index + 1}/{args.count}] sent: {subject}")
        if index < args.count - 1:
            time.sleep(args.delay_sec)

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
