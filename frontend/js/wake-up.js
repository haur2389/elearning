// Wake up Render backend - ping trước khi load trang
(async function wakeUpBackend() {
    const BACKEND = 'https://elearning-backend-ead0.onrender.com';
    
    // Hiển thị banner loading nếu backend chưa sẵn sàng
    let banner = null;
    let wakeTimeout = setTimeout(() => {
        banner = document.createElement('div');
        banner.id = 'wake-banner';
        banner.className = 'fixed top-0 left-0 right-0 z-50 bg-yellow-500 text-white text-center py-2 text-sm font-medium';
        banner.innerHTML = '⏳ Đang khởi động server Cloud... Vui lòng chờ 30 giây <span id="wake-count">30</span>s';
        document.body.prepend(banner);
        
        let count = 30;
        const counter = setInterval(() => {
            count--;
            const el = document.getElementById('wake-count');
            if (el) el.textContent = count;
            if (count <= 0) clearInterval(counter);
        }, 1000);
    }, 2000);

    try {
        const start = Date.now();
        await fetch(`${BACKEND}/api/courses/categories/`, { method: 'GET', mode: 'cors' });
        clearTimeout(wakeTimeout);
        const elapsed = Date.now() - start;
        
        // Nếu nhanh thì ẩn banner
        if (banner) {
            banner.className = 'fixed top-0 left-0 right-0 z-50 bg-green-500 text-white text-center py-2 text-sm font-medium';
            banner.textContent = '✅ Server sẵn sàng! Đang tải dữ liệu...';
            setTimeout(() => banner?.remove(), 2000);
        }
    } catch {
        clearTimeout(wakeTimeout);
        if (banner) {
            banner.textContent = '❌ Không kết nối được server. Kiểm tra lại đường truyền.';
        }
    }
})();
