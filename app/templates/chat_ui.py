"""
UI Interaktif Web Chatbot untuk Dea Trans Group AI Assistant.
Disajikan langsung melalui FastAPI HTMLResponse.
"""

CHAT_UI_HTML = """<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Dea Trans Group - AI Customer Service & FAQ</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --primary: #1e3a8a;
      --primary-light: #3b82f6;
      --primary-hover: #1d4ed8;
      --accent: #f59e0b;
      --bg-main: #f8fafc;
      --card-bg: #ffffff;
      --text-main: #0f172a;
      --text-muted: #64748b;
      --border: #e2e8f0;
      --badge-direct: #10b981;
      --badge-rag: #3b82f6;
      --badge-web: #f59e0b;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: 'Plus Jakarta Sans', sans-serif;
    }

    body {
      background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
      color: var(--text-main);
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      padding: 16px;
    }

    .chat-container {
      width: 100%;
      max-width: 960px;
      height: 92vh;
      background: var(--card-bg);
      border-radius: 20px;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.35);
      display: flex;
      flex-direction: column;
      overflow: hidden;
      border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Header */
    .header {
      background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
      color: #ffffff;
      padding: 18px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    .header-left {
      display: flex;
      align-items: center;
      gap: 14px;
    }

    .brand-logo {
      width: 44px;
      height: 44px;
      background: #ffffff;
      color: #1e3a8a;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 20px;
      box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .brand-title {
      font-size: 18px;
      font-weight: 700;
      letter-spacing: -0.3px;
    }

    .brand-subtitle {
      font-size: 12px;
      color: #bfdbfe;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .status-dot {
      width: 8px;
      height: 8px;
      background: #10b981;
      border-radius: 50%;
      display: inline-block;
      box-shadow: 0 0 8px #10b981;
    }

    .header-right a {
      color: #ffffff;
      background: rgba(255, 255, 255, 0.15);
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 12px;
      text-decoration: none;
      font-weight: 500;
      transition: all 0.2s;
    }

    .header-right a:hover {
      background: rgba(255, 255, 255, 0.25);
    }

    /* Quick Test Chips */
    .chips-bar {
      background: #f1f5f9;
      padding: 10px 20px;
      border-bottom: 1px solid var(--border);
      display: flex;
      gap: 8px;
      overflow-x: auto;
      white-space: nowrap;
      scrollbar-width: thin;
    }

    .chips-bar::-webkit-scrollbar {
      height: 4px;
    }

    .chips-bar::-webkit-scrollbar-thumb {
      background: #cbd5e1;
      border-radius: 4px;
    }

    .chip-label {
      font-size: 11px;
      color: var(--text-muted);
      align-self: center;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .chip {
      background: #ffffff;
      border: 1px solid #cbd5e1;
      color: #334155;
      padding: 6px 12px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }

    .chip:hover {
      background: var(--primary-light);
      color: #ffffff;
      border-color: var(--primary-light);
      transform: translateY(-1px);
    }

    /* Messages Area */
    .messages-area {
      flex: 1;
      overflow-y: auto;
      padding: 24px;
      background: #f8fafc;
      display: flex;
      flex-direction: column;
      gap: 18px;
    }

    .message {
      display: flex;
      gap: 12px;
      max-width: 82%;
      animation: fadeIn 0.3s ease;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(6px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .message.user {
      align-self: flex-end;
      flex-direction: row-reverse;
    }

    .message.bot {
      align-self: flex-start;
    }

    .avatar {
      width: 38px;
      height: 38px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 15px;
      flex-shrink: 0;
    }

    .avatar.bot-avatar {
      background: linear-gradient(135deg, #1e3a8a, #3b82f6);
      color: #ffffff;
      box-shadow: 0 4px 6px rgba(59, 130, 246, 0.25);
    }

    .avatar.user-avatar {
      background: #475569;
      color: #ffffff;
    }

    .bubble {
      padding: 14px 18px;
      border-radius: 16px;
      font-size: 14.5px;
      line-height: 1.6;
      word-wrap: break-word;
      position: relative;
    }

    .message.user .bubble {
      background: linear-gradient(135deg, #1e40af, #2563eb);
      color: #ffffff;
      border-bottom-right-radius: 4px;
      box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);
    }

    .message.bot .bubble {
      background: #ffffff;
      color: var(--text-main);
      border-bottom-left-radius: 4px;
      border: 1px solid var(--border);
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
    }

    /* Decision Node Badge */
    .node-badge {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 600;
      margin-bottom: 8px;
      text-transform: uppercase;
      letter-spacing: 0.3px;
    }

    .badge-direct {
      background: #d1fae5;
      color: #065f46;
      border: 1px solid #a7f3d0;
    }

    .badge-vector {
      background: #dbeafe;
      color: #1e40af;
      border: 1px solid #bfdbfe;
    }

    .badge-web {
      background: #fef3c7;
      color: #92400e;
      border: 1px solid #fde68a;
    }

    .metric-pill {
      font-size: 11px;
      color: var(--text-muted);
      margin-left: 6px;
      font-weight: 400;
      text-transform: none;
    }

    /* Sources Accordion */
    .sources-box {
      margin-top: 12px;
      padding-top: 10px;
      border-top: 1px dashed var(--border);
      font-size: 12px;
    }

    .sources-header {
      font-weight: 600;
      color: var(--text-muted);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: space-between;
      user-select: none;
      padding: 4px 0;
    }

    .source-item {
      background: #f8fafc;
      border: 1px solid var(--border);
      padding: 8px 10px;
      border-radius: 8px;
      margin-top: 6px;
    }

    .source-title {
      font-weight: 600;
      color: var(--primary);
    }

    .source-snippet {
      color: #475569;
      font-size: 11.5px;
      margin-top: 3px;
      line-height: 1.4;
    }

    /* Typing Indicator */
    .typing {
      display: flex;
      align-items: center;
      gap: 5px;
      padding: 12px 16px;
    }

    .typing-dot {
      width: 7px;
      height: 7px;
      background: var(--text-muted);
      border-radius: 50%;
      animation: bounce 1.4s infinite ease-in-out both;
    }

    .typing-dot:nth-child(1) { animation-delay: -0.32s; }
    .typing-dot:nth-child(2) { animation-delay: -0.16s; }

    @keyframes bounce {
      0%, 80%, 100% { transform: scale(0); }
      40% { transform: scale(1); }
    }

    /* Input Bar */
    .input-bar {
      padding: 16px 20px;
      background: #ffffff;
      border-top: 1px solid var(--border);
      display: flex;
      gap: 12px;
      align-items: center;
    }

    .input-box {
      flex: 1;
      padding: 14px 18px;
      border: 1.5px solid var(--border);
      border-radius: 12px;
      font-size: 14.5px;
      outline: none;
      transition: all 0.2s;
    }

    .input-box:focus {
      border-color: var(--primary-light);
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
    }

    .send-btn {
      background: linear-gradient(135deg, #1e3a8a, #2563eb);
      color: #ffffff;
      border: none;
      padding: 14px 24px;
      border-radius: 12px;
      font-weight: 600;
      font-size: 14px;
      cursor: pointer;
      transition: all 0.2s;
      display: flex;
      align-items: center;
      gap: 6px;
      box-shadow: 0 4px 6px rgba(37, 99, 235, 0.25);
    }

    .send-btn:hover {
      background: linear-gradient(135deg, #1d4ed8, #1e40af);
      transform: translateY(-1px);
    }

    .send-btn:disabled {
      background: #94a3b8;
      cursor: not-allowed;
      transform: none;
      box-shadow: none;
    }
  </style>
</head>
<body>

  <div class="chat-container">
    <!-- Header -->
    <div class="header">
      <div class="header-left">
        <div class="brand-logo">DT</div>
        <div>
          <div class="brand-title">Dea Trans Group AI Assistant</div>
          <div class="brand-subtitle">
            <span class="status-dot"></span>
            Operational CS & FAQ • https://deatransgroup.com/
          </div>
        </div>
      </div>
      <div class="header-right">
        <a href="/docs" target="_blank">📖 Swagger Docs</a>
        <a href="https://deatransgroup.com/" target="_blank">🌐 Website Resmi</a>
      </div>
    </div>

    <!-- Quick Test Chips -->
    <div class="chips-bar">
      <span class="chip-label">Coba Cepat:</span>
      <button class="chip" onclick="sendQuickPrompt('Halo min, selamat pagi apa kabar?')">
        👋 Sapaan (Direct Answer)
      </button>
      <button class="chip" onclick="sendQuickPrompt('Bagaimana kebijakan pengembalian barang yang tertinggal di travel?')">
        🎒 Barang Tertinggal (ChromaDB)
      </button>
      <button class="chip" onclick="sendQuickPrompt('Berapa komisi afiliasi untuk mitra agen tiket Dea Trans?')">
        💼 Komisi Afiliasi (ChromaDB)
      </button>
      <button class="chip" onclick="sendQuickPrompt('Apakah tol Cipali macet hari ini?')">
        🌐 Kondisi Tol Hari Ini (Web Search)
      </button>
      <button class="chip" onclick="sendQuickPrompt('Apa saja fasilitas armada HiAce Premio Dea Trans?')">
        🚐 Fasilitas Armada (ChromaDB)
      </button>
    </div>

    <!-- Messages Area -->
    <div class="messages-area" id="messagesArea">
      <!-- Bot Welcome Message -->
      <div class="message bot">
        <div class="avatar bot-avatar">DT</div>
        <div class="bubble">
          <div class="node-badge badge-direct">⚡ Direct Answer</div>
          <div>
            Halo Kak! Selamat datang di Layanan Pelanggan Resmi <strong>Dea Trans Group</strong> (<a href="https://deatransgroup.com/" target="_blank" style="color: #2563eb;">deatransgroup.com</a>).
            <br><br>
            Saya dapat membantu menjawab informasi seputar:
            <ul style="margin-left: 20px; margin-top: 6px;">
              <li>Kebijakan barang tertinggal & klaim paket kiriman</li>
              <li>Program kemitraan & komisi afiliasi agen tiket travel</li>
              <li>Jadwal, fasilitas armada (HiAce Premio/Innova), reschedule & refund</li>
              <li>Pencarian info lalu lintas terkini secara otomatis</li>
            </ul>
            <br>
            Silakan pilih tombol cepat di atas atau ketik pertanyaan Kakak di bawah ini! 😊
          </div>
        </div>
      </div>
    </div>

    <!-- Input Bar -->
    <div class="input-bar">
      <input 
        type="text" 
        id="userInput" 
        class="input-box" 
        placeholder="Ketik pertanyaan seputar layanan Dea Trans Group..." 
        autocomplete="off"
        onkeydown="if(event.key === 'Enter') sendMessage()"
      />
      <button id="sendBtn" class="send-btn" onclick="sendMessage()">
        <span>Kirim</span>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="22" y1="2" x2="11" y2="13"></line>
          <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
        </svg>
      </button>
    </div>
  </div>

  <script>
    const messagesArea = document.getElementById('messagesArea');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');

    function scrollToBottom() {
      messagesArea.scrollTop = messagesArea.scrollHeight;
    }

    function sendQuickPrompt(text) {
      userInput.value = text;
      sendMessage();
    }

    function appendUserMessage(text) {
      const msgDiv = document.createElement('div');
      msgDiv.className = 'message user';
      msgDiv.innerHTML = `
        <div class="avatar user-avatar">Anda</div>
        <div class="bubble">${escapeHtml(text)}</div>
      `;
      messagesArea.appendChild(msgDiv);
      scrollToBottom();
    }

    function showTypingIndicator() {
      const typingDiv = document.createElement('div');
      typingDiv.className = 'message bot';
      typingDiv.id = 'typingIndicator';
      typingDiv.innerHTML = `
        <div class="avatar bot-avatar">DT</div>
        <div class="bubble typing">
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
        </div>
      `;
      messagesArea.appendChild(typingDiv);
      scrollToBottom();
    }

    function removeTypingIndicator() {
      const el = document.getElementById('typingIndicator');
      if (el) el.remove();
    }

    function getBadgeHtml(route, timeMs) {
      const timeStr = timeMs ? `<span class="metric-pill">⚡ ${timeMs} ms</span>` : '';
      if (route === 'direct_greeting') {
        return `<span class="node-badge badge-direct">⚡ Direct Answer (Tanpa DB)${timeStr}</span>`;
      } else if (route === 'vector_retrieval') {
        return `<span class="node-badge badge-vector">📚 ChromaDB Vector RAG${timeStr}</span>`;
      } else if (route === 'web_search_fallback') {
        return `<span class="node-badge badge-web">🌐 Web Search Fallback (Tavily)${timeStr}</span>`;
      }
      return `<span class="node-badge badge-direct">${route}</span>`;
    }

    function formatBotAnswer(answer) {
      // Ubah baris baru menjadi <br>
      let formatted = escapeHtml(answer).replace(/\\n/g, '<br>');
      // Buat tautan URL clickable
      formatted = formatted.replace(/(https?:\\/\\/[^\\s<]+)/g, '<a href="$1" target="_blank" style="color: #2563eb; font-weight: 500;">$1</a>');
      return formatted;
    }

    function appendBotResponse(data) {
      const msgDiv = document.createElement('div');
      msgDiv.className = 'message bot';

      let sourcesHtml = '';
      if (data.sources && data.sources.length > 0) {
        const sourceItems = data.sources.map((s, idx) => `
          <div class="source-item">
            <div class="source-title">[${idx + 1}] ${escapeHtml(s.title)} <span style="font-weight: 400; color: #64748b; font-size: 11px;">(${s.category || 'FAQ'})</span></div>
            <div class="source-snippet">${escapeHtml(s.snippet || '')}</div>
          </div>
        `).join('');

        sourcesHtml = `
          <div class="sources-box">
            <details>
              <summary class="sources-header">
                <span>📎 ${data.sources.length} Sumber Rujukan yang Digunakan</span>
              </summary>
              <div style="margin-top: 8px;">
                ${sourceItems}
              </div>
            </details>
          </div>
        `;
      }

      msgDiv.innerHTML = `
        <div class="avatar bot-avatar">DT</div>
        <div class="bubble">
          ${getBadgeHtml(data.route_taken, data.execution_time_ms)}
          <div>${formatBotAnswer(data.answer)}</div>
          ${sourcesHtml}
        </div>
      `;
      messagesArea.appendChild(msgDiv);
      scrollToBottom();
    }

    async function sendMessage() {
      const text = userInput.value.trim();
      if (!text) return;

      appendUserMessage(text);
      userInput.value = '';
      userInput.disabled = true;
      sendBtn.disabled = true;

      showTypingIndicator();

      try {
        const response = await fetch('/api/v1/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text })
        });

        const data = await response.json();
        removeTypingIndicator();

        if (response.ok) {
          appendBotResponse(data);
        } else {
          appendBotResponse({
            answer: "Maaf, terjadi kendala teknis saat memproses pertanyaan Anda: " + (data.detail || "Server error"),
            route_taken: "error",
            sources: []
          });
        }
      } catch (err) {
        removeTypingIndicator();
        appendBotResponse({
          answer: "Gagal terhubung ke server API. Pastikan server FastAPI aktif di http://localhost:8000.",
          route_taken: "error",
          sources: []
        });
      } finally {
        userInput.disabled = false;
        sendBtn.disabled = false;
        userInput.focus();
      }
    }

    function escapeHtml(string) {
      const div = document.createElement('div');
      div.innerText = string;
      return div.innerHTML;
    }
  </script>
</body>
</html>
"""
