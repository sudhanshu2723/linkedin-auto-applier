"""
CI patch script - run by GitHub Actions before starting the bot.
Patches runAiBot.py and config files for headless/CI operation.
"""
import re, sys, py_compile

# ── 1. Patch config/settings.py ─────────────────────────────────────────────
with open('config/settings.py', 'r') as f:
    s = f.read()

patches = {
    r'^run_in_background\s*=.*$':       'run_in_background = True',
    r'^safe_mode\s*=.*$':               'safe_mode = True',
    r'^stealth_mode\s*=.*$':            'stealth_mode = False',
    r'^apply_gap_min\s*=.*$':           'apply_gap_min = 45',
    r'^apply_gap_max\s*=.*$':           'apply_gap_max = 180',
    r'^pause_before_submit\s*=.*$':     'pause_before_submit = False',
    r'^pause_at_failed_question\s*=.*$':'pause_at_failed_question = False',
    r'^keep_screen_awake\s*=.*$':       'keep_screen_awake = False',
}
for pattern, replacement in patches.items():
    s = re.sub(pattern, replacement, s, flags=re.MULTILINE)

with open('config/settings.py', 'w') as f:
    f.write(s)
print("✅ config/settings.py patched")

# ── 2. Patch config/search.py ────────────────────────────────────────────────
with open('config/search.py', 'r') as f:
    s = f.read()
s = re.sub(r'^pause_after_filters\s*=.*$', 'pause_after_filters = False', s, flags=re.MULTILINE)
with open('config/search.py', 'w') as f:
    f.write(s)
print("✅ config/search.py patched")

# ── 3. Patch config/secrets.py ───────────────────────────────────────────────
import os
with open('config/secrets.py', 'r') as f:
    s = f.read()
s = re.sub(r'^username\s*=.*$', f'username = "{os.environ["LINKEDIN_USERNAME"]}"', s, flags=re.MULTILINE)
s = re.sub(r'^password\s*=.*$', f'password = "{os.environ["LINKEDIN_PASSWORD"]}"', s, flags=re.MULTILINE)
s = re.sub(r'^llm_api_key\s*=.*$', f'llm_api_key = "{os.environ["OPENAI_API_KEY"]}"', s, flags=re.MULTILINE)
with open('config/secrets.py', 'w') as f:
    f.write(s)
print("✅ config/secrets.py patched")

# ── 4. Patch runAiBot.py - remove all pyautogui blocking calls ───────────────
with open('runAiBot.py', 'r') as f:
    s = f.read()

# Replace pyautogui.alert(...) with None - handles multiline
s = re.sub(r'pyautogui\.alert\([^)]*\)', 'None', s)

# Replace if-conditions that use pyautogui.confirm as the condition
# Pattern: if <something> and "<text>" == pyautogui.confirm(...):
s = re.sub(
    r'if pause_after_filters and[^\n]+pyautogui\.confirm[^\n]+:',
    'if False:  # CI: pause_after_filters disabled',
    s
)
s = re.sub(
    r'if errored != "stuck" and cur_pause_before_submit[^\n]+:',
    'if False:  # CI: pause_before_submit disabled',
    s
)

# Replace remaining pyautogui.confirm(...) calls with "Continue"
s = re.sub(r'pyautogui\.confirm\([^)]*\)', '"Continue"', s)

with open('runAiBot.py', 'w') as f:
    f.write(s)

# Verify syntax
try:
    py_compile.compile('runAiBot.py', doraise=True)
    print("✅ runAiBot.py patched and syntax OK")
except py_compile.PyCompileError as e:
    print(f"❌ Syntax error after patching: {e}")
    sys.exit(1)

print("\n✅ All CI patches applied successfully")
