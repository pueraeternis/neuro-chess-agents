import urllib.request
from urllib.parse import urlparse

from src.config import (
    ASSETS_BASE_URL,
    ASSETS_PIECES,
    ASSETS_TARGET_DIR,
    ASSETS_USER_AGENT,
)

opener = urllib.request.build_opener()
opener.addheaders = [("User-agent", ASSETS_USER_AGENT)]
urllib.request.install_opener(opener)


def download_assets():
    target_dir = ASSETS_TARGET_DIR

    if not target_dir.exists():
        target_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {target_dir}")

    print(f"Downloading chess pieces from {ASSETS_BASE_URL}...")
    for piece in ASSETS_PIECES:
        url = f"{ASSETS_BASE_URL}{piece}.png"
        save_path = target_dir / f"{piece}.png"

        try:
            parsed = urlparse(url)
            if parsed.scheme not in {"http", "https"}:
                raise ValueError(f"Refusing to download from non-HTTP(S) URL: {url}")

            urllib.request.urlretrieve(url, save_path)  # noqa: S310 - scheme is validated above
            print(f"✔ Downloaded {piece}.png")
        except Exception as e:
            print(f"❌ Error downloading {piece}.png: {e}")


if __name__ == "__main__":
    download_assets()
