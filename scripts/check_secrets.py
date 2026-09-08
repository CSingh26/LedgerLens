"""Heuristic tracked-file scan; prints only file paths, never matched secret values."""

from pathlib import Path
import re
import subprocess

PATTERNS = [
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    r"gh[pousr]_[A-Za-z0-9]{30,}",
    r"AKIA[0-9A-Z]{16}",
    r"sk-[A-Za-z0-9]{40,}",
]
files = subprocess.check_output(["git", "ls-files", "-z"]).decode().split("\0")
failed = []
for name in files:
    path = Path(name)
    if path.is_file() and any(
        re.search(pattern, path.read_text(errors="ignore")) for pattern in PATTERNS
    ):
        failed.append(name)
if failed:
    raise SystemExit("Potential secret patterns in: " + ", ".join(failed))
print("Tracked-file secret-pattern scan passed")
