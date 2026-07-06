/**
 * Smart E-Learning — Notification Bell cho trang Admin / Giảng viên
 *
 * Các trang admin/*.html và instructor/*.html trước đây KHÔNG có chuông
 * thông báo nào cả (chỉ index.html mới có), nên dù backend có tạo thông
 * báo cho giảng viên/admin (vd "học viên vừa nộp bài", "có đăng ký khóa
 * học mới"...) thì cũng không ai nhìn thấy được.
 *
 * File này tự tìm nút "Đăng xuất" (button onclick="Auth.logout()") đã có
 * sẵn trên mọi trang admin/instructor và chèn chuông + dropdown ngay
 * trước nút đó — không cần sửa tay từng file HTML. Dùng class Tailwind có
 * sẵn (CDN đã load trên các trang này) thay vì 1 file CSS riêng, để tránh
 * lặp lại lỗi 404 đường dẫn CSS đã từng gặp với chatbot.css.
 */
(function () {
  'use strict';

  function $(id) { return document.getElementById(id); }

  function escapeHtml(str) {
    const d = document.createElement('div');
    d.textContent = str == null ? '' : String(str);
    return d.innerHTML;
  }

  function formatDate(iso) {
    try {
      const d = new Date(iso);
      return d.toLocaleString('vi-VN', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
    } catch { return ''; }
  }

  async function loadUnreadCount() {
    try {
      const data = await API.get('/notifications/unread/');
      const badge = $('nb-badge');
      if (!badge) return;
      if (data && data.unread_count > 0) {
        badge.textContent = data.unread_count > 99 ? '99+' : data.unread_count;
        badge.classList.remove('hidden');
      } else {
        badge.classList.add('hidden');
      }
    } catch { /* im lặng nếu lỗi mạng, không làm phiền người dùng */ }
  }

  async function loadList() {
    const box = $('nb-list');
    if (!box) return;
    box.innerHTML = '<div class="p-4 text-center text-gray-400 text-sm">Đang tải...</div>';
    try {
      const list = await API.get('/notifications/');
      const items = Array.isArray(list) ? list : (list?.results || []);
      if (!items.length) {
        box.innerHTML = '<div class="p-4 text-center text-gray-400 text-sm">Không có thông báo nào</div>';
        return;
      }
      box.innerHTML = items.map(n => `
        <a href="${escapeHtml(n.link || '#')}" data-nid="${n.id}"
           class="nb-item block p-3 hover:bg-gray-50 ${n.is_read ? '' : 'bg-blue-50'}">
          <div class="font-medium text-sm text-gray-800">${escapeHtml(n.title)}</div>
          <div class="text-xs text-gray-500 mt-0.5">${escapeHtml(n.message)}</div>
          <div class="text-xs text-gray-400 mt-1">${formatDate(n.created_at)}</div>
        </a>`).join('');

      box.querySelectorAll('.nb-item').forEach(el => {
        el.addEventListener('click', () => markRead(el.dataset.nid));
      });
    } catch {
      box.innerHTML = '<div class="p-4 text-center text-red-400 text-sm">Lỗi tải thông báo</div>';
    }
  }

  async function markRead(id) {
    try { await API.post(`/notifications/${id}/read/`); } catch {}
  }

  async function markAllRead() {
    try {
      await API.post('/notifications/mark-read/');
      $('nb-badge')?.classList.add('hidden');
      await loadList();
    } catch {}
  }
  window.NotifBell = { markAllRead };

  function buildWidget() {
    const wrap = document.createElement('div');
    wrap.className = 'relative inline-block';
    wrap.innerHTML = `
      <button id="nb-toggle" type="button" aria-label="Thông báo"
        class="relative text-gray-500 hover:text-blue-600 text-lg leading-none px-1">
        🔔<span id="nb-badge" class="hidden absolute -top-1.5 -right-1.5 bg-red-500 text-white text-[10px] font-semibold rounded-full min-w-[16px] h-4 px-1 flex items-center justify-center">0</span>
      </button>
      <div id="nb-dropdown" class="hidden absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-2xl border z-50 max-h-96 overflow-y-auto">
        <div class="p-3 border-b font-semibold text-gray-700 flex justify-between items-center text-sm">
          <span>Thông báo</span>
          <button onclick="NotifBell.markAllRead()" class="text-xs text-blue-600 hover:underline font-normal">Đánh dấu đã đọc</button>
        </div>
        <div id="nb-list" class="divide-y"></div>
      </div>`;
    return wrap;
  }

  function bindToggle() {
    $('nb-toggle').addEventListener('click', async (e) => {
      e.preventDefault();
      e.stopPropagation();
      const dd = $('nb-dropdown');
      const willOpen = dd.classList.contains('hidden');
      dd.classList.toggle('hidden');
      if (willOpen) await loadList();
    });
    document.addEventListener('click', (e) => {
      const dd = $('nb-dropdown');
      if (dd && !dd.classList.contains('hidden') && !dd.contains(e.target) && e.target.id !== 'nb-toggle') {
        dd.classList.add('hidden');
      }
    });
  }

  function init() {
    if (typeof Auth === 'undefined' || !Auth.isLoggedIn()) return; // trang admin/instructor luôn yêu cầu đăng nhập
    if ($('nb-toggle')) return; // đã inject rồi, tránh chèn trùng

    const logoutBtn = document.querySelector('button[onclick*="Auth.logout"]');
    if (!logoutBtn || !logoutBtn.parentNode) return; // không tìm thấy chỗ neo -> bỏ qua, không phá layout

    logoutBtn.parentNode.insertBefore(buildWidget(), logoutBtn);
    bindToggle();
    loadUnreadCount();

    // Cập nhật lại số chưa đọc khi quay lại tab (không cần polling liên tục)
    window.addEventListener('focus', loadUnreadCount);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
