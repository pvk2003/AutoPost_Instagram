import requests, re
from PIL import Image

def convert_google_drive(url: str) -> str:
    """
    Convert nhiều dạng Google Drive URL thành link tải trực tiếp.
    """
    # Dạng 1: /file/d/FILEID/view
    match = re.search(r"/d/([^/]+)/", url)
    if match:
        return f"https://drive.google.com/uc?export=download&id={match.group(1)}"

    # Dạng 2: uc?id=FILEID&export=download (đã đúng)
    match = re.search(r"id=([^&]+)", url)
    if match:
        return f"https://drive.google.com/uc?export=download&id={match.group(1)}"

    return url


def download_image(url, filename="post.jpg"):
    url = convert_google_drive(url)
    print("🔗 Final image URL:", url)

    response = requests.get(url, allow_redirects=True)

    if response.status_code != 200:
        raise Exception(f"Failed to download image: HTTP {response.status_code}")

    content = response.content

    # Check ảnh thật
    if not (content.startswith(b"\xff\xd8") or content.startswith(b"\x89PNG")):
        print("❌ File tải về không phải ảnh!")
        print("🔍 Header:", content[:50])
        raise Exception("Downloaded file is not an image. Check your URL.")

    with open(filename, "wb") as f:
        f.write(content)

    # Convert ảnh thành vuông
    make_square(filename)

    return filename

def make_square(image_path, min_size=1080, fill_color=(0, 0, 0)):
    img = Image.open(image_path)
    x, y = img.size
    size = max(min_size, x, y)
    new_img = Image.new("RGB", (size, size), fill_color)
    new_img.paste(img, ((size - x) // 2, (size - y) // 2))
    
    new_img.save(image_path)
    return image_path