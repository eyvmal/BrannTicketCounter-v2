import os
from atproto import Client
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
bs_username = os.environ.get("BLUESKY_USERNAME")
bs_handle = os.environ.get("BLUESKY_HANDLE")
bs_password = os.environ.get("BLUESKY_PASSWORD")


def create_bluesky_skeet(text, media_path):
    print("Creating Skeet...")
    client = Client()
    client.login(bs_handle, bs_password)

    images_data = []
    for path in media_path:
        with open(path, 'rb') as f:
            images_data.append(f.read())
            
    client.send_images(text=text, images=images_data)


def main():
    create_bluesky_skeet("Test", ["clubs/brann/picture0.png"])

if __name__ == '__main__':
    main()