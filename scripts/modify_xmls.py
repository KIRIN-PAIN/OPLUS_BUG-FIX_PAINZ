import os
import xml.etree.ElementTree as ET
import zipfile
import shutil
import sys

INPUT_ZIP = "permissions.zip"
OUTPUT_DIR = "output"
EXTRACTED_DIR = "permission_patched"
ZIP_OUT = "patched_permission.zip"

TARGETS = {
    "oplus.feature.android.xml": {
        "remove": [
            "oplus.software.vibrator_qcom_lmvibrator",
            "oplus.software.vibrator_lmvibrator",
            "oplus.software.vibrator_richctap",
            "oplus.hardware.vibrator_oplus_v1",
        ],
        "add": [
            "oplus.hardware.vibrator_xlinear_type",
            "oplus.software.haptic_vibrator_v1.support",
        ],
        "tag": "oplus-feature"
    },
    "com.oppo.features_allnet_android.xml": {
        "remove": [
            "oppo.hardware.fingerprint.optical.support",
            "android.hardware.biometrics.face",
            "oppo.common.support.curved.display",
            "oppo.breeno.three.words.support"
        ],
        "add": [],
        "tag": "feature"
    },
    "oplus.product.display_features.xml": {
        "remove": [
            "oplus.software.fingeprint_optical_enabled",
            "oplus.software.display.screen_heteromorphism"
        ],
        "add": [],
        "tag": "oplus-feature"
    },
    "oplus.product.feature_multimedia_unique.xml": {
        "remove": [
            "oplus.software.audio.alert_slider",
            "oplus.software.video.osie_support",
            "oplus.software.audio.voice_wakeup_support"
        ],
        "add": [],
        "tag": "oplus-feature"
    }
}

def process_file(path, rules, output_path):
    print(f"📂 Parsing: {path}")
    try:
        tree = ET.parse(path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"❌ Skipping file '{path}' due to parse error: {e}")
        return

    tagname = rules["tag"]

    for elem in list(root):
        if elem.tag == tagname and elem.attrib.get("name") in rules["remove"]:
            root.remove(elem)

    existing = {e.attrib.get("name") for e in root if e.tag == tagname}
    for name in rules["add"]:
        if name not in existing:
            ET.SubElement(root, tagname, {"name": name})

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)


if not os.path.isfile(INPUT_ZIP):
    print("❌ permissions.zip not found.")
    sys.exit(1)

shutil.rmtree(EXTRACTED_DIR, ignore_errors=True)
shutil.rmtree(OUTPUT_DIR, ignore_errors=True)

with zipfile.ZipFile(INPUT_ZIP, 'r') as zip_ref:
    zip_ref.extractall(".")

if not os.path.isdir(EXTRACTED_DIR):
    print("❌ 'permissions' folder not found inside ZIP.")
    sys.exit(1)

for file, rule in TARGETS.items():
    input_path = os.path.join(EXTRACTED_DIR, file)
    output_path = os.path.join(OUTPUT_DIR, EXTRACTED_DIR, file)

    if os.path.isfile(input_path):
        process_file(input_path, rule, output_path)
    else:
        print(f"⚠️ File not found: {file} — skipping.")

for root_dir, dirs, files in os.walk(EXTRACTED_DIR):
    for file in files:
        rel_path = os.path.relpath(os.path.join(root_dir, file), EXTRACTED_DIR)
        dst_path = os.path.join(OUTPUT_DIR, EXTRACTED_DIR, rel_path)
        if not os.path.exists(dst_path):
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            shutil.copy2(os.path.join(root_dir, file), dst_path)

shutil.make_archive(ZIP_OUT.replace(".zip", ""), 'zip', os.path.join(OUTPUT_DIR, EXTRACTED_DIR))
print(f"✅ Done. Output zip: {ZIP_OUT}")

ZIP_NAME = "patched_permission"
OUTPUT_DIR = os.path.join(OUTPUT_DIR, EXTRACTED_DIR)

if os.path.exists(OUTPUT_DIR):
    shutil.make_archive(ZIP_NAME, 'zip', OUTPUT_DIR)
    print(f"✅ Done. Output zip: {ZIP_NAME}.zip")
else:
    print(f"❌ Output directory not found: {OUTPUT_DIR}")

