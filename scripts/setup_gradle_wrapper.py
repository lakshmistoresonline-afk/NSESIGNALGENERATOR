import os
import zipfile
import subprocess
from pathlib import Path

os.environ["ANDROID_HOME"] = r"C:\Users\srina\AppData\Local\Android\Sdk"
os.environ["ANDROID_SDK_ROOT"] = r"C:\Users\srina\AppData\Local\Android\Sdk"

root = Path(__file__).resolve().parents[1]
zip_path = root / "gradle-8.9-bin.zip"
dist_dir = root / ".gradle-dist"
android_dir = root / "android"

if not zip_path.exists():
    raise RuntimeError("gradle-8.9-bin.zip not found")

if not dist_dir.exists():
    print("Extracting Gradle 8.9...")
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(dist_dir)

gradle_bat = None
for p in dist_dir.glob("**/bin/gradle.bat"):
    gradle_bat = p
    break

if not gradle_bat or not gradle_bat.exists():
    raise RuntimeError("Could not find gradle.bat in extracted distribution")

print(f"Found gradle.bat at: {gradle_bat}")

wrapper_dir = android_dir / "gradle" / "wrapper"
wrapper_dir.mkdir(parents=True, exist_ok=True)
props = """distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-8.9-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
"""
(wrapper_dir / "gradle-wrapper.properties").write_text(props, encoding="utf-8")

print("Generating Gradle wrapper in android/...")
cmd = [str(gradle_bat), "wrapper", "--gradle-version", "8.9", "--distribution-type", "bin"]
res = subprocess.run(cmd, cwd=str(android_dir), capture_output=True, text=True, env=os.environ)
print("STDOUT:", res.stdout)
print("STDERR:", res.stderr)
print("Exit code:", res.returncode)

if res.returncode == 0:
    print("Gradle wrapper generated successfully!")
else:
    print("Failed to generate Gradle wrapper")
