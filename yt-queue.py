#!/usr/bin/env python3
import os, sys, socket, json, subprocess, shutil, time, readline

UID = getattr(os, "getuid", lambda: 1000)()
DIR = os.environ.get("XDG_RUNTIME_DIR", f"/tmp/mpv_yt_{UID}")
os.makedirs(DIR, mode=0o700, exist_ok=True)
SOCK = os.path.join(DIR, "ipc.sock")

def ping():
    if not os.path.exists(SOCK): return False
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.connect(SOCK)
        return True
    except socket.error:
        os.remove(SOCK)
        return False

def ensure():
    if ping(): return
    subprocess.Popen(
        [
            "mpv", "--idle=yes", "--force-window", f"--input-ipc-server={SOCK}",
            "--cache=yes", "--demuxer-max-bytes=512M", "--demuxer-max-back-bytes=512M"
        ],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL,
        start_new_session=True
    )
    for _ in range(50):
        if ping(): return
        time.sleep(0.05)
    sys.exit("Error: mpv IPC binding failed.")

def ipc(cmd):
    ensure()
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.connect(SOCK)
            s.sendall((json.dumps({"command": cmd}) + "\n").encode())
    except socket.error as e:
        sys.exit(f"IPC Error: {e}")

def main():
    for c in ("mpv", "ytfzf"):
        if not shutil.which(c): sys.exit(f"Missing: {c}")

    if not sys.stdin.isatty():
        for line in sys.stdin:
            if u := line.strip(): ipc(["loadfile", u, "append-play"])
        return

    cache = {}
    binds = {
        ">": ["playlist-next"],
        "<": ["playlist-prev"],
        " ": ["cycle", "pause"],
        "c": ["playlist-clear"],
        "s": ["stop"]
    }

    while True:
        try:
            if not (q := input("> ").strip()): continue
            if q in ("q", "quit", "exit"): break
            if q in binds:
                ipc(binds[q])
                continue

            urls = [q] if q.startswith(("http://", "https://")) else cache.get(q)
            if not urls:
                urls = subprocess.run(["ytfzf", "-L", q], stdout=subprocess.PIPE, text=True).stdout.strip().splitlines()
                if urls: cache[q] = urls

            for u in urls or []:
                if u:
                    ipc(["loadfile", u, "append-play"])
                    print(f"+ {u}")

        except (KeyboardInterrupt, EOFError):
            print()
            break

if __name__ == "__main__":
    main()
