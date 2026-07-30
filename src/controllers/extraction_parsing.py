import json
import re
from typing import Optional



REQUIRED_FIELDS = {"error_title", "tags", "error_type", "error_signature"}


def extract_first_json_object(raw_text: str) -> Optional[str]:

    start = raw_text.find("{")
    if start == -1:
        return None

    depth = 0
    for i in range(start, len(raw_text)):
        char = raw_text[i]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return raw_text[start:i + 1]

    return None 


def parse_extraction_output(raw_output: str) -> dict:

    json_str = extract_first_json_object(raw_output)

    if json_str is None:
        return {
            "success": False,
            "data": None,
            "error": "No valid JSON object found in model output (possibly truncated)"
        }

    try:
        parsed = json.loads(json_str)
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "data": None,
            "error": f"JSON decode failed: {str(e)}"
        }

    missing = REQUIRED_FIELDS - parsed.keys()
    if missing:
        return {
            "success": False,
            "data": parsed,
            "error": f"Missing required fields: {missing}"
        }

    data = {field: parsed[field] for field in REQUIRED_FIELDS}

    return {
        "success": True,
        "data": data,
    }