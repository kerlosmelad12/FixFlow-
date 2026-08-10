from string import Template

EXTRACTION_SYSTEM_PROMPT = Template("\n".join([
    "أنت مساعد متخصص في تحليل أخطاء البرمجة.",
    "استخرج معلومات منظّمة من رسائل الأخطاء البرمجية أو الأسئلة التقنية.",
    "أرجع فقط JSON صالح، بدون أي شرح، وبدون تنسيق Markdown، وبدون أي نص إضافي.",
    "استخدم صيغة الإخراج والأمثلة التالية لتوجيه عملية الاستخراج.",
]))

EXTRACTION_INSTRUCTIONS_TEMPLATE = Template("\n".join([
    'Output format:',
    '{',
    '  "error_title": "عنوان قصير وواضح يلخّص الخطأ (10 كلمات كحد أقصى)",',
    '  "tags": ["lowercase", "technical", "keywords"],',
    '  "error_type": "one of: syntax_error, runtime_error, dependency_conflict, import_error, configuration_error, network_error, database_error, type_error, value_error, timeout_error, build_error, plugin_error, unknown",',
    '  "error_signature": "فقط سطر/أسطر الخطأ الأساسية، بحد أقصى 20 كلمة. لا تُضمّن الكود المحيط أو ملفات الإعداد أو أي سياق — فقط رسالة الخطأ نفسها مع استبدال أي معرّفات عشوائية بـ <ID>"',
    '}',
]))

EXAMPLES_TEMPLATE = Template("\n".join([
    'أمثلة:',
    '',
    'مثال 1:',
    'Text: "npm ERR! peer dep missing: react@^18.0.0, cannot resolve module"',
    'Output: {"error_title": "NPM Peer Dependency Missing for React", "tags": ["npm", "react", "javascript", "dependency-conflict"], "error_type": "dependency_conflict", "error_signature": "npm ERR! peer dep missing: react, cannot resolve module"}',
    '',
    'مثال 2:',
    'Text: "No signature of method: build_ap86oam3dut3pxce3x49rdtma.android() is applicable for argument types"',
    'Output: {"error_title": "Gradle Build Error: No Signature for android() Method", "tags": ["android", "gradle", "build-config"], "error_type": "build_error", "error_signature": "No signature of method: <ID>.android() is applicable for argument types"}',
    '',
    'مثال 3:',
    'Text: "ImportError: No module named pandas in virtualenv"',
    'Output: {"error_title": "ImportError: pandas Module Not Found in Virtualenv", "tags": ["python", "pandas", "importerror", "virtualenv"], "error_type": "import_error", "error_signature": "ImportError: No module named pandas in virtualenv"}',
]))


USER_PROMPT_TEMPLATE = Template("\n".join([
    'Text: "$cleaned_text"',
    '',
    'Output:',
]))
