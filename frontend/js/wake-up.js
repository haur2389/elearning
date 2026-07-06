// Wake up Render backend - ping với retry và timeout dài hơn
(async function wakeUpBackend() {
    const BACKEND = 'https://elearning-backend-ead6.onrender.com';
    const MAX_WAIT = 60; // Render cold start có thể mất đến 60s

    let banner = null;
    let countInterval = null;

    // Hiển thị banner sau 1.5s nếu server chưa phản hồi
    let wakeTimeout = setTimeout(() => {
        banner = document.createElement('div');
        banner.id = 'wake-banner';
        banner.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:9999;background:#f59e0b;color:#fff;text-align:center;padding:10px;font-size:14px;font-weight:500;';
        banner.innerHTML = `⏳ Đang khởi động server (lần đầu mất ~60s)... <span id="wake-count">${MAX_WAIT}</span>s`;
        document.body.prepend(banner);

        let count = MAX_WAIT;
        countInterval = setInterval(() => {
            count--;
            const el = document.getElementById('wake-count');
            if (el) el.textContent = Math.max(0, count);
            if (count <= 0) {
                clearInterval(countInterval);
                if (banner) banner.innerHTML = '⌛ Server đang khởi động, vui lòng thử lại sau...';
            }
        }, 1000);
    }, 1500);

    // Retry ping tối đa 3 lần
    let success = false;
    for (let attempt = 1; attempt <= 3; attempt++) {
        try {
            const ctrl = new AbortController();
            const timer = setTimeout(() => ctrl.abort(), 65000); // 65s timeout mỗi lần
            await fetch(`${BACKEND}/api/courses/categories/`, {
                method: 'GET', mode: 'cors', signal: ctrl.signal
            });
            clearTimeout(timer);
            success = true;
            break;
        } catch (err) {
            if (attempt === 3) break;
            // Đợi 2s rồi thử lại
            await new Promise(r => setTimeout(r, 2000));
        }
    }

    clearTimeout(wakeTimeout);
    if (countInterval) clearInterval(countInterval);

    if (banner) {
        if (success) {
            banner.style.background = '#10b981';
            banner.textContent = '✅ Server sẵn sàng! Đang tải dữ liệu...';
            setTimeout(() => banner?.remove(), 2000);
        } else {
            banner.style.background = '#ef4444';
            banner.innerHTML = '❌ Không thể kết nối server. <a href="javascript:location.reload()" style="text-decoration:underline;color:#fff;">Thử lại</a> hoặc kiểm tra đường truyền.';
        }
    }
})();
