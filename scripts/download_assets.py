import os
import urllib.request

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
    target_dir = str(ASSETS_TARGET_DIR)

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"Created directory: {target_dir}")

    print(f"Downloading chess pieces from {ASSETS_BASE_URL}...")
    for piece in ASSETS_PIECES:
        url = f"{ASSETS_BASE_URL}{piece}.png"
        save_path = os.path.join(target_dir, f"{piece}.png")

        try:
            urllib.request.urlretrieve(url, save_path)
            print(f"✔ Downloaded {piece}.png")
        except Exception as e:
            print(f"❌ Error downloading {piece}.png: {e}")


if __name__ == "__main__":
    download_assets()
