"""
CI mock for pyautogui - replaces all dialog calls with no-ops.
Used in GitHub Actions where there is no display for dialog boxes.
"""

FAILSAFE = False

def alert(*args, **kwargs):
    """No-op alert - just log it."""
    text = kwargs.get('text', args[0] if args else '')
    title = kwargs.get('title', '')
    print(f"[CI-MOCK] pyautogui.alert suppressed: {title}: {str(text)[:100]}")
    return None

def confirm(*args, **kwargs):
    """Auto-confirm - return the last button (Continue/OK)."""
    text = kwargs.get('text', args[0] if args else '')
    title = kwargs.get('title', '')
    buttons = kwargs.get('buttons', args[2] if len(args) > 2 else ['OK'])
    # Return last button to continue execution
    result = buttons[-1] if buttons else 'OK'
    print(f"[CI-MOCK] pyautogui.confirm suppressed: {title} -> returning '{result}'")
    return result

def prompt(*args, **kwargs):
    return ''

def password(*args, **kwargs):
    return ''

# Stub out all other pyautogui functions that might be called
def hotkey(*args, **kwargs): pass
def press(*args, **kwargs): pass
def typewrite(*args, **kwargs): pass
def click(*args, **kwargs): pass
def moveTo(*args, **kwargs): pass
def scroll(*args, **kwargs): pass
def screenshot(*args, **kwargs): return None
def locateOnScreen(*args, **kwargs): return None
def size(): return (1920, 1080)
def position(): return (0, 0)
