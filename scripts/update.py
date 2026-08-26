from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent

SOURCES_FILE = ROOT / "sources.txt"
OUTPUT_FILE = ROOT / "Zinted VPN.txt"

TIMEOUT = 20
MAX_SIZE = 5 * 1024 * 1024  # 5 MB


def download(url):
    request = Request(
        url,
        headers={
            "User-Agent": "Zinted-VPN-Updater/1.0"
        }
    )

    with urlopen(request, timeout=TIMEOUT) as response:
        data = response.read(MAX_SIZE + 1)

    if len(data) > MAX_SIZE:
        raise ValueError("source is larger than 5 MB")

    return data.decode("utf-8", errors="replace")


def load_sources():
    if not SOURCES_FILE.exists():
        raise FileNotFoundError("sources.txt not found")

    urls = []

    for line in SOURCES_FILE.read_text(
        encoding="utf-8"
    ).splitlines():

        line = line.strip()

        if not line:
            continue

        if line.startswith("#"):
            continue

        if line.startswith(("http://", "https://")):
            urls.append(line)

    return list(dict.fromkeys(urls))


def clean_text(text):
    lines = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        lines.append(line)

    return lines


def main():
    sources = load_sources()

    if not sources:
        raise RuntimeError("No valid URLs found in sources.txt")

    all_lines = []
    successful = 0

    print(f"Found {len(sources)} sources")

    for url in sources:
        try:
            print(f"Downloading: {url}")

            text = download(url)
            lines = clean_text(text)

            if lines:
                all_lines.extend(lines)
                successful += 1
                print(f"  OK: {len(lines)} lines")
            else:
                print("  EMPTY")

        except (HTTPError, URLError, TimeoutError, ValueError) as e:
            print(f"  FAILED: {e}")

        except Exception as e:
            print(f"  FAILED: {type(e).__name__}: {e}")

    if successful == 0:
        raise RuntimeError("All sources failed")

    # Удаляем дубли, сохраняя порядок.
    unique_lines = list(dict.fromkeys(all_lines))

    header = (
        "#profile-title: Zinted VPN\n"
        f"# Updated: {datetime.now(timezone.utc).isoformat()}\n"
        f"# Sources: {successful}/{len(sources)}\n"
        "\n"
    )

    OUTPUT_FILE.write_text(
        header + "\n".join(unique_lines) + "\n",
        encoding="utf-8"
    )

    print()
    print(f"Successful sources: {successful}/{len(sources)}")
    print(f"Unique entries: {len(unique_lines)}")
    print(f"Written to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
