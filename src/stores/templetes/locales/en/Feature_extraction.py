from string import Template

EXTRACTION_SYSTEM_PROMPT = Template("\n".join([
    "You are a technical error analysis assistant.",
    "Extract structured information from programming error messages or questions.",
    "Return ONLY valid JSON, no explanation, no markdown formatting, no extra text.",
    "Use the following output format and examples to guide your extraction.",
]))

EXTRACTION_INSTRUCTIONS_TEMPLATE = Template("\n".join([
    'Output format:',
    '{',
    '  "error_title": "a short, clear title summarizing the error (max 10 words)",',
    '  "tags": ["lowercase", "technical", "keywords"],',
    '  "error_type": "one of: syntax_error, runtime_error, dependency_conflict, import_error, configuration_error, network_error, database_error, type_error, value_error, timeout_error, build_error, plugin_error, unknown",',
    '  "error_signature": "ONLY the core error line(s), max 20 words. Do NOT include surrounding code, config files, or context — just the error message itself with random ids replaced by <ID>"',
    '}',
]))

EXAMPLES_TEMPLATE = Template("\n".join([
    'Examples:',
    '',
    'Example 1:',
    'Text: "npm ERR! peer dep missing: react@^18.0.0, cannot resolve module"',
    'Output: {"error_title": "NPM Peer Dependency Missing for React", "tags": ["npm", "react", "javascript", "dependency-conflict"], "error_type": "dependency_conflict", "error_signature": "npm ERR! peer dep missing: react, cannot resolve module"}',
    '',
    'Example 2:',
    'Text: "No signature of method: build_ap86oam3dut3pxce3x49rdtma.android() is applicable for argument types"',
    'Output: {"error_title": "Gradle Build Error: No Signature for android() Method", "tags": ["android", "gradle", "build-config"], "error_type": "build_error", "error_signature": "No signature of method: <ID>.android() is applicable for argument types"}',
    '',
    'Example 3:',
    'Text: "ImportError: No module named pandas in virtualenv"',
    'Output: {"error_title": "ImportError: pandas Module Not Found in Virtualenv", "tags": ["python", "pandas", "importerror", "virtualenv"], "error_type": "import_error", "error_signature": "ImportError: No module named pandas in virtualenv"}',
]))


USER_PROMPT_TEMPLATE = Template("\n".join([
    'Text: "$cleaned_text"',
    '',
    'Output:',
]))