import os
import UnityPy

base_dir = os.path.dirname(__file__)

config_path = os.path.join(
    base_dir,
    "..",
    "DefaultPackage",
    "game_ui_activitylistpreview",
)

export_dir = os.path.join(base_dir, "..", "img")
os.makedirs(export_dir, exist_ok=True)

for filename in os.listdir(export_dir):
    file_path = os.path.join(export_dir, filename)
    if os.path.isfile(file_path):
        os.remove(file_path)

env = UnityPy.load(config_path)

object_map = {obj.path_id: obj for obj in env.objects}

export_count = 0

for obj in env.objects:
    if obj.type.name != "GameObject":
        continue
    try:
        go = obj.read()
    except Exception:
        continue
    if not go.m_Name.startswith("imgPreview"):
        continue

    print(f"Processing: {go.m_Name} {go.m_IsActive}")

    # 只处理激活的
    if not go.m_IsActive:
        print("  Skipped (inactive)")
        continue

    for component in go.m_Component:
        reader = component.component
        if reader.type.name != "MonoBehaviour":
            continue
        try:
            tree = reader.read_typetree()
        except Exception:
            continue

        sprite_info = tree.get("m_Sprite")

        if not sprite_info:
            continue

        sprite_path_id = sprite_info.get("m_PathID", 0)

        if not sprite_path_id:
            continue

        sprite_obj = object_map.get(sprite_path_id)

        if not sprite_obj:
            print(f"  Sprite not found: {sprite_path_id}")
            continue
        try:
            sprite = sprite_obj.read()
            image = sprite.image
            output_path = os.path.join(export_dir, f"{go.m_Name}.png")
            image.save(output_path)
            export_count += 1
        except Exception as e:
            print(f"  Export failed: {e}")
        break
