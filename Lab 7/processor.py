import json

def calculate_dimensional_weight(dimensions_str):
    if not isinstance(dimensions_str, str) or 'x' not in dimensions_str:
        return 0.0
    dims = dimensions_str.split('x')
    if len(dims) != 3:
        return 0.0
    try:
        length = float(dims[0])
        width = float(dims[1])
        height = float(dims[2])
        if length < 0 or width < 0 or height < 0:
            return 0.0
        return round((length * width * height) / 5000.0, 2)
    except (ValueError, TypeError):
        return 0.0

def format_tracking_label(raw_code):
    if not isinstance(raw_code, str) or not raw_code:
        return "INVALID"
    prefix = raw_code[0].upper()
    try:
        tracking_num = int(raw_code[1:])
        return f"{prefix}-{tracking_num:06d}"
    except ValueError:
        return "INVALID"

def parse_package_manifest(json_payload):
    if not isinstance(json_payload, str):
        return 0.0
    try:
        data = json.loads(json_payload)
        if isinstance(data, dict) and "weight" in data:
            return float(data["weight"])
        return 0.0
    except (json.JSONDecodeError, ValueError, TypeError):
        return 0.0

def main():
    print("==== Running calculate_dimensional_weight ====")
    dims_input = input("Enter dimensions LxWxH in cm (e.g. 20x30x10): ")
    dim_weight = calculate_dimensional_weight(dims_input)
    print("Dimensional Weight (kg):", dim_weight)

    print("\n==== Running format_tracking_label ====")
    code_input = input("Enter raw code (e.g. E123): ")
    label = format_tracking_label(code_input)
    print("Formatted Label:", label)

    print("\n==== Running parse_package_manifest ====")
    json_input = input('Enter manifest JSON (e.g. {"weight": 12.5}): ')
    weight = parse_package_manifest(json_input)
    print("Manifest Weight:", weight)

if __name__ == "__main__":
    main()