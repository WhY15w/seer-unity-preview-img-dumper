from PIL import Image
import os

BASE_DIR = os.path.dirname(__file__)
IMG_DIR = os.path.join(BASE_DIR, "..", "img")
OUTPUT_PATH = os.path.join(IMG_DIR, "preview.png")

MAX_WIDTH = 1024


def main():
    images = []

    for name in sorted(os.listdir(IMG_DIR)):
        if not name.lower().endswith(".png"):
            continue
        if name == "preview.png":
            continue

        images.append(Image.open(os.path.join(IMG_DIR, name)))

    if not images:
        raise RuntimeError("img 目录下没有可合并的图片")

    max_width = max(img.width for img in images)
    total_height = sum(img.height for img in images)

    canvas = Image.new("RGBA", (max_width, total_height), (0, 0, 0, 0))

    y = 0
    for img in images:
        canvas.paste(img, (0, y))
        y += img.height

    if canvas.width > MAX_WIDTH:
        ratio = MAX_WIDTH / canvas.width
        new_height = int(canvas.height * ratio)

        canvas = canvas.resize((MAX_WIDTH, new_height), Image.LANCZOS)

    canvas.save(OUTPUT_PATH)

    print(f"已生成 {OUTPUT_PATH}（宽度 ≤ {MAX_WIDTH}）")


if __name__ == "__main__":
    main()
