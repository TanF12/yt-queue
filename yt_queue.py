#!/usr/bin/env python3
import os, sys, socket, json, subprocess, shutil, time, readline

UID = getattr(os, "getuid", lambda: 1000)()
SOCK = os.path.join(os.environ.get("XDG_RUNTIME_DIR", f"/tmp/mpv_yt_{UID}"), "ipc.sock")
os.makedirs(os.path.dirname(SOCK), mode=0o700, exist_ok=True)

def ping():
    if not os.path.exists(SOCK):
        return False
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.connect(SOCK)
        return True
    except OSError:
        try:
            os.remove(SOCK)
        except OSError:
            pass
        return False

def ensure():
    if ping():
        return
    subprocess.Popen(
        [
            "mpv", "--idle=yes", "--force-window", f"--input-ipc-server={SOCK}",
            "--cache=yes", "--demuxer-max-bytes=512M", "--demuxer-max-back-bytes=512M"
        ],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL,
        start_new_session=True
    )
    for _ in range(50):
        if ping():
            return
        time.sleep(0.05)
    sys.exit("Error: mpv IPC binding failed.")

def ipc(cmd):
    ensure()
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.connect(SOCK)
            s.sendall(json.dumps({"command": cmd}).encode() + b"\n")
    except OSError as e:
        sys.exit(f"IPC Error: {e}")

def main():
    for c in ("mpv", "ytfzf"):
        if not shutil.which(c):
            sys.exit(f"Missing: {c}")
    if not sys.stdin.isatty():
        for line in sys.stdin:
            if u := line.strip():
                ipc(["loadfile", u, "append-play"])
        return
    idx = 1
    history = {}
    binds = {
        ">": ["playlist-next"],
        "<": ["playlist-prev"],
        " ": ["cycle", "pause"],
        "c": ["playlist-clear"],
        "s": ["stop"]
    }
    while True:
        try:
            if not (q := input("> ").strip()):
                continue
            if q in ("q", "quit", "exit"):
                break
            if q in binds:
                ipc(binds[q])
                continue
            if q.isdigit() and (i := int(q)) in history:
                urls = [history[i]]
            else:
                urls = [q] if q.startswith(("http://", "https://")) else subprocess.run(["ytfzf", "-L", q], stdout=subprocess.PIPE, text=True).stdout.strip().splitlines()
            for u in urls or []:
                if u:
                    history[idx] = u
                    ipc(["loadfile", u, "append-play"])
                    print(f"[{idx}] + {u}")
                    idx += 1
        except (KeyboardInterrupt, EOFError):
            print()
            break

if __name__ == "__main__":
    main()
