import os
import urllib.request

# Официальный сайт - самый надежный источник
BASE_URL = "https://chessboardjs.com/img/chesspieces/wikipedia/"
PIECES = ["wP", "wN", "wB", "wR", "wQ", "wK", "bP", "bN", "bB", "bR", "bQ", "bK"]
TARGET_DIR = "static/img/chesspieces/wikipedia"

# Добавляем User-Agent, чтобы сайт не блокировал скрипт как бота
opener = urllib.request.build_opener()
opener.addheaders = [("User-agent", "Mozilla/5.0")]
urllib.request.install_opener(opener)


def download_assets():
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)
        print(f"Created directory: {TARGET_DIR}")

    print(f"Downloading chess pieces from {BASE_URL}...")
    for piece in PIECES:
        url = f"{BASE_URL}{piece}.png"
        save_path = os.path.join(TARGET_DIR, f"{piece}.png")

        try:
            urllib.request.urlretrieve(url, save_path)
            print(f"✔ Downloaded {piece}.png")
        except Exception as e:
            print(f"❌ Error downloading {piece}.png: {e}")


if __name__ == "__main__":
    download_assets()
