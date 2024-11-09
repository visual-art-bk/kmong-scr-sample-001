import os
import shutil
import subprocess

# 빌드할 앱의 이름과 경로를 설정합니다.
app_name = "app.exe"  # 빌드 후 생성될 파일 이름
dist_path = "dist"
app_path = os.path.join(dist_path, app_name)

# 기존 파일이 존재하는지 확인하고 백업합니다.
if os.path.exists(app_path):
    old_app_path = os.path.join(dist_path, f"old_{app_name}")
    # 이미 백업 파일이 있다면 삭제합니다.
    if os.path.exists(old_app_path):
        os.remove(old_app_path)
    # 파일 이름을 old_로 변경하여 백업합니다.
    shutil.move(app_path, old_app_path)
    print(f"기존 빌드 파일을 백업했습니다: {old_app_path}")

# PyInstaller 빌드를 수행합니다.
subprocess.run(["pyinstaller", "--noconfirm", "--onefile", "--windowed", "app.py"])

print(f"{app_name} 빌드가 완료되었습니다.")
