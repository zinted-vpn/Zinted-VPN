from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import base64
import binascii
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
SOURCES_FILE = ROOT / "sources.txt"
OUTPUT_FILE = ROOT / "Zinted VPN.txt"

TIMEOUT = 20


def fetch(url):
    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 Zinted-VPN-Updater"
        }
    )

    with urlopen(req, timeout=TIMEOUT) as response:
        return response.read().decode("utf-8", errors="ignore")


def decode_base64(text):
    compact = "".join(text.split())

    try:
        raw = base64.b64decode(compact + "=" * (-len(compact) % 4))
        decoded = raw.decode("utf-8", errors="ignore")

        # Возвращаем результат только если это действительно похоже
        # на список конфигураций.
        if any(
            x in decoded
            for x in (
                "vmess://",
                "vless://",
                "trojan://",
                "ss://",
                "socks://",
                "http://",
                "https://",
            )
        ):
            return decoded
    except (binascii.Error, ValueError):
        pass

    return text


def clean_lines(text):
    text = decode_base64(text)

    result = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        if line.startswith("#"):
            continue

        result.append(line)

    return result


def main():
    if not SOURCES_FILE.exists():
        raise FileNotFoundError("sources.txt not found")

    sources = []

    for line in SOURCES_FILE.read_text(
        encoding="utf-8"
    ).splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        sources.append(line)

    all_configs = []
    failed = []

    for url in sources:
        try:
            print(f"Downloading: {url}")

            text = fetch(url)
            configs = clean_lines(text)

            print(f"  received: {len(configs)} lines")

            all_configs.extend(configs)

        except (HTTPError, URLError, TimeoutError, Exception) as e:
            print(f"  FAILED: {e}")
            failed.append(url)

    # Убираем дубликаты, сохраняя порядок.
    unique_configs = list(dict.fromkeys(all_configs))

    if not unique_configs:
        raise RuntimeError(
            "No configurations were downloaded. "
            "Existing subscription was not replaced."
        )

    header = (
        "#profile-title: Zinted VPN\n"
        f"#updated: {datetime.now(timezone.utc).isoformat()}\n"
        f"#sources: {len(sources)}\n"
        f"#configs: {len(unique_configs)}\n"
        "\n"
    )

    OUTPUT_FILE.write_text(
        header + "\n".join(unique_configs) + "\n",
        encoding="utf-8"
    )

    print()
    print(f"Sources: {len(sources)}")
    print(f"Configurations: {len(unique_configs)}")
    print(f"Failed sources: {len(failed)}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
