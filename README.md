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

## Setup

### 1. Extract the zip to the right place

```bash
cd /home/jparks/nvidia-workbench/
unzip pdf417-workbench.zip
# Folder will be: /home/jparks/nvidia-workbench/pdf417-workbench/
```

### 2. Initialize as a Git repo (required by AI Workbench)

```bash
cd /home/jparks/nvidia-workbench/pdf417-workbench
git init
git add .
git commit -m "Initial commit: PDF417 encoder"
```

### 3. Open in AI Workbench

- Open the AI Workbench desktop app
- Select **Local** on the My Locations screen
- Click **Open Local Project** (or Add Existing)
- Browse to: `/home/jparks/nvidia-workbench/pdf417-workbench`
- Workbench detects `.project/spec.yaml` and registers the project

### 4. Build

Workbench will build the container and run `postBuild.bash` automatically,
which installs `flask`, `pdf417gen`, and `pillow`.

### 5. Launch the app

Go to **Environment → Applications → PDF417 Encoder → Start**

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

## Reassembly script (run on isolated machine)

```python
import re

# Paste decoded barcode strings here, one per line
raw_scans = [
    "[001/003] First chunk of text...",
    "[002/003] Second chunk...",
    "[003/003] Final chunk.",
]

chunks = {}
for scan in raw_scans:
    m = re.match(r'\[(\d+)/(\d+)\] (.*)', scan, re.DOTALL)
    if m:
        idx, payload = int(m.group(1)), m.group(3)
        chunks[idx] = payload

result = ''.join(chunks[k] for k in sorted(chunks))
print(result)
```