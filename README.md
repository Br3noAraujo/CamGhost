# 🕵️‍♂️ CamGhost: Stealthy Webcam Privacy Toolkit

![CamGhost Banner](https://i.imgur.com/Ppf1hFc.png)

> "Not every eye sees. Not every camera captures. Some just... obey."

---

## 👁️‍🗨️ What is CamGhost?

**CamGhost** is a cross-platform, hacker-style CLI tool for ultimate webcam privacy and control. Hide, monitor, or wipe your webcam traces with a single command. Built for sysadmins, privacy freaks, and anyone who wants to keep Big Brother out of their lens.

- ⚡ **No bloat**: Only Python 3, colorama, psutil. No web, no GUI, no nonsense.
- 🦾 **Root required** for device control/monitoring. Wipe mode is user-level.
- 🦑 **Unix/cyberpunk aesthetic**: All output is colorized, direct, and practical.

---

## 🔥 Features

- 🕳️ **Ghost Mode**: Instantly disables (hides) all `/dev/video*` devices. No app can see your cam.
- 🕶️ **Restore**: Bring your cam back with a single flag.
- 🛰️ **Monitor Mode**: See which processes are accessing your webcam in real time.
- 🧹 **Wipe Mode**: Securely delete webcam-related logs and configs (Zoom, OBS, Teams, etc).
- 📝 **Logging**: Optional detailed logs to `camghost.log`.
- 🦾 **Cross-platform**: Linux/macOS (optimized for Linux).

---

## 🚀 Installation

```sh
python3 -m pip install colorama psutil
# Or let CamGhost install for you:
python3 camghost.py --install-deps
```

---

## 🛠️ Usage

```sh
python3 camghost.py --mode <ghost|monitor|wipe> [options]
```

### 📖 Help

```sh
python3 camghost.py -h
```

---

## 🕳️ Ghost Mode

Disable all `/dev/video*` devices instantly (root required):

```sh
sudo python3 camghost.py --mode ghost
```

![Ghost Mode Example](https://i.imgur.com/qPOIGl7.png)

---

## 🕶️ Restore Mode

Restore all webcam devices (root required):

```sh
sudo python3 camghost.py --mode ghost --restore
```

![Restore Example](https://i.imgur.com/lnTk7Ff.png)

---

## 🛰️ Monitor Mode

Monitor which processes access your webcam (root required):

```sh
sudo python3 camghost.py --mode monitor
# Or specify a device:
sudo python3 camghost.py --mode monitor --device /dev/video1
```

![Monitor Example](https://i.imgur.com/L77orQx.png)

---

## 🧹 Wipe Mode

Securely delete webcam-related logs and configs (no root needed):

```sh
python3 camghost.py --mode wipe
```

---

## 💡 Tips & Troubleshooting

- Run as **root** for ghost/monitor modes: `sudo python3 camghost.py ...`
- Use `--log` for detailed logs: `python3 camghost.py --mode ghost --log`
- If you see `device busy`, close all apps using the webcam and try again.
- If `permission denied`, run as root.
- For more info, check `camghost.log`.
- CamGhost is cross-platform but **optimized for Linux**.

---

## 🏴‍☠️ Hacker Tip

> Use CamGhost before video calls, in public spaces, or whenever you want to vanish from the digital eye. Stay invisible. Stay free.

---

## 👤 Author

- By [Br3noAraujo](https://github.com/Br3noAraujo)

---

## 📜 License

MIT. Free as in freedom. Hack the planet. 