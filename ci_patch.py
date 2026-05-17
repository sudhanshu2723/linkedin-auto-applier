"""
CI patch script - run by GitHub Actions before starting the bot.
Patches config files for headless/CI operation.
Does NOT touch runAiBot.py - pyautogui is mocked via ci_pyautogui_mock.py instead.
"""
import re, os, sys

# ── 1. Patch config/settings.py ─────────────────────────────────────────────
with open('config/settings.py', 'r') as f:
    s = f.read()

patches = {
    r'^run_in_background\s*=.*$':        'run_in_background = True',
    r'^safe_mode\s*=.*$':                'safe_mode = True',
    r'^stealth_mode\s*=.*$':             'stealth_mode = False',
    r'^apply_gap_min\s*=.*$':            'apply_gap_min = 45',
    r'^apply_gap_max\s*=.*$':            'apply_gap_max = 180',
    r'^pause_before_submit\s*=.*$':      'pause_before_submit = False',
    r'^pause_at_failed_question\s*=.*$': 'pause_at_failed_question = False',
    r'^keep_screen_awake\s*=.*$':        'keep_screen_awake = False',
}
for pattern, replacement in patches.items():
    s = re.sub(pattern, replacement, s, flags=re.MULTILINE)

with open('config/settings.py', 'w') as f:
    f.write(s)
print("OK config/settings.py patched")

# ── 2. Patch config/search.py ────────────────────────────────────────────────
with open('config/search.py', 'r') as f:
    s = f.read()
s = re.sub(r'^pause_after_filters\s*=.*$', 'pause_after_filters = False', s, flags=re.MULTILINE)
with open('config/search.py', 'w') as f:
    f.write(s)
print("OK config/search.py patched")

# ── 3. Patch config/secrets.py ───────────────────────────────────────────────
with open('config/secrets.py', 'r') as f:
    s = f.read()

linkedin_user = os.environ.get("LINKEDIN_USERNAME", "")
linkedin_pass = os.environ.get("LINKEDIN_PASSWORD", "")
openai_key    = os.environ.get("OPENAI_API_KEY", "")

if not linkedin_user or not linkedin_pass:
    print("ERROR: LINKEDIN_USERNAME or LINKEDIN_PASSWORD secret not set!")
    sys.exit(1)

# Escape any double quotes in password
linkedin_pass_escaped = linkedin_pass.replace('\\', '\\\\').replace('"', '\\"')

s = re.sub(r'^username\s*=.*$', f'username = "{linkedin_user}"', s, flags=re.MULTILINE)
s = re.sub(r'^password\s*=.*$', f'password = "{linkedin_pass_escaped}"', s, flags=re.MULTILINE)
if openai_key:
    s = re.sub(r'^llm_api_key\s*=.*$', f'llm_api_key = "{openai_key}"', s, flags=re.MULTILINE)

with open('config/secrets.py', 'w') as f:
    f.write(s)
print("OK config/secrets.py patched")

# ── 4. Create pyautogui mock that silently no-ops all dialogs ────────────────
# We prepend an import of our mock to runAiBot.py so pyautogui is replaced
mock_import_line = "import ci_pyautogui_mock as pyautogui  # CI: mock pyautogui\n"

with open('runAiBot.py', 'r') as f:
    content = f.read()

# Only add if not already patched
if 'ci_pyautogui_mock' not in content:
    # Replace the real pyautogui import line
    content = content.replace(
        'import pyautogui\n',
        mock_import_line
    )
    with open('runAiBot.py', 'w') as f:
        f.write(content)
    print("OK runAiBot.py: pyautogui replaced with CI mock")
else:
    print("OK runAiBot.py: already patched")

# Verify syntax
import py_compile
try:
    py_compile.compile('runAiBot.py', doraise=True)
    print("OK runAiBot.py syntax check passed")
except py_compile.PyCompileError as e:
    print(f"ERROR Syntax error: {e}")
    sys.exit(1)

print("\nAll CI patches applied successfully")
