from PIL import Image
import os
import imagehash
import re

BASE_DIR = os.path.dirname(__file__)
IMG_DIR = os.path.join(BASE_DIR, "..", "img")
OUTPUT_PATH = os.path.join(IMG_DIR, "preview.png")

MAX_WIDTH = 1024


def is_digit_name(name):
    """检查文件名（不含扩展名）是否为纯数字"""
    base = os.path.splitext(name)[0]
    return base.isdigit()


def compute_phash(img):
    """计算图片的感知哈希"""
    if img.mode == "RGBA":
        img = img.convert("RGB")
    return imagehash.phash(img)


def main():
    sactx_groups = {}  # group_name -> [(filename, phash), ...]
    source_images = {}  # filename -> (Image, phash)
    crop_height = None

    for name in sorted(os.listdir(IMG_DIR)):
        if not name.lower().endswith(".png"):
            continue
        if name == "preview.png":
            continue

        filepath = os.path.join(IMG_DIR, name)
        img = Image.open(filepath)
        base = os.path.splitext(name)[0]

        if base.startswith("sactx-"):
            if crop_height is None:
                raise RuntimeError("未找到 000.png，无法确定裁剪高度")
            crop_img = img.crop((0, img.height - crop_height, img.width, img.height))
            match = re.match(r"(sactx-\d+)", base)
            if match:
                group = match.group(1)
                if group not in sactx_groups:
                    sactx_groups[group] = []
                sactx_groups[group].append((name, compute_phash(crop_img)))
        elif is_digit_name(name):
            source_images[name] = (img, compute_phash(img))
            if name == "000.png":
                crop_height = img.height

    if "sactx-1" not in sactx_groups:
        raise RuntimeError("未找到 sactx-1 预告图片")

    if not source_images:
        raise RuntimeError("未找到数字命名的源图片（如 000.png, 111.png）")

    # 将每个源图片匹配到 pHash 距离最近的 sactx 组
    preview_images = []

    for src_name, (src_img, src_hash) in sorted(source_images.items()):
        best_group = None
        best_diff = float("inf")
        best_sactx_name = None

        for group_name, sactx_list in sactx_groups.items():
            for sactx_name, sactx_hash in sactx_list:
                diff = src_hash - sactx_hash
                if diff < best_diff:
                    best_diff = diff
                    best_group = group_name
                    best_sactx_name = sactx_name

        print(
            f"{src_name} -> {best_sactx_name} ({best_group}), pHash diff: {best_diff}"
        )

        if best_group == "sactx-1":
            preview_images.append(src_img)

    if not preview_images:
        raise RuntimeError("未找到匹配 sactx-1 的源图片")

    # 垂直拼接匹配到的源图片
    if len(preview_images) == 1:
        canvas = preview_images[0].copy()
    else:
        max_width = max(img.width for img in preview_images)
        total_height = sum(img.height for img in preview_images)

        canvas = Image.new("RGBA", (max_width, total_height), (0, 0, 0, 0))

        y = 0
        for img in preview_images:
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
