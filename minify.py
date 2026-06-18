import re

INPUT  = '/sessions/sleepy-focused-babbage/mnt/outputs/support-assistant-prototype.html'
OUTPUT = '/sessions/sleepy-focused-babbage/mnt/outputs/widget_min.html'

with open(INPUT, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Extract Google Fonts link tag from <head>
fonts_match = re.search(r'<link\s[^>]*fonts\.googleapis\.com[^>]*>', html)
fonts_tag = fonts_match.group(0) if fonts_match else ''

# 2. Extract full <style>...</style> block from <head>
style_match = re.search(r'(<style>.*?</style>)', html, re.DOTALL)
style_block = style_match.group(1) if style_match else ''

# 3. Extract content between <body> and </body>
body_match = re.search(r'<body>(.*?)</body>', html, re.DOTALL)
body_content = body_match.group(1) if body_match else ''

# 4. Pull out <script> blocks before whitespace-collapsing HTML,
#    so JS string literals are not mangled.
script_placeholder = '\x00SCRIPT{}\x00'
scripts = []

def save_script(m):
    idx = len(scripts)
    scripts.append(m.group(0))
    return script_placeholder.format(idx)

body_no_scripts = re.sub(r'<script[\s\S]*?</script>', save_script, body_content)

# 5. Strip HTML comments from the non-script portion
body_no_scripts = re.sub(r'<!--.*?-->', '', body_no_scripts, flags=re.DOTALL)

# 6. Collapse whitespace/newlines to single spaces in HTML
body_no_scripts = re.sub(r'\s+', ' ', body_no_scripts).strip()

# 7. Restore <script> blocks verbatim
for i, script in enumerate(scripts):
    body_no_scripts = body_no_scripts.replace(script_placeholder.format(i), script)

# 8. Collapse whitespace inside the style block (no JS — safe)
style_collapsed = re.sub(r'\s+', ' ', style_block).strip()

# 9. Assemble final output
result = fonts_tag + '\n' + style_collapsed + '\n' + body_no_scripts

with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write(result)

import os
size = os.path.getsize(OUTPUT)
print(f'widget_min.html created successfully.')
print(f'File size: {size} bytes ({size/1024:.1f} KB)')
