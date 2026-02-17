# PDF417 Text Encoder — AI Workbench Project

Runs on your DGX Spark (Sparky) via NVIDIA AI Workbench.
Paste text into the browser, get a sequence of PDF417 barcodes for
air-gap data transfer to your isolated machine.

---

## Expected location on Sparky

```
/home/jparks/nvidia-workbench/pdf417-workbench/
├── .project/
│   └── spec.yaml
├── code/
│   └── app.py
├── postBuild.bash
└── README.md
```

---

### 1. Launch the app

docker run -d \
  -p 8888:8888 \
  -v /home/jparks/nvidia-workbench/pdf417-workbench:/project \
  --restart unless-stopped \
  --name pdf417 \
  python:3.11-slim \
  bash -c "pip install flask pdf417gen pillow -q && python3 /project/code/app.py"


### 6. Access from isolated machine

```
http://<sparky-ip>:8888
```

Find Sparky's IP with: `hostname -I`

---

## Barcode format

| Property        | Value                         |
|----------------|-------------------------------|
| Symbology       | PDF417                        |
| Columns         | 8                             |
| Security level  | 2 (medium error correction)   |
| Max chars/chunk | ~1,180                        |
| Sequence prefix | `[NNN/TOTAL]` (3-digit padded)|
| Image format    | PNG                           |

---


The app is now running as a Docker container on Sparky, completely independent of AI Workbench. Your isolated machine can reach it at http://192.168.1.218:8888 any time it wants.
What Workbench was doing wrong for your use case — Workbench is designed for a developer sitting at Sparky using its own browser. It deliberately proxies all web apps through its own internal URL (localhost:10000/...) rather than exposing ports directly to the LAN. That's great for development workflows but completely incompatible with what you need — a LAN-accessible web server reachable from a separate machine.
What Docker does differently — the -p 8888:8888 flag directly bridges Sparky's LAN port 8888 to the container's port 8888, so any machine on the network can reach it.
The --restart unless-stopped flag means the container will automatically come back up if Sparky reboots, so you don't have to manually start it each time.
A few things worth knowing going forward:

To stop the app: docker stop pdf417
To start it again: docker start pdf417
To see if it's running: docker ps
To see its logs: docker logs pdf417


Your workflow for updates going forward:
bashcd /home/jparks/nvidia-workbench/pdf417-workbench

# 1. Edit app.py however you like

# 2. Rebuild the image
docker build -t pdf417 .

# 3. Swap the running container
docker stop pdf417 && docker rm pdf417
docker run -d -p 8888:8888 --restart unless-stopped --name pdf417 pdf417
