"""Secret scrubbing — never let tokens/keys reach the frontend, logs, or job events."""
from __future__ import annotations
import re
from pathlib import Path
from config import RAYA_DIR

_PATTERNS = [
    re.compile(r"(?i)(x-api-key['\"]?\s*[:=]\s*['\"]?)([A-Za-z0-9._\-]{12,})"),
    re.compile(r"(?i)(bearer\s+)([A-Za-z0-9._\-]{12,})"),
    re.compile(r"\b(sk_[A-Za-z0-9._\-]{8,})\b"),
    re.compile(r"\b(raya_[A-Za-z0-9]{8,})\b"),
    re.compile(r"\b(BAP_[A-Za-z0-9._\-]{8,})\b"),
    re.compile(r"\b(jobs_[A-Za-z0-9]{16,})\b"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----"),
]

# literal secret values from raya/.env, scrubbed exactly
_LITERALS: list[str] = []


def _load_literals():
    if _LITERALS:
        return
    env = RAYA_DIR / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                v = line.split("=", 1)[1].strip().strip('"').strip("'")
                if len(v) >= 8 and not v.startswith(("http://", "https://")):
                    _LITERALS.append(v)


def scrub(text) -> str:
    if text is None:
        return text
    if not isinstance(text, str):
        text = str(text)
    _load_literals()
    for lit in _LITERALS:
        text = text.replace(lit, "‹redacted›")
    for pat in _PATTERNS:
        if pat.groups >= 2:
            text = pat.sub(lambda m: m.group(1) + "‹redacted›", text)
        else:
            text = pat.sub("‹redacted›", text)
    return text
