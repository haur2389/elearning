/**
 * Smart E-Learning — Chatbot Widget
 * Tư vấn đăng ký môn học bằng Groq AI — gọi qua BACKEND (Django)
 * Tự inject vào bất kỳ trang nào chỉ bằng 1 thẻ <script>
 *
 * FIX (theo yêu cầu): quay lại cách gọi Groq AI THÔNG QUA BACKEND thay vì
 * gọi thẳng từ trình duyệt — vì để API key ở backend (biến môi trường
 * GROQ_API_KEY trên Render) an toàn hơn nhiều so với để lộ trong JS phía
 * client. Backend endpoint /ai/chat/ (apps/users/ai_chat_view.py) đã được
 * viết sẵn để gọi Groq (api.groq.com), lấy dữ liệu khóa học thật từ
 * database, và tự xử lý "chuyển tiếp cho nhân viên hỗ trợ" (handoff).
 *
 * ✅ Cách gắn key: vào Render dashboard → service backend → Environment →
 *    thêm biến GROQ_API_KEY = key thật của bạn (lấy tại console.groq.com/keys)
 *    → Save → Render tự redeploy. KHÔNG cần sửa code, KHÔNG cần đặt key
 *    trong file JS này.
 */
(function () {
  'use strict';

  const SELF_SCRIPT = document.currentScript;

  /* ── CONFIG BACKEND ─────────────────────────────────────── */
  const API_BASE = (window.CONFIG?.API_BASE_URL || 'https://elearning-backend-ead6.onrender.com/api');
  const CHAT_ENDPOINT = `${API_BASE}/ai/chat/`;

  const LEVEL_MAP = { beginner: 'Cơ bản', intermediate: 'Trung cấp', advanced: 'Nâng cao' };

  const QUICK_ACTIONS = [
    { label: '📚 Xem khóa học',  text: 'Cho tôi xem danh sách khóa học hiện có' },
    { label: '🆓 Miễn phí',      text: 'Có những khóa học miễn phí nào?' },
    { label: '💡 Tư vấn chọn',   text: 'Tôi muốn được tư vấn chọn khóa học phù hợp' },
    { label: '💳 Học phí',       text: 'Học phí các khóa học là bao nhiêu?' },
    { label: '📝 Cách đăng ký',  text: 'Hướng dẫn cách đăng ký môn học' },
  ];

  /* ── STATE ──────────────────────────────────────────────── */
  let isOpen      = false;
  let isBusy      = false;
  let greeted     = false;
  let chatHistory = [];       // { role: 'user'|'assistant', content }

  /* ── CSS INJECTION ──────────────────────────────────────── */
  function injectCSS() {
    if (document.querySelector('link[data-chatbot-css]')) return;
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.setAttribute('data-chatbot-css', '1');
    let cssHref;
    const selfSrc = SELF_SCRIPT && SELF_SCRIPT.src;
    if (selfSrc && selfSrc.includes('/js/chatbot.js')) {
      cssHref = selfSrc.replace('/js/chatbot.js', '/css/chatbot.css');
    } else if (selfSrc) {
      const scriptDir = selfSrc.substring(0, selfSrc.lastIndexOf('/'));
      cssHref = scriptDir.replace(/\/js$/, '') + '/css/chatbot.css';
    } else {
      cssHref = 'css/chatbot.css';
    }
    link.href = cssHref;
    document.head.appendChild(link);
  }

  /* ── BUILD WIDGET HTML ──────────────────────────────────── */
  function buildWidget() {
    const div = document.createElement('div');
    div.id = 'chatbot-widget';
    div.style.cssText = 'position:fixed;bottom:24px;right:24px;z-index:9999;';
    div.innerHTML = `
      <button id="chatbot-toggle" aria-label="Mở chatbot tư vấn">
        <svg id="cb-icon-chat" viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/></svg>
        <svg id="cb-icon-close" viewBox="0 0 24 24" style="display:none"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
        <span id="chatbot-badge"></span>
      </button>

      <div id="chatbot-box" role="dialog" aria-label="Trợ lý tư vấn học tập">
        <div id="chatbot-header">
          <div class="bot-avatar">🤖</div>
          <div class="bot-info">
            <h3>Trợ lý E-Learning</h3>
            <p><span class="online-dot"></span>Hoạt động 24/7</p>
          </div>
          <button id="chatbot-close" aria-label="Đóng">✕</button>
        </div>

        <div id="chatbot-quick">
          ${QUICK_ACTIONS.map(a =>
            `<button class="quick-btn" data-text="${a.text}">${a.label}</button>`
          ).join('')}
        </div>

        <div id="chatbot-messages" aria-live="polite"></div>

        <div id="chatbot-input-area">
          <textarea id="chatbot-input" rows="1" placeholder="Hỏi về khóa học, học phí, đăng ký..."></textarea>
          <button id="chatbot-send" aria-label="Gửi">
            <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
          </button>
        </div>
      </div>
    `;
    document.body.appendChild(div);
  }

  /* ── RENDER ─────────────────────────────────────────────── */
  function $(id) { return document.getElementById(id); }

  function renderMarkdown(text) {
    return text
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g,     '<em>$1</em>')
      .replace(/`(.+?)`/g,       '<code style="background:#e2e8f0;padding:1px 5px;border-radius:3px;font-size:12px">$1</code>');
  }

  function addMessage(text, role, courses, handoff) {
    const msgs = $('chatbot-messages');
    if (!msgs) return;

    const wrap = document.createElement('div');
    wrap.className = `msg ${role}`;

    let cardsHtml = '';
    if (courses && courses.length) {
      cardsHtml = courses.map(c => {
        const priceVal = parseFloat(c.price || 0);
        const priceHtml = priceVal === 0
          ? '<span class="price-free">Miễn phí</span>'
          : `<span class="price-paid">${priceVal.toLocaleString('vi-VN')}đ</span>`;
        const lvl = LEVEL_MAP[c.level] || '';
        return `
          <a class="course-card-mini" href="course-detail.html?id=${c.id}" target="_blank">
            <div class="cc-title">${c.title}</div>
            <div class="cc-meta">
              ${priceHtml}
              ${lvl ? `<span>📶 ${lvl}</span>` : ''}
              ${c.duration_hours ? `<span>⏱ ${c.duration_hours}h</span>` : ''}
              ${c.instructor ? `<span>👨‍🏫 ${c.instructor}</span>` : ''}
            </div>
          </a>`;
      }).join('');
    }

    let handoffHtml = '';
    if (handoff) {
      handoffHtml = `
        <div class="handoff-card">
          <div class="handoff-title">🙋 Đã chuyển cho nhân viên hỗ trợ</div>
          <div class="handoff-actions">
            <a class="handoff-btn" href="mailto:support@elearning.com">📧 Gửi email</a>
            <a class="handoff-btn" href="tel:0367626072">📞 Gọi hotline</a>
          </div>
        </div>`;
    }

    wrap.innerHTML = `
      <div class="msg-avatar">${role === 'bot' ? '🤖' : '👤'}</div>
      <div class="msg-body">
        <div class="msg-bubble">${renderMarkdown(text)}</div>
        ${cardsHtml}
        ${handoffHtml}
      </div>`;

    msgs.appendChild(wrap);
    msgs.scrollTop = msgs.scrollHeight;
  }

  function showTyping() {
    const msgs = $('chatbot-messages');
    if (!msgs) return;
    const el = document.createElement('div');
    el.className = 'msg bot';
    el.id = 'cb-typing';
    el.innerHTML = `
      <div class="msg-avatar">🤖</div>
      <div class="msg-body">
        <div class="typing-bubble">
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
        </div>
      </div>`;
    msgs.appendChild(el);
    msgs.scrollTop = msgs.scrollHeight;
  }

  function hideTyping() {
    const el = $('cb-typing');
    if (el) el.remove();
  }

  /* ── SEND MESSAGE (gọi backend, KHÔNG gọi Groq trực tiếp) ── */
  async function sendMessage(text) {
    text = text.trim();
    if (!text || isBusy) return;

    const input   = $('chatbot-input');
    const sendBtn = $('chatbot-send');
    if (input)   { input.value = ''; input.style.height = 'auto'; }
    if (sendBtn) sendBtn.disabled = true;

    addMessage(text, 'user');
    chatHistory.push({ role: 'user', content: text });

    isBusy = true;
    showTyping();

    const currentCourseId = new URLSearchParams(location.search).get('id');
    const onCourseDetailPage = location.pathname.includes('course-detail.html');

    try {
      const res = await fetch(CHAT_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          history: chatHistory.slice(-10),
          current_course_id: onCourseDetailPage ? currentCourseId : null,
        }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      hideTyping();
      const reply   = data.reply   || 'Xin lỗi, có lỗi xảy ra!';
      const courses = data.courses || null;
      const handoff = data.handoff || false;

      addMessage(reply, 'bot', courses, handoff);
      chatHistory.push({ role: 'assistant', content: reply });

    } catch (err) {
      hideTyping();
      addMessage('Không thể kết nối đến máy chủ. Vui lòng thử lại sau ít phút! 🙏', 'bot');
    } finally {
      isBusy = false;
      if (sendBtn) sendBtn.disabled = false;
      if (input)   input.focus();
    }
  }

  /* ── OPEN / CLOSE ───────────────────────────────────────── */
  function openChat() {
    isOpen = true;
    const box = $('chatbot-box');
    if (box) box.classList.add('open');
    $('cb-icon-chat').style.display  = 'none';
    $('cb-icon-close').style.display = 'block';
    $('chatbot-badge').style.display = 'none';

    if (!greeted) {
      greeted = true;
      setTimeout(() => {
        addMessage(
          'Xin chào! 👋 Tôi là trợ lý AI của **Smart E-Learning**.\n\n'
        + 'Tôi có thể giúp bạn:\n'
        + '📚 Tìm & tư vấn khóa học phù hợp\n'
        + '💰 Tra cứu học phí, khóa học miễn phí\n'
        + '📝 Hướng dẫn đăng ký môn học\n'
        + '❓ Giải đáp thắc mắc về hệ thống\n\n'
        + 'Bạn muốn học gì hôm nay? 😊',
          'bot'
        );
      }, 400);
    }

    setTimeout(() => { const i = $('chatbot-input'); if (i) i.focus(); }, 350);
  }

  function closeChat() {
    isOpen = false;
    const box = $('chatbot-box');
    if (box) box.classList.remove('open');
    $('cb-icon-chat').style.display  = 'block';
    $('cb-icon-close').style.display = 'none';
  }

  /* ── BIND EVENTS ─────────────────────────────────────────── */
  function bindEvents() {
    $('chatbot-toggle').addEventListener('click', () => isOpen ? closeChat() : openChat());
    $('chatbot-close').addEventListener('click', closeChat);

    document.querySelectorAll('.quick-btn').forEach(btn =>
      btn.addEventListener('click', () => sendMessage(btn.dataset.text))
    );

    $('chatbot-send').addEventListener('click', () => {
      const i = $('chatbot-input');
      if (i) sendMessage(i.value);
    });

    const input = $('chatbot-input');
    if (input) {
      input.addEventListener('keydown', e => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          sendMessage(input.value);
        }
      });
      input.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 80) + 'px';
      });
    }

    document.addEventListener('click', e => {
      const w = $('chatbot-widget');
      if (isOpen && w && !w.contains(e.target)) closeChat();
    });
  }

  /* ── INIT ────────────────────────────────────────────────── */
  function init() {
    injectCSS();
    buildWidget();
    bindEvents();

    setTimeout(() => {
      if (!isOpen) $('chatbot-badge').style.display = 'block';
    }, 3000);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();