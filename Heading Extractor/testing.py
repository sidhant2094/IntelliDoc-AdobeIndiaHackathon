import os
import json
import time

VALID_LEVELS = {"H1", "H2", "H3","H4"}

def validate_json_structure(data, filename):
    errors = []
    
    # Title check
    if "title" not in data or not isinstance(data["title"], str):
        errors.append("Missing or invalid 'title'")

    if "outline" not in data or not isinstance(data["outline"], list):
        errors.append("Missing or invalid 'outline'")

    # Outline entry checks
    for idx, entry in enumerate(data.get("outline", [])):
        if not all(k in entry for k in ("level", "text", "page")):
            errors.append(f"Outline entry {idx} missing keys")
        if entry.get("level") not in VALID_LEVELS:
            errors.append(f"Invalid heading level: {entry.get('level')}")
        if not isinstance(entry.get("page"), int) or entry["page"] <= 0:
            errors.append(f"Invalid page number in entry {idx}")
        if not isinstance(entry.get("text"), str) or len(entry["text"]) < 2:
            errors.append(f"Invalid heading text in entry {idx}")
    
    if errors:
        print(f"❌ Validation failed for {filename}:\n" + "\n".join(["  - " + e for e in errors]))
    else:
        print(f"✅ {filename} passed all validations")
    return len(errors) == 0


def validate_all_outputs(output_dir):
    json_files = [f for f in os.listdir(output_dir) if f.endswith(".json")]
    if not json_files:
        print("⚠️  No JSON files found in output directory.")
        return False

    all_passed = True
    for file in json_files:
        with open(os.path.join(output_dir, file), "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                passed = validate_json_structure(data, file)
                if not passed:
                    all_passed = False
            except Exception as e:
                print(f"❌ Failed to parse {file}: {e}")
                all_passed = False
    return all_passed


def measure_speed(pdf_path, process_fn):
    start = time.time()
    process_fn(pdf_path)
    end = time.time()
    elapsed = end - start
    print(f"⏱️  Execution time for {os.path.basename(pdf_path)}: {elapsed:.2f}s")
    if elapsed > 10.0:
        print("⚠️  WARNING: Exceeds 10s constraint!")
    else:
        print("✅ Execution time within limit")


# Optional standalone usage
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="D:\\AdobeHackthon\\AdobeIndiaHackthon\\Round 1A\\outputs", help="Path to output JSON dir")
    args = parser.parse_args()

    print("🧪 Validating all outputs...")
    result = validate_all_outputs(args.out)
    print("✅ All outputs valid" if result else "❌ Some outputs failed validation.")
