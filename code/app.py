from flask import Flask, request, jsonify
import pdf417gen
import qrcode
import io
import base64
import math
from PIL import Image

app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Barcode Encoder</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap');

  :root {
    --bg: #0d0f14;
    --surface: #161a23;
    --surface2: #1e2433;
    --border: #2a3347;
    --accent: #00e5ff;
    --accent2: #ff6b35;
    --text: #c8d6e8;
    --text-dim: #5a6a80;
    --success: #00ff88;
    --radius: 6px;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: 'Rajdhani', sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    padding: 24px;
  }

  h1 {
    font-family: 'Share Tech Mono', monospace;
    font-size: 1.4rem;
    letter-spacing: 0.15em;
    color: var(--accent);
    text-transform: uppercase;
    margin-bottom: 24px;
    border-bottom: 1px solid var(--border);
    padding-bottom: 12px;
  }

  h1 span { color: var(--accent2); }

  .layout {
    display: grid;
    grid-template-columns: 340px 1fr;
    gap: 20px;
    max-width: 1400px;
  }

  .panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px;
  }

  label {
    display: block;
    font-size: 0.75rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-dim);
    margin-bottom: 6px;
    margin-top: 16px;
  }

  label:first-child { margin-top: 0; }

  textarea {
    width: 100%;
    height: 200px;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    color: var(--text);
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem;
    padding: 10px;
    resize: vertical;
    transition: border-color 0.2s;
  }

  textarea:focus { outline: none; border-color: var(--accent); }

  /* Format toggle */
  .toggle-group {
    display: flex;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
  }

  .toggle-group input[type="radio"] { display: none; }

  .toggle-group label {
    flex: 1;
    margin: 0;
    padding: 8px 0;
    text-align: center;
    cursor: pointer;
    font-size: 0.8rem;
    letter-spacing: 0.1em;
    color: var(--text-dim);
    background: var(--bg);
    border: none;
    transition: all 0.2s;
  }

  .toggle-group input[type="radio"]:checked + label {
    background: var(--accent);
    color: #000;
    font-weight: 700;
  }

  /* Sliders */
  .slider-row {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  input[type="range"] {
    flex: 1;
    accent-color: var(--accent);
    height: 4px;
  }

  .slider-val {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.85rem;
    color: var(--accent);
    min-width: 40px;
    text-align: right;
  }

  /* Select */
  select {
    width: 100%;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    color: var(--text);
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.9rem;
    padding: 7px 10px;
  }

  select:focus { outline: none; border-color: var(--accent); }

  /* QR options - hidden by default */
  #qr-options { display: none; }

  /* Number input for chunk size */
  .chunk-row {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  input[type="number"] {
    width: 90px;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    color: var(--accent);
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.9rem;
    padding: 6px 10px;
    text-align: center;
  }

  input[type="number"]:focus { outline: none; border-color: var(--accent); }

  .chunk-hint {
    font-size: 0.75rem;
    color: var(--text-dim);
  }

  button {
    width: 100%;
    margin-top: 20px;
    padding: 12px;
    background: var(--accent);
    color: #000;
    border: none;
    border-radius: var(--radius);
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    cursor: pointer;
    transition: background 0.2s, transform 0.1s;
  }

  button:hover { background: #00cfea; }
  button:active { transform: scale(0.98); }
  button:disabled { background: var(--border); color: var(--text-dim); cursor: default; }

  /* Stats bar */
  .stats {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    color: var(--text-dim);
    margin-top: 12px;
    line-height: 1.8;
  }

  .stats span { color: var(--accent2); }

  /* Right panel - barcodes */
  .right-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px;
    overflow-y: auto;
    max-height: calc(100vh - 72px);
  }

  .barcode-nav {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
    flex-wrap: wrap;
  }

  .barcode-nav button {
    width: auto;
    margin: 0;
    padding: 8px 20px;
    font-size: 0.8rem;
  }

  .nav-prev { background: var(--surface2); color: var(--text); border: 1px solid var(--border); }
  .nav-prev:hover { background: var(--border); }
  .nav-next { background: var(--accent2); }
  .nav-next:hover { background: #ff855a; }

  .barcode-counter {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.85rem;
    color: var(--text-dim);
  }

  .barcode-counter span { color: var(--success); }

  .barcode-display {
    display: flex;
    justify-content: center;
    align-items: center;
    background: #fff;
    border-radius: var(--radius);
    padding: 32px;
    min-height: 200px;
  }

  .barcode-display img {
    display: block;
    image-rendering: pixelated;
    max-width: 100%;
  }

  .seq-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 1rem;
    color: var(--accent);
    text-align: center;
    margin-top: 12px;
    letter-spacing: 0.08em;
  }

  .placeholder {
    color: var(--text-dim);
    font-size: 0.85rem;
    text-align: center;
    padding: 60px 20px;
  }

  .error-msg {
    color: #ff4444;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem;
    margin-top: 8px;
  }

  @media (max-width: 800px) {
    .layout { grid-template-columns: 1fr; }
    .right-panel { max-height: none; }
  }
</style>
</head>
<body>

<h1>Barcode <span>Encoder</span></h1>

<div class="layout">
  <!-- Left: controls -->
  <div class="panel">
    <label>Paste Text</label>
    <textarea id="text-input" placeholder="Paste your text here..."></textarea>

    <label>Format</label>
    <div class="toggle-group">
      <input type="radio" id="fmt-pdf417" name="format" value="pdf417" checked>
      <label for="fmt-pdf417">PDF417</label>
      <input type="radio" id="fmt-qr" name="format" value="qr">
      <label for="fmt-qr">QR Code</label>
    </div>

    <!-- QR-only options -->
    <div id="qr-options">
      <label>QR Error Correction</label>
      <select id="qr-ecc">
        <option value="L">L — Low (~7% recovery)</option>
        <option value="M" selected>M — Medium (~15% recovery)</option>
        <option value="Q">Q — Quartile (~25% recovery)</option>
        <option value="H">H — High (~30% recovery)</option>
      </select>
    </div>

    <label>Chunk Size (chars)</label>
    <div class="chunk-row">
      <input type="number" id="chunk-size" value="1180" min="100" max="2800" step="10">
      <span class="chunk-hint">PDF417 max ~1800 · QR max ~2800</span>
    </div>

    <label>Scale</label>
    <div class="slider-row">
      <input type="range" id="scale" min="1" max="12" value="4">
      <span class="slider-val" id="scale-val">4</span>
    </div>

    <button id="generate-btn" onclick="generate()">Generate Barcodes</button>

    <div class="stats" id="stats"></div>
    <div class="error-msg" id="error-msg"></div>
  </div>

  <!-- Right: barcode display -->
  <div class="right-panel" id="right-panel">
    <div class="placeholder" id="placeholder">
      Barcodes will appear here after generation.
    </div>
    <div id="barcode-area" style="display:none">
      <div class="barcode-nav">
        <button class="nav-prev" onclick="prevBarcode()">&#8592; Prev</button>
        <span class="barcode-counter">Barcode <span id="cur-idx">1</span> of <span id="total-count">1</span></span>
        <button class="nav-next" onclick="nextBarcode()">Next &#8594;</button>
      </div>
      <div class="barcode-display">
        <img id="barcode-img" src="" alt="barcode">
      </div>
      <div class="seq-label" id="seq-label"></div>
    </div>
  </div>
</div>

<script>
  let barcodes = [];
  let currentIdx = 0;

  // Scale slider
  const scaleSlider = document.getElementById('scale');
  const scaleVal = document.getElementById('scale-val');
  scaleSlider.addEventListener('input', () => { scaleVal.textContent = scaleSlider.value; });

  // Format toggle: show/hide QR options, update chunk size default
  document.querySelectorAll('input[name="format"]').forEach(r => {
    r.addEventListener('change', () => {
      const isQR = r.value === 'qr';
      document.getElementById('qr-options').style.display = isQR ? 'block' : 'none';
      // Suggest sensible default chunk sizes
      const chunkInput = document.getElementById('chunk-size');
      if (isQR && chunkInput.value > 800) chunkInput.value = 800;
      if (!isQR && chunkInput.value < 1180) chunkInput.value = 1180;
    });
  });

  async function generate() {
    const text = document.getElementById('text-input').value.trim();
    if (!text) { setError('Please paste some text first.'); return; }
    clearError();

    const format = document.querySelector('input[name="format"]:checked').value;
    const chunkSize = parseInt(document.getElementById('chunk-size').value) || 1180;
    const scale = parseInt(document.getElementById('scale').value);
    const qrEcc = document.getElementById('qr-ecc').value;

    const btn = document.getElementById('generate-btn');
    btn.disabled = true;
    btn.textContent = 'Generating...';

    try {
      const resp = await fetch('/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, format, chunk_size: chunkSize, scale, qr_ecc: qrEcc })
      });
      const data = await resp.json();
      if (data.error) { setError(data.error); return; }

      barcodes = data.barcodes;
      currentIdx = 0;
      showBarcode(0);

      const charCount = text.length;
      document.getElementById('stats').innerHTML =
        `chars: <span>${charCount.toLocaleString()}</span> &nbsp;|&nbsp; ` +
        `chunks: <span>${barcodes.length}</span> &nbsp;|&nbsp; ` +
        `format: <span>${format.toUpperCase()}</span> &nbsp;|&nbsp; ` +
        `chunk size: <span>${chunkSize}</span>`;

    } catch (e) {
      setError('Request failed: ' + e.message);
    } finally {
      btn.disabled = false;
      btn.textContent = 'Generate Barcodes';
    }
  }

  function showBarcode(idx) {
    if (!barcodes.length) return;
    const b = barcodes[idx];
    document.getElementById('placeholder').style.display = 'none';
    document.getElementById('barcode-area').style.display = 'block';
    document.getElementById('barcode-img').src = 'data:image/png;base64,' + b.image;
    document.getElementById('seq-label').textContent = b.header;
    document.getElementById('cur-idx').textContent = idx + 1;
    document.getElementById('total-count').textContent = barcodes.length;
  }

  function prevBarcode() {
    if (currentIdx > 0) { currentIdx--; showBarcode(currentIdx); }
  }

  function nextBarcode() {
    if (currentIdx < barcodes.length - 1) { currentIdx++; showBarcode(currentIdx); }
  }

  // Keyboard navigation
  document.addEventListener('keydown', e => {
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown') nextBarcode();
    if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') prevBarcode();
  });

  function setError(msg) { document.getElementById('error-msg').textContent = msg; }
  function clearError() { document.getElementById('error-msg').textContent = ''; }
</script>
</body>
</html>
"""

ECC_MAP = {
    'L': qrcode.constants.ERROR_CORRECT_L,
    'M': qrcode.constants.ERROR_CORRECT_M,
    'Q': qrcode.constants.ERROR_CORRECT_Q,
    'H': qrcode.constants.ERROR_CORRECT_H,
}


def normalize_line_endings(text):
    """Normalize \n to \r\n so scanned text preserves line breaks in Word."""
    text = text.replace('\r\n', '\n')
    return text.replace('\n', '\r\n')


def chunk_text(text, chunk_size):
    """Split text into chunks of at most chunk_size characters."""
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


def encode_pdf417(payload, scale):
    codes = pdf417gen.encode(payload, security_level=2, columns=6)
    img = pdf417gen.render_image(codes, scale=scale, ratio=3, padding=20)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return base64.b64encode(buf.getvalue()).decode()


def encode_qr(payload, scale, ecc_level):
    ecc = ECC_MAP.get(ecc_level, qrcode.constants.ERROR_CORRECT_M)
    qr = qrcode.QRCode(
        error_correction=ecc,
        box_size=scale,
        border=4,
    )
    qr.add_data(payload.encode('utf-8'))
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white').convert('RGB')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return base64.b64encode(buf.getvalue()).decode()


@app.route('/')
def index():
    return HTML


@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    text = data.get('text', '')
    fmt = data.get('format', 'pdf417').lower()
    chunk_size = int(data.get('chunk_size', 1180))
    scale = int(data.get('scale', 4))
    qr_ecc = data.get('qr_ecc', 'M')

    if not text:
        return jsonify({'error': 'No text provided'})

    # Clamp chunk size to reasonable bounds
    if fmt == 'qr':
        chunk_size = max(50, min(chunk_size, 2800))
    else:
        chunk_size = max(50, min(chunk_size, 1800))

    # Normalize line endings before encoding
    text = normalize_line_endings(text)

    chunks = chunk_text(text, chunk_size)
    total = len(chunks)

    results = []
    for i, chunk in enumerate(chunks):
        header = f'[{i+1:03d}/{total:03d}]'
        payload = header + chunk

        try:
            if fmt == 'qr':
                img_b64 = encode_qr(payload, scale, qr_ecc)
            else:
                img_b64 = encode_pdf417(payload, scale)
        except Exception as e:
            return jsonify({'error': f'Encoding failed on chunk {i+1}: {str(e)}'})

        results.append({'header': header, 'image': img_b64})

    return jsonify({'barcodes': results})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=False)