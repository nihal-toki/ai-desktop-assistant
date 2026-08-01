from pynput import keyboard

def on_activate():
    print("hotkey pressed")

def for_canonical(f):
    return lambda k: f(l.canonical(k))

hotkey = keyboard.HotKey(
    keyboard.HotKey.parse('<cmd>+<shift>+a'),
    on_activate
)

l = keyboard.Listener(
    on_press=for_canonical(hotkey.press),
    on_release=for_canonical(hotkey.release)
)

print("Listening for Cmd+Shift+A... (press Ctrl+C in terminal to stop)")
l.start()
l.join()