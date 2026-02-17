#!/usr/bin/env python3
"""
PDF417 Text Encoder - AI Workbench App
Converts pasted text into a sequence of PDF417 barcodes.
Each barcode is prefixed with sequence info: [N/TOTAL] for reassembly.
"""

import io
import base64
import math
from flask import Flask, render_template_string, request, jsonify
from pdf417gen import encode, render_image

app = Flask(__name__)

# PDF417 practical capacity (conservative — accounts for header overhead)
# PDF417 can hold up to ~1800 bytes in high-error-correction mode;
# we use a safe 1200 chars per chunk to leave room for our sequence header.
CHUNK_SIZE = 1200
HEADER_OVERHEAD = 20  # "[NNN/NNN] " prefix length

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> list[str]:
    """Split text into chunks that fit in a PDF417 barcode."""
    usable = chunk_size - HEADER_OVERHEAD
    return [text[i:i+usable] for i in range(0, len(text), usable)]

def text_to_pdf417_b64(payload: str, scale: int = 3, ratio: int = 3) -> str:
    """Encode a string as a PDF417 barcode and return a base64 PNG string."""
    codes = encode(payload, columns=8, security_level=2)
    image = render_image(codes, scale=scale, ratio=ratio, padding=20)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>PDF417 Text Encoder</title>
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
      padding: 18px 32px;
      display: flex;
      align-items: center;
      gap: 14px;
      background: linear-gradient(90deg, rgba(0,240,160,0.04) 0%, transparent 60%);
    }

    .logo-icon {
      width: 36px; height: 36px;
      display: grid;
      grid-template-columns: repeat(3,1fr);
      gap: 3px;
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
      font-size: 1.15rem;
      font-weight: 700;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: var(--accent);
    }
    header p {
      font-family: var(--font-mono);
      font-size: 0.72rem;
      color: var(--muted);
      letter-spacing: 0.06em;
    }

    main {
      flex: 1;
      display: grid;
      grid-template-columns: 420px 1fr;
      gap: 0;
    }

    /* ─── Left panel ─── */
    .panel-left {
      border-right: 1px solid var(--border);
      padding: 28px 28px 28px 32px;
      display: flex;
      flex-direction: column;
      gap: 20px;
      background: var(--surface);
    }

    label {
      font-size: 0.72rem;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--muted);
      display: block;
      margin-bottom: 8px;
    }

    textarea {
      width: 100%;
      min-height: 260px;
      resize: vertical;
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 4px;
      color: var(--text);
      font-family: var(--font-mono);
      font-size: 0.85rem;
      padding: 14px;
      outline: none;
      line-height: 1.6;
      transition: border-color 0.2s;
    }
    textarea:focus { border-color: var(--accent2); }

    .stats {
      font-family: var(--font-mono);
      font-size: 0.75rem;
      color: var(--muted);
      display: flex;
      gap: 18px;
    }
    .stats span { color: var(--accent); }

    .settings-row {
      display: flex;
      gap: 14px;
    }

    .field {
      flex: 1;
    }

    select, input[type=number] {
      width: 100%;
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 4px;
      color: var(--text);
      font-family: var(--font-mono);
      font-size: 0.85rem;
      padding: 9px 12px;
      outline: none;
    }
    select:focus, input:focus { border-color: var(--accent2); }

    .btn {
      width: 100%;
      padding: 13px;
      border: none;
      border-radius: 4px;
      font-family: var(--font-ui);
      font-size: 0.85rem;
      font-weight: 700;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      cursor: pointer;
      transition: all 0.15s;
    }

    .btn-primary {
      background: var(--accent);
      color: #000;
    }
    .btn-primary:hover { background: #00ffa8; transform: translateY(-1px); }
    .btn-primary:active { transform: translateY(0); }
    .btn-primary:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }

    .btn-secondary {
      background: transparent;
      color: var(--muted);
      border: 1px solid var(--border);
    }
    .btn-secondary:hover { color: var(--text); border-color: var(--muted); }

    .error-box {
      background: rgba(255,64,96,0.1);
      border: 1px solid var(--danger);
      border-radius: 4px;
      padding: 10px 14px;
      font-family: var(--font-mono);
      font-size: 0.78rem;
      color: var(--danger);
      display: none;
    }

    /* ─── Right panel ─── */
    .panel-right {
      padding: 28px 32px;
      display: flex;
      flex-direction: column;
      gap: 24px;
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
      font-size: 0.8rem;
      letter-spacing: 0.08em;
    }

    .empty-grid {
      display: grid;
      grid-template-columns: repeat(8,10px);
      gap: 4px;
      opacity: 0.25;
    }
    .empty-grid div {
      height: 36px;
      background: var(--muted);
      border-radius: 1px;
    }

    .results-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .results-title {
      font-size: 0.72rem;
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
      font-size: 0.72rem;
      color: var(--accent);
    }

    .barcode-grid {
      display: flex;
      flex-direction: column;
      gap: 24px;
    }

    .barcode-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 6px;
      overflow: hidden;
      animation: slideIn 0.3s ease both;
    }
    .barcode-card:nth-child(2) { animation-delay: 0.05s; }
    .barcode-card:nth-child(3) { animation-delay: 0.10s; }
    .barcode-card:nth-child(4) { animation-delay: 0.15s; }

    @keyframes slideIn {
      from { opacity: 0; transform: translateY(12px); }
      to   { opacity: 1; transform: translateY(0); }
    }

    .barcode-card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 10px 16px;
      border-bottom: 1px solid var(--border);
      background: rgba(0,0,0,0.2);
    }

    .seq-label {
      font-family: var(--font-mono);
      font-size: 0.75rem;
      color: var(--accent2);
      letter-spacing: 0.08em;
    }

    .chunk-preview {
      font-family: var(--font-mono);
      font-size: 0.68rem;
      color: var(--muted);
      max-width: 340px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .barcode-card-body {
      padding: 32px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #ffffff;
      border-top: 1px solid #e0e0e0;
    }

    .barcode-card-body img {
      max-width: 100%;
      height: auto;
      display: block;
    }

    /* ─── Progress ─── */
    .progress-wrap {
      display: none;
      flex-direction: column;
      gap: 10px;
      align-items: center;
      justify-content: center;
      flex: 1;
    }

    .progress-label {
      font-family: var(--font-mono);
      font-size: 0.78rem;
      color: var(--accent);
      letter-spacing: 0.1em;
    }

    .progress-bar-outer {
      width: 300px;
      height: 6px;
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

    footer {
      border-top: 1px solid var(--border);
      padding: 10px 32px;
      font-family: var(--font-mono);
      font-size: 0.68rem;
      color: var(--muted);
      display: flex;
      gap: 24px;
    }

    @media print {
      body::before { display: none; }
      header, footer, .panel-left { display: none; }
      main { display: block; }
      .panel-right { padding: 0; }
      .barcode-card { break-inside: avoid; border: none; }
      .barcode-card-header { display: none; }
      .barcode-card-body { background: white; padding: 10px 0; }
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
    <h1>PDF417 Text Encoder</h1>
    <p>DGX Spark // Air-gap data transfer via barcode sequence</p>
  </div>
</header>

<main>
  <!-- LEFT: Input -->
  <div class="panel-left">
    <div>
      <label>Input Text</label>
      <textarea id="inputText" placeholder="Paste your text here..."></textarea>
      <div class="stats" id="stats">
        <div>chars: <span id="charCount">0</span></div>
        <div>chunks: <span id="chunkCount">0</span></div>
      </div>
    </div>

    <div class="settings-row">
      <div class="field">
        <label>Scale (px/module)</label>
        <input type="number" id="scale" value="5" min="1" max="12" />
      </div>
      <div class="field">
        <label>Barcode Ratio (h/w)</label>
        <input type="number" id="ratio" value="3" min="1" max="8" />
      </div>
    </div>

    <div class="error-box" id="errorBox"></div>

    <button class="btn btn-primary" id="encodeBtn" onclick="encode()">
      ⬡ Generate Barcodes
    </button>
    <button class="btn btn-secondary" onclick="clearAll()">
      Clear
    </button>
    <button class="btn btn-secondary" onclick="window.print()">
      Print Barcode Sheet
    </button>
  </div>

  <!-- RIGHT: Output -->
  <div class="panel-right" id="rightPanel">
    <div class="empty-state" id="emptyState">
      <div class="empty-grid">
        <div></div><div></div><div></div><div></div>
        <div></div><div></div><div></div><div></div>
        <div></div><div></div><div></div><div></div>
        <div></div><div></div><div></div><div></div>
        <div></div><div></div><div></div><div></div>
        <div></div><div></div><div></div><div></div>
      </div>
      <span>Barcodes will appear here</span>
    </div>

    <div class="progress-wrap" id="progressWrap">
      <div class="progress-label" id="progressLabel">Encoding chunk 1 / 1...</div>
      <div class="progress-bar-outer">
        <div class="progress-bar-inner" id="progressBar"></div>
      </div>
    </div>

    <div id="resultsSection" style="display:none; flex-direction:column; gap:24px;">
      <div class="results-header">
        <span class="results-title">Generated Sequence</span>
        <span class="badge" id="totalBadge">0 barcodes</span>
      </div>
      <div class="barcode-grid" id="barcodeGrid"></div>
    </div>
  </div>
</main>

<footer>
  <span>PDF417 // security level 2</span>
  <span>chunk size: 1200 chars</span>
  <span>format: PNG base64</span>
</footer>

<script>
  const CHUNK_SIZE = 1200;

  const inputText  = document.getElementById('inputText');
  const charCount  = document.getElementById('charCount');
  const chunkCount = document.getElementById('chunkCount');
  const encodeBtn  = document.getElementById('encodeBtn');
  const errorBox   = document.getElementById('errorBox');

  function chunkText(text) {
    const usable = CHUNK_SIZE - 20;
    const chunks = [];
    for (let i = 0; i < text.length; i += usable) {
      chunks.push(text.slice(i, i + usable));
    }
    return chunks;
  }

  inputText.addEventListener('input', () => {
    const text = inputText.value;
    const chunks = chunkText(text);
    charCount.textContent  = text.length.toLocaleString();
    chunkCount.textContent = Math.max(1, chunks.length);
  });

  async function encode() {
    const text = inputText.value.trim();
    if (!text) {
      showError('Please paste some text first.');
      return;
    }

    hideError();
    encodeBtn.disabled = true;

    const chunks  = chunkText(text);
    const total   = chunks.length;
    const scale   = parseInt(document.getElementById('scale').value) || 3;
    const ratio   = parseInt(document.getElementById('ratio').value) || 3;

    // Show progress
    document.getElementById('emptyState').style.display   = 'none';
    document.getElementById('resultsSection').style.display = 'none';
    const progressWrap = document.getElementById('progressWrap');
    progressWrap.style.display = 'flex';

    const grid  = document.getElementById('barcodeGrid');
    grid.innerHTML = '';

    for (let i = 0; i < chunks.length; i++) {
      const label = `[${String(i+1).padStart(3,'0')}/${String(total).padStart(3,'0')}]`;
      const payload = `${label} ${chunks[i]}`;

      document.getElementById('progressLabel').textContent =
        `Encoding chunk ${i+1} of ${total}...`;
      document.getElementById('progressBar').style.width =
        `${Math.round(((i) / total) * 100)}%`;

      try {
        const resp = await fetch('/encode', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: payload, scale, ratio })
        });
        const data = await resp.json();
        if (data.error) throw new Error(data.error);

        const card = document.createElement('div');
        card.className = 'barcode-card';
        card.innerHTML = `
          <div class="barcode-card-header">
            <span class="seq-label">Barcode ${i+1} / ${total}</span>
            <span class="chunk-preview">${escapeHtml(chunks[i].slice(0,60))}${chunks[i].length>60?'…':''}</span>
          </div>
          <div class="barcode-card-body">
            <img src="data:image/png;base64,${data.image}" alt="PDF417 barcode ${i+1}" />
          </div>
        `;
        grid.appendChild(card);
      } catch (err) {
        showError(`Error on chunk ${i+1}: ${err.message}`);
        progressWrap.style.display = 'none';
        encodeBtn.disabled = false;
        return;
      }
    }

    document.getElementById('progressBar').style.width = '100%';
    setTimeout(() => {
      progressWrap.style.display = 'none';
      const rs = document.getElementById('resultsSection');
      rs.style.display = 'flex';
      document.getElementById('totalBadge').textContent =
        `${total} barcode${total !== 1 ? 's' : ''}`;
    }, 300);

    encodeBtn.disabled = false;
  }

  function clearAll() {
    inputText.value = '';
    charCount.textContent  = '0';
    chunkCount.textContent = '0';
    document.getElementById('barcodeGrid').innerHTML = '';
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('progressWrap').style.display   = 'none';
    document.getElementById('emptyState').style.display     = 'flex';
    hideError();
  }

  function showError(msg) {
    errorBox.textContent = msg;
    errorBox.style.display = 'block';
  }
  function hideError() {
    errorBox.style.display = 'none';
  }
  function escapeHtml(s) {
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }
</script>
</body>
</html>"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/encode", methods=["POST"])
def encode_barcode():
    data = request.get_json(force=True)
    text = data.get("text", "")

    # Browser textareas normalize all line endings to \n, silently stripping \r.
    # Restore proper \r\n (CRLF) before encoding so the scanner outputs line
    # endings exactly as the original text intended.
    text = text.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '\r\n')

    scale = max(1, min(int(data.get("scale", 5)), 12))
    ratio = max(1, min(int(data.get("ratio", 3)), 8))

    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        b64 = text_to_pdf417_b64(text, scale=scale, ratio=ratio)
        return jsonify({"image": b64})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # AI Workbench binds to 0.0.0.0 so other machines on the network can reach it
    app.run(host="0.0.0.0", port=8888, debug=False)
