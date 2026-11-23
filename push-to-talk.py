#!/usr/bin/env python3
import json, selectors, signal, subprocess, sys, time
import evdev
from evdev import ecodes

KEY = ecodes.KEY_CAPSLOCK
DN = subprocess.DEVNULL
TICK = 1.0  # segundos entre reaplicações / checagens

# (flag do pgrep, padrão)
#  -xi : nome exato do processo, sem diferenciar maiúsculas
#  -f  : regex na linha de comando completa
APPS = [
    ("-xi", "discord"),
    ("-f", r"electron.* /usr/lib/stoat-desktop/app\.asar"),  # Stoat (Electron)
]

def log(msg):
    print(msg, flush=True)

def appRunning():
    return any(
        subprocess.run(["pgrep", flag, pat], stdout=DN).returncode == 0
        for flag, pat in APPS
    )

def sourceIds():
    """IDs de todos os nós Audio/Source (mic físico + Easy Effects Source)."""
    try:
        out = subprocess.run(["pw-dump"], capture_output=True, text=True, timeout=3).stdout
        nodes = json.loads(out)
    except Exception:
        return []
    ids = []
    for n in nodes:
        if n.get("type") != "PipeWire:Interface:Node":
            continue
        props = n.get("info", {}).get("props", {})
        if props.get("media.class", "").startswith("Audio/Source"):
            ids.append(n["id"])
    return ids

def mute(ids, m):
    for i in ids:
        subprocess.run(["wpctl", "set-mute", str(i), "1" if m else "0"],
                       stdout=DN, stderr=DN)

ids = sourceIds()

def cleanup(*a):
    mute(sourceIds() or ids, False)
    sys.exit(0)

signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)

sel = selectors.DefaultSelector()
seen = set()  # caminhos /dev/input/event* já verificados

def scanDevices():
    """Registra teclados novos (hotplug). Chamado no início e a cada TICK."""
    paths = set(evdev.list_devices())
    seen.intersection_update(paths)  # esquece os que sumiram
    for p in paths - seen:
        seen.add(p)
        try:
            d = evdev.InputDevice(p)
        except OSError:
            continue
        if KEY in d.capabilities().get(ecodes.EV_KEY, []):
            sel.register(d, selectors.EVENT_READ)
            log(f"teclado: {d.name} ({p})")
        else:
            d.close()

def dropDevice(d):
    seen.discard(d.path)
    try:
        sel.unregister(d)
    except Exception:
        pass
    try:
        d.close()
    except Exception:
        pass
    log(f"desconectado: {d.path}")

scanDevices()
log("push-to-talk iniciado")

active = False   # app de voz aberto -> PTT ligado
pressed = False  # tecla segurada
lastCheck = 0

try:
    while True:
        now = time.time()
        if now - lastCheck > TICK:
            lastCheck = now
            running = appRunning()
            scanDevices()      # pega teclados conectados depois
            ids = sourceIds()  # atualiza (EasyEffects pode recriar os nós)
            if running != active:
                active = running
                pressed = False
                mute(ids, active)       # liga: começa mutado / desliga: desmuta
            elif active:
                mute(ids, not pressed)  # reaplica, caso algo tenha revertido

        for item, mask in sel.select(timeout=TICK):
            try:
                events = list(item.fileobj.read())
            except BlockingIOError:
                continue
            except OSError:  # teclado desconectado
                dropDevice(item.fileobj)
                continue
            for e in events:
                if active and e.type == ecodes.EV_KEY and e.code == KEY and e.value in (0, 1):
                    pressed = (e.value == 1)
                    mute(ids, not pressed)
finally:
    mute(ids, False)
