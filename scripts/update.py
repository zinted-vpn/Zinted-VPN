from pathlib import Path
from datetime import datetime, timezone

FILE = Path("Zinted VPN.txt")

PINNED = {
    "🇩🇪 Германия [🔥]",
    "🇬🇧 Великобритания [#2]",
}

text = FILE.read_text(encoding="utf-8") if FILE.exists() else ""

if not text.startswith("#profile-title:"):
    text = "#profile-title: Zinted VPN\n" + text

print("Zinted VPN update:", datetime.now(timezone.utc).isoformat())
print("Pinned nodes:", ", ".join(PINNED))

FILE.write_text(text, encoding="utf-8")
