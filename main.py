import json
import os
import asyncio
from telethon import TelegramClient

from config import API_ID, API_HASH, PHONE, CHANNEL

DOWNLOAD_PATH = "downloads"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

client = TelegramClient("session", API_ID, API_HASH)

def download_video(url, key, name):
    try:
        key_value = key[0].split(":")[1]

        safe_name = name.replace("/", "-")
        output = os.path.join(DOWNLOAD_PATH, f"{safe_name}.mp4")

        cmd = f'''yt-dlp \
--allow-unplayable-formats \
--external-downloader ffmpeg \
--external-downloader-args "ffmpeg_i:-decryption_key {key_value}" \
-o "{output}" "{url}"'''

        return os.system(cmd), output

    except Exception as e:
        print("Download error:", e)
        return 1, None


async def main():
    await client.start(phone=PHONE)

    with open("videos.json", encoding="utf-8") as f:
        data = json.load(f)

    for i, item in enumerate(data, start=1):
        name = item.get("video_name", f"Video {i}")
        url = item.get("mpd_url")
        key = item.get("key")

        print(f"\nProcessing {i}: {name}")

        if not url or not key:
            print("Missing data, skipping")
            continue

        status, filepath = download_video(url, key, name)

        if status != 0 or not filepath:
            print("Download failed")
            continue

        try:
            await client.send_file(
                CHANNEL,
                filepath,
                caption=name
            )

            print("Uploaded:", name)

            os.remove(filepath)

        except Exception as e:
            print("Upload error:", e)


with client:
    client.loop.run_until_complete(main())
