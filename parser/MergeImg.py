from PIL import Image
import os
import re

BASE_DIR = os.path.dirname(__file__)
IMG_DIR = os.path.join(BASE_DIR, "..", "img")
OUTPUT_PATH = os.path.join(IMG_DIR, "preview.png")

MAX_WIDTH = 1024


def get_png_files():
    files = []
    for name in os.listdir(IMG_DIR):
        if not name.lower().endswith(".png"):
            continue
        if name == "preview.png":
            continue
        files.append(name)
    return sorted(files, key=sort_key)


def sort_key(name):
    base = os.path.splitext(name)[0]
    match = re.search(r"_(\d+)$", base)
    if match:
        return (0, int(match.group(1)))
    return (1, base)


def resize_if_needed(img):
    if img.width > MAX_WIDTH:
        ratio = MAX_WIDTH / img.width
        new_height = int(img.height * ratio)
        return img.resize((MAX_WIDTH, new_height), Image.LANCZOS)
    return img


def concatenate_vertical(images):
    max_width = max(img.width for img in images)
    total_height = sum(img.height for img in images)

    canvas = Image.new("RGBA", (max_width, total_height), (0, 0, 0, 0))

    y = 0
    for img in images:
        canvas.paste(img, (0, y))
        y += img.height

    return canvas


def main():
    png_files = get_png_files()

    if not png_files:
        raise RuntimeError("img 目录下没有 PNG 图片")

    if len(png_files) == 1:
        filepath = os.path.join(IMG_DIR, png_files[0])
        img = Image.open(filepath)
        canvas = resize_if_needed(img)
    else:
        images = []
        for name in png_files:
            filepath = os.path.join(IMG_DIR, name)
            images.append(Image.open(filepath))
        canvas = concatenate_vertical(images)
        canvas = resize_if_needed(canvas)

    canvas.save(OUTPUT_PATH)
    print(f"已生成 {OUTPUT_PATH}（宽度 ≤ {MAX_WIDTH}）")


if __name__ == "__main__":
    main()
