# yt-queue

If you spend time in the Linux terminal, you know the FOSS ecosystem has top notch backends and great TUIs. However, the UX for queueing unrelated videos dynamically is a nightmare of duct-tape solutions, frozen terminals, manual sockets, and deprecated scripts. And frankly, not a fuck has been given to this issue so far.

yt-queue solves this (or tries to). It acts as an interactive, continuous prompt that bridges `ytfzf` and `mpv`'s native IPC. 

Search, queue, and keep searching. No freezes. No manual sockets. No hacks.

## System Requirements
You only need the core terminal tools installed on your system:
- `mpv` (The media player)
- `ytfzf` (The search UI)
- `yt-dlp` (The extractor engine)

This does not try to do anything on its own. It just glues together preexisting robust tools seamlessly.

**On Arch Linux:**
```bash
sudo pacman -S mpv ytfzf yt-dlp
````
