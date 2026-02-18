from flask import Flask, request, jsonify
import qrcode
import io
import base64
from PIL import Image

app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>QR Encoder</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Chakra+Petch:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
  :root {
    --bg:        #0a0c10;
    --surface:   #111520;
    --border:    #1e2a40;
    --accent:    #00f0a0;
    --accent2:   #0086ff;
    --danger:    #ff4060;
    --text:      #c8d8e8;
    --muted:     #4a6080;
    --font-mono: 'Share Tech Mono', monospace;
    --font-ui:   'Chakra Petch', sans-serif;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: var(--font-ui);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  header {
    border-bottom: 1px solid var(--border);
    padding: 16px 28px;
    display: flex;
    align-items: center;
    gap: 14px;
    background: linear-gradient(90deg, rgba(0,240,160,0.04) 0%, transparent 60%);
  }

  .logo-icon {
    width: 34px; height: 34px;
    display: grid;
    grid-template-columns: repeat(3,1fr);
    gap: 3px;
    flex-shrink: 0;
  }
  .logo-icon span {
    background: var(--accent);
    border-radius: 1px;
    animation: blink 2.4s infinite;
  }
  .logo-icon span:nth-child(2n) { animation-delay: 0.3s; opacity: 0.5; }
  .logo-icon span:nth-child(3n) { animation-delay: 0.6s; opacity: 0.75; }

  @keyframes blink {
    0%,100% { opacity: 1; }
    50%      { opacity: 0.3; }
  }

  header h1 {
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--accent);
  }
  header p {
    font-family: var(--font-mono);
    font-size: 0.7rem;
    color: var(--muted);
    letter-spacing: 0.06em;
  }

  main {
    flex: 1;
    display: grid;
    grid-template-columns: 380px 1fr;
    gap: 0;
    overflow: hidden;
  }

  .panel-left {
    border-right: 1px solid var(--border);
    padding: 24px 24px 24px 28px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    background: var(--surface);
    overflow-y: auto;
  }

  label {
    font-size: 0.7rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--muted);
    display: block;
    margin-bottom: 7px;
  }

  textarea {
    width: 100%;
    min-height: 220px;
    resize: vertical;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 4px;
    color: var(--text);
    font-family: var(--font-mono);
    font-size: 0.82rem;
    padding: 12px;
    outline: none;
    line-height: 1.6;
    transition: border-color 0.2s;
  }
  textarea:focus { border-color: var(--accent2); }

  .live-stats {
    font-family: var(--font-mono);
    font-size: 0.72rem;
    color: var(--muted);
    display: flex;
    gap: 16px;
    margin-top: 6px;
  }
  .live-stats span { color: var(--accent); }

  select {
    width: 100%;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 4px;
    color: var(--text);
    font-family: var(--font-mono);
    font-size: 0.82rem;
    padding: 8px 10px;
    outline: none;
  }
  select:focus { border-color: var(--accent2); }

  .chunk-row {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  input[type="number"] {
    width: 90px;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 4px;
    color: var(--accent);
    font-family: var(--font-mono);
    font-size: 0.88rem;
    padding: 7px 10px;
    text-align: center;
    outline: none;
  }
  input[type="number"]:focus { border-color: var(--accent2); }
  .chunk-hint {
    font-family: var(--font-mono);
    font-size: 0.68rem;
    color: var(--muted);
    line-height: 1.4;
  }

  .slider-row {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  input[type="range"] {
    flex: 1;
    accent-color: var(--accent);
  }
  .slider-val {
    font-family: var(--font-mono);
    font-size: 0.85rem;
    color: var(--accent);
    min-width: 24px;
    text-align: right;
  }

  .btn {
    width: 100%;
    padding: 11px;
    border: none;
    border-radius: 4px;
    font-family: var(--font-ui);
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    cursor: pointer;
    transition: all 0.15s;
  }
  .btn-primary { background: var(--accent); color: #000; }
  .btn-primary:hover { background: #00ffa8; transform: translateY(-1px); }
  .btn-primary:active { transform: translateY(0); }
  .btn-primary:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }
  .btn-secondary { background: transparent; color: var(--muted); border: 1px solid var(--border); }
  .btn-secondary:hover { color: var(--text); border-color: var(--muted); }

  .error-box {
    background: rgba(255,64,96,0.1);
    border: 1px solid var(--danger);
    border-radius: 4px;
    padding: 9px 13px;
    font-family: var(--font-mono);
    font-size: 0.75rem;
    color: var(--danger);
    display: none;
  }

  .panel-right {
    padding: 24px 28px;
    display: flex;
    flex-direction: column;
    gap: 20px;
    overflow-y: auto;
  }

  .empty-state {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 14px;
    color: var(--muted);
    font-family: var(--font-mono);
    font-size: 0.78rem;
    letter-spacing: 0.08em;
  }
  .empty-grid {
    display: grid;
    grid-template-columns: repeat(8, 10px);
    gap: 4px;
    opacity: 0.2;
  }
  .empty-grid div { height: 36px; background: var(--muted); border-radius: 1px; }

  .progress-wrap {
    display: none;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    padding: 40px 0;
  }
  .progress-label {
    font-family: var(--font-mono);
    font-size: 0.78rem;
    color: var(--muted);
    letter-spacing: 0.08em;
  }
  .progress-bar-outer {
    width: 300px; height: 5px;
    background: var(--border);
    border-radius: 3px;
    overflow: hidden;
  }
  .progress-bar-inner {
    height: 100%;
    background: var(--accent);
    border-radius: 3px;
    transition: width 0.2s;
    width: 0%;
  }

  .results-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .results-title {
    font-size: 0.7rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--muted);
  }
  .badge {
    background: rgba(0,240,160,0.12);
    border: 1px solid rgba(0,240,160,0.3);
    border-radius: 100px;
    padding: 3px 12px;
    font-family: var(--font-mono);
    font-size: 0.7rem;
    color: var(--accent);
  }

  .barcode-nav {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
  }
  .barcode-nav .btn { width: auto; padding: 8px 20px; }
  .nav-prev { background: transparent; color: var(--muted); border: 1px solid var(--border); }
  .nav-prev:hover { color: var(--text); border-color: var(--muted); }
  .nav-next { background: var(--accent2); color: #fff; border: none; }
  .nav-next:hover { background: #0099ff; transform: translateY(-1px); }

  .barcode-counter {
    font-family: var(--font-mono);
    font-size: 0.82rem;
    color: var(--muted);
  }
  .barcode-counter span { color: var(--accent); }

  .barcode-display {
    display: flex;
    justify-content: center;
    align-items: center;
    background: #ffffff;
    border-radius: 4px;
    padding: 32px;
    min-height: 180px;
  }
  .barcode-display img {
    display: block;
    image-rendering: pixelated;
    max-width: 100%;
  }

  .seq-label {
    font-family: var(--font-mono);
    font-size: 0.9rem;
    color: var(--accent);
    text-align: center;
    margin-top: 10px;
    letter-spacing: 0.08em;
  }

  footer {
    border-top: 1px solid var(--border);
    padding: 9px 28px;
    font-family: var(--font-mono);
    font-size: 0.66rem;
    color: var(--muted);
    display: flex;
    gap: 24px;
    flex-wrap: wrap;
  }

  @media (max-width: 800px) {
    main { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>

<header>
  <div class="logo-icon">
    <span></span><span></span><span></span>
    <span></span><span></span><span></span>
    <span></span><span></span><span></span>
  </div>
  <div>
    <h1>QR Text Encoder</h1>
    <p>DGX Spark // Air-gap data transfer via QR code sequence</p>
  </div>
</header>

<main>
  <div class="panel-left">

    <div>
      <label>Input Text</label>
      <textarea id="inputText" placeholder="Paste your text here..."></textarea>
      <div class="live-stats">
        <div>chars: <span id="charCount">0</span></div>
        <div>chunks: <span id="chunkCount">0</span></div>
      </div>
    </div>

    <div>
      <label>Error Correction</label>
      <select id="qr-ecc">
        <option value="L">L — Low (~7% recovery)</option>
        <option value="M" selected>M — Medium (~15% recovery)</option>
        <option value="Q">Q — Quartile (~25% recovery)</option>
        <option value="H">H — High (~30% recovery)</option>
      </select>
    </div>

    <div>
      <label>Chunk Size (chars)</label>
      <div class="chunk-row">
        <input type="number" id="chunk-size" value="800" min="100" max="2800" step="10">
        <span class="chunk-hint">QR max ~2800<br>Recommended: 800</span>
      </div>
    </div>

    <div>
      <label>Scale (px/module)</label>
      <div class="slider-row">
        <input type="range" id="scale" min="1" max="12" value="4">
        <span class="slider-val" id="scale-val">4</span>
      </div>
    </div>

    <div class="error-box" id="errorBox"></div>

    <button class="btn btn-primary" id="encodeBtn" onclick="generate()">&#x2B21; Generate QR Codes</button>
    <button class="btn btn-secondary" onclick="clearAll()">Clear</button>

  </div>

  <div class="panel-right">

    <div class="empty-state" id="emptyState">
      <div class="empty-grid">
        <div></div><div></div><div></div><div></div>
        <div></div><div></div><div></div><div></div>
        <div></div><div></div><div></div><div></div>
        <div></div><div></div><div></div><div></div>
        <div></div><div></div><div></div><div></div>
        <div></div><div></div><div></div><div></div>
      </div>
      <span>QR codes will appear here</span>
    </div>

    <div class="progress-wrap" id="progressWrap">
      <div class="progress-label" id="progressLabel">Encoding...</div>
      <div class="progress-bar-outer">
        <div class="progress-bar-inner" id="progressBar"></div>
      </div>
    </div>

    <div id="resultsSection" style="display:none; flex-direction:column; gap:18px;">
      <div class="results-header">
        <span class="results-title">Generated Sequence</span>
        <span class="badge" id="totalBadge">0 codes</span>
      </div>
      <div class="barcode-nav">
        <button class="btn nav-prev" onclick="prevBarcode()">&#8592; Prev</button>
        <span class="barcode-counter">Code <span id="cur-idx">1</span> of <span id="total-count">1</span></span>
        <button class="btn nav-next" onclick="nextBarcode()">Next &#8594;</button>
      </div>
      <div class="barcode-display">
        <img id="barcode-img" src="" alt="QR code">
      </div>
      <div class="seq-label" id="seq-label"></div>
    </div>

  </div>
</main>

<footer>
  <span>QR Code // <span id="footer-ecc">ECC M</span></span>
  <span>chunk size: <span id="footer-chunk">800</span> chars</span>
  <span>format: PNG</span>
  <span>sparky // 192.168.1.218:8888</span>
</footer>

<script>
  let barcodes  = [];
  let currentIdx = 0;

  const inputText    = document.getElementById('inputText');
  const charCountEl  = document.getElementById('charCount');
  const chunkCountEl = document.getElementById('chunkCount');

  function getChunkSize() {
    return parseInt(document.getElementById('chunk-size').value) || 800;
  }

  inputText.addEventListener('input', updateLiveStats);
  document.getElementById('chunk-size').addEventListener('input', updateLiveStats);

  function updateLiveStats() {
    const len = inputText.value.length;
    const cs  = getChunkSize();
    charCountEl.textContent  = len.toLocaleString();
    chunkCountEl.textContent = len > 0 ? Math.ceil(len / cs) : 0;
  }

  const scaleSlider = document.getElementById('scale');
  scaleSlider.addEventListener('input', () => {
    document.getElementById('scale-val').textContent = scaleSlider.value;
  });

  async function generate() {
    const text = inputText.value.trim();
    if (!text) { showError('Please paste some text first.'); return; }
    hideError();

    const chunkSize = getChunkSize();
    const scale     = parseInt(scaleSlider.value);
    const qrEcc     = document.getElementById('qr-ecc').value;

    const btn = document.getElementById('encodeBtn');
    btn.disabled = true;

    document.getElementById('emptyState').style.display     = 'none';
    document.getElementById('resultsSection').style.display = 'none';
    const progressWrap = document.getElementById('progressWrap');
    progressWrap.style.display = 'flex';
    document.getElementById('progressBar').style.width    = '0%';
    document.getElementById('progressLabel').textContent  = 'Sending request...';

    try {
      const resp = await fetch('/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, chunk_size: chunkSize, scale, qr_ecc: qrEcc })
      });
      const data = await resp.json();
      if (data.error) {
        showError(data.error);
        progressWrap.style.display = 'none';
        return;
      }

      barcodes   = data.barcodes;
      currentIdx = 0;

      document.getElementById('progressBar').style.width   = '100%';
      document.getElementById('progressLabel').textContent =
        `Done — ${barcodes.length} code${barcodes.length !== 1 ? 's' : ''} generated`;

      setTimeout(() => {
        progressWrap.style.display = 'none';
        const rs = document.getElementById('resultsSection');
        rs.style.display = 'flex';
        document.getElementById('totalBadge').textContent =
          `${barcodes.length} code${barcodes.length !== 1 ? 's' : ''}`;
        showBarcode(0);
      }, 350);

      document.getElementById('footer-ecc').textContent   = `ECC ${qrEcc}`;
      document.getElementById('footer-chunk').textContent = chunkSize;

    } catch (e) {
      showError('Request failed: ' + e.message);
      progressWrap.style.display = 'none';
    } finally {
      btn.disabled = false;
    }
  }

  function showBarcode(idx) {
    if (!barcodes.length) return;
    const b = barcodes[idx];
    document.getElementById('barcode-img').src            = 'data:image/png;base64,' + b.image;
    document.getElementById('seq-label').textContent      = b.header;
    document.getElementById('cur-idx').textContent        = idx + 1;
    document.getElementById('total-count').textContent    = barcodes.length;
  }

  function prevBarcode() {
    if (currentIdx > 0) { currentIdx--; showBarcode(currentIdx); }
  }
  function nextBarcode() {
    if (currentIdx < barcodes.length - 1) { currentIdx++; showBarcode(currentIdx); }
  }

  document.addEventListener('keydown', e => {
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown') nextBarcode();
    if (e.key === 'ArrowLeft'  || e.key === 'ArrowUp')   prevBarcode();
  });

  function clearAll() {
    inputText.value          = '';
    charCountEl.textContent  = '0';
    chunkCountEl.textContent = '0';
    barcodes                 = [];
    currentIdx               = 0;
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('progressWrap').style.display   = 'none';
    document.getElementById('emptyState').style.display     = 'flex';
    hideError();
  }

  function showError(msg) {
    const box = document.getElementById('errorBox');
    box.textContent   = msg;
    box.style.display = 'block';
  }
  function hideError() {
    document.getElementById('errorBox').style.display = 'none';
  }
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
    data       = request.get_json()
    text       = data.get('text', '')
    chunk_size = int(data.get('chunk_size', 800))
    scale      = int(data.get('scale', 4))
    qr_ecc     = data.get('qr_ecc', 'M')

    if not text:
        return jsonify({'error': 'No text provided'})

    chunk_size = max(50, min(chunk_size, 2800))
    text       = normalize_line_endings(text)
    chunks     = chunk_text(text, chunk_size)
    total      = len(chunks)

    results = []
    for i, chunk in enumerate(chunks):
        header  = f'[{i+1:03d}/{total:03d}]'
        payload = header + chunk
        try:
            img_b64 = encode_qr(payload, scale, qr_ecc)
        except Exception as e:
            return jsonify({'error': f'Encoding failed on chunk {i+1}: {str(e)}'})
        results.append({'header': header, 'image': img_b64})

    return jsonify({'barcodes': results})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=False)