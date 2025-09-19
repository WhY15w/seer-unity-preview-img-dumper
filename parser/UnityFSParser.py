import UnityPy
import os

base_dir = os.path.dirname(__file__)
config_path = os.path.join(
    base_dir, "..", "DefaultPackage", "game_ui_activitylistpreview"
)
export_dir = os.path.join(base_dir, "..", "img")
os.makedirs(export_dir, exist_ok=True)

env = UnityPy.load(config_path)
for obj in env.objects:
    if obj.type.name in ["Sprite"]:
        data = obj.read()
        if not data.m_Name.startswith("000"):
            continue
        path = os.path.join(export_dir, "preview.png")
        data.image.save(path)
