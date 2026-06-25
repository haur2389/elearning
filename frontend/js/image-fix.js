// Fix ảnh bị lỗi - chạy sau khi DOM load
document.addEventListener('DOMContentLoaded', function() {
    // Fix tất cả ảnh bị lỗi
    document.querySelectorAll('img').forEach(img => {
        img.addEventListener('error', function() {
            const title = this.alt || '';
            this.src = UI.getCategoryImage('', title);
            this.onerror = function() {
                this.src = 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400&h=220&fit=crop';
                this.onerror = null;
            };
        });
    });
});
