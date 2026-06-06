import UnityPy
import os

base_dir = os.path.dirname(__file__)
config_path = os.path.join(
    base_dir, "..", "DefaultPackage", "game_ui_activitylistpreview"
)
export_dir = os.path.join(base_dir, "..", "img")
os.makedirs(export_dir, exist_ok=True)
# 删除该目录下的所有文件
for filename in os.listdir(export_dir):
    file_path = os.path.join(export_dir, filename)
    if os.path.isfile(file_path):
        os.remove(file_path)

env = UnityPy.load(config_path)

idx = 0
for obj in env.objects:
    if obj.type.name != "Sprite" and obj.type.name != "Texture2D":
        continue

    data = obj.read()
    name = data.m_Name

    #if not (name.isdigit() or name.startswith("sactx")):
        #continue
    path = os.path.join(export_dir, f"{name}.png")
    data.image.save(path)
