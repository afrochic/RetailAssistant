"""Client-name redaction for the approved distribution snapshot (not full de-identification)."""
import re


def public_text(value: str, private_terms=()) -> str:
    text = str(value or '')
    # Remove URLs before replacing configured names, including image/source links.
    text = re.sub(r'https?://[^\s<>"\']+', '[link withheld]', text, flags=re.I)
    for term in sorted(filter(None, private_terms), key=len, reverse=True):
        text = re.sub(re.escape(term), 'Client X', text, flags=re.I)
    return text
