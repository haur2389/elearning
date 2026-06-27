const CONFIG = {
    API_BASE_URL: 'https://elearning-backend-ead6.onrender.com/api/',
    APP_NAME: 'Smart E-Learning',
};

// ── API HELPER ────────────────────────────────────────────────────────
const API = {
    getHeaders(auth = true) {
        const headers = { 'Content-Type': 'application/json' };
        if (auth) {
            const token = localStorage.getItem('access_token');
            if (token) headers['Authorization'] = `Bearer ${token}`;
        }
        return headers;
    },
    async request(method, endpoint, data = null, isForm = false) {
        const url = `${CONFIG.API_BASE_URL}${endpoint}`;
        const options = {
            method,
            headers: isForm ? { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` } : this.getHeaders(),
        };
        if (data) options.body = isForm ? data : JSON.stringify(data);
        try {
            const res = await fetch(url, options);
            if (res.status === 401) {
                const refreshed = await this.refreshToken();
                if (refreshed) return this.request(method, endpoint, data, isForm);
                Auth.logout(); return null;
            }
            const json = await res.json().catch(() => ({}));
            if (!res.ok) throw { status: res.status, data: json };
            return json;
        } catch (err) {
            if (err.status) throw err;
            throw { status: 0, data: { error: 'Không thể kết nối server.' } };
        }
    },
    async refreshToken() {
        const refresh = localStorage.getItem('refresh_token');
        if (!refresh) return false;
        try {
            const res = await fetch(`${CONFIG.API_BASE_URL}/auth/token/refresh/`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh }),
            });
            if (res.ok) { const d = await res.json(); localStorage.setItem('access_token', d.access); return true; }
        } catch {}
        return false;
    },
    get:      (ep)       => API.request('GET',    ep),
    post:     (ep, data) => API.request('POST',   ep, data),
    put:      (ep, data) => API.request('PUT',    ep, data),
    patch:    (ep, data) => API.request('PATCH',  ep, data),
    delete:   (ep)       => API.request('DELETE', ep),
    postForm: (ep, fd)   => API.request('POST',   ep, fd, true),
};

// ── AUTH HELPER ───────────────────────────────────────────────────────
const Auth = {
    login(tokens, user) {
        localStorage.setItem('access_token', tokens.access);
        localStorage.setItem('refresh_token', tokens.refresh);
        localStorage.setItem('user', JSON.stringify(user));
    },
    logout()     { localStorage.clear(); window.location.href = '/login.html'; },
    getUser()    { const u = localStorage.getItem('user'); return u ? JSON.parse(u) : null; },
    isLoggedIn() { return !!localStorage.getItem('access_token'); },
    requireLogin() { if (!this.isLoggedIn()) { window.location.href = '/login.html'; return false; } return true; },
    requireRole(role) {
        const user = this.getUser();
        if (!user || user.role !== role) { alert('Bạn không có quyền truy cập!'); window.location.href = '/index.html'; return false; }
        return true;
    },
};

// ── ẢNH THẬT CHO TỪNG MÔN HỌC (Google/Unsplash) ─────────────────────
// Key = từ khóa trong tên môn học (lowercase), Value = URL ảnh thật
const COURSE_IMAGES = {
    // Từ khóa ngắn - ưu tiên match trước
    'python':               'https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=500&h=300&fit=crop&auto=format',
    'java':                 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=500&h=300&fit=crop&auto=format',
    'javascript':           'https://images.unsplash.com/photo-1627398242454-45a1465c2479?w=500&h=300&fit=crop&auto=format',
    'react':                'https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=500&h=300&fit=crop&auto=format',
    'html':                 'https://images.unsplash.com/photo-1547658719-da2b51169166?w=500&h=300&fit=crop&auto=format',
    'css':                  'https://images.unsplash.com/photo-1561070791-2526d30994b5?w=500&h=300&fit=crop&auto=format',
    'node':                 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=500&h=300&fit=crop&auto=format',
    'sql':                  'https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=500&h=300&fit=crop&auto=format',
    'mysql':                'https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=500&h=300&fit=crop&auto=format',
    'docker':               'https://images.unsplash.com/photo-1605745341112-85968b19335b?w=500&h=300&fit=crop&auto=format',
    'git':                  'https://images.unsplash.com/photo-1618401471353-b98afee0b2eb?w=500&h=300&fit=crop&auto=format',
    'linux':                'https://images.unsplash.com/photo-1629654297299-c8506221ca97?w=500&h=300&fit=crop&auto=format',
    'android':              'https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=500&h=300&fit=crop&auto=format',
    'ios':                  'https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=500&h=300&fit=crop&auto=format',
    'flutter':              'https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=500&h=300&fit=crop&auto=format',
    'c++':                  'https://images.unsplash.com/photo-1542831371-29b0f74f9713?w=500&h=300&fit=crop&auto=format',
    'c#':                   'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=500&h=300&fit=crop&auto=format',
    'php':                  'https://images.unsplash.com/photo-1516116216624-53e697fedbea?w=500&h=300&fit=crop&auto=format',
    // Cụm từ dài
    'nhập môn lập trình':   'https://images.unsplash.com/photo-1587620962725-abab19836100?w=500&h=300&fit=crop&auto=format',
    'cơ sở dữ liệu':        'https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=500&h=300&fit=crop&auto=format',
    'lập trình web':         'https://images.unsplash.com/photo-1547658719-da2b51169166?w=500&h=300&fit=crop&auto=format',
    'trí tuệ nhân tạo':     'https://images.unsplash.com/photo-1677442135703-1787eea5ce01?w=500&h=300&fit=crop&auto=format',
    'điện toán đám mây':    'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=500&h=300&fit=crop&auto=format',
    'an toàn thông tin':    'https://images.unsplash.com/photo-1614064641938-3bbee52942c7?w=500&h=300&fit=crop&auto=format',
    'mạng máy tính':        'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=500&h=300&fit=crop&auto=format',
    'hướng đối tượng':      'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=500&h=300&fit=crop&auto=format',
    'cấu trúc dữ liệu':     'https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=500&h=300&fit=crop&auto=format',
    'học máy':               'https://images.unsplash.com/photo-1535378917042-10a22c95931a?w=500&h=300&fit=crop&auto=format',
    'machine learning':     'https://images.unsplash.com/photo-1535378917042-10a22c95931a?w=500&h=300&fit=crop&auto=format',
    'deep learning':        'https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=500&h=300&fit=crop&auto=format',
    'học sâu':               'https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=500&h=300&fit=crop&auto=format',
    'khoa học dữ liệu':     'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=500&h=300&fit=crop&auto=format',
    'data science':         'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=500&h=300&fit=crop&auto=format',
    'thiết kế web':          'https://images.unsplash.com/photo-1561070791-2526d30994b5?w=500&h=300&fit=crop&auto=format',
    'lập trình game':        'https://images.unsplash.com/photo-1511512578047-dfb367046420?w=500&h=300&fit=crop&auto=format',
    'thiết bị di động':     'https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=500&h=300&fit=crop&auto=format',
    'an ninh mạng':          'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=500&h=300&fit=crop&auto=format',
    'kiểm thử':              'https://images.unsplash.com/photo-1516116216624-53e697fedbea?w=500&h=300&fit=crop&auto=format',
    'iot':                   'https://images.unsplash.com/photo-1558346490-a72e53ae2d4f?w=500&h=300&fit=crop&auto=format',
    // Danh mục fallback ngắn
    'lập trình':             'https://images.unsplash.com/photo-1587620962725-abab19836100?w=500&h=300&fit=crop&auto=format',
    'hệ thống':              'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=500&h=300&fit=crop&auto=format',
    'mạng':                  'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=500&h=300&fit=crop&auto=format',
    'bảo mật':               'https://images.unsplash.com/photo-1614064641938-3bbee52942c7?w=500&h=300&fit=crop&auto=format',
    'dữ liệu':               'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=500&h=300&fit=crop&auto=format',
    'web':                   'https://images.unsplash.com/photo-1547658719-da2b51169166?w=500&h=300&fit=crop&auto=format',
    'mobile':                'https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=500&h=300&fit=crop&auto=format',
    'default':               'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=500&h=300&fit=crop&auto=format',
};

// ── UI HELPER ─────────────────────────────────────────────────────────
const UI = {
    showAlert(message, type = 'success', duration = 3000) {
        const existing = document.getElementById('alert-toast');
        if (existing) existing.remove();
        const colors = { success:'bg-green-500', error:'bg-red-500', warning:'bg-yellow-500', info:'bg-blue-500' };
        const icons  = { success:'✅', error:'❌', warning:'⚠️', info:'ℹ️' };
        const toast  = document.createElement('div');
        toast.id     = 'alert-toast';
        toast.className = `fixed top-5 right-5 z-50 ${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-2`;
        toast.innerHTML = `<span>${icons[type]}</span><span>${message}</span>`;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), duration);
    },

    formatPrice(price) {
        if (!price || price == 0 || price === '0.00')
            return '<span class="text-green-600 font-bold">Miễn phí</span>';
        return `<span class="text-blue-600 font-bold">${parseInt(price).toLocaleString('vi-VN')}đ</span>`;
    },

    formatDate(dateStr) {
        if (!dateStr) return '';
        return new Date(dateStr).toLocaleDateString('vi-VN');
    },

    renderStars(rating) {
        const full = Math.floor(rating || 0);
        return '<span class="text-yellow-400">' + '★'.repeat(full) + '<span class="text-gray-300">' + '★'.repeat(5-full) + '</span></span>';
    },

    levelBadge(level) {
        const map = {
            beginner:     ['Cơ bản',    'bg-green-100 text-green-700'],
            intermediate: ['Trung cấp', 'bg-yellow-100 text-yellow-700'],
            advanced:     ['Nâng cao',  'bg-red-100 text-red-700'],
        };
        const [label, cls] = map[level] || ['', ''];
        return `<span class="px-2 py-1 rounded-full text-xs font-medium ${cls}">${label}</span>`;
    },

    roleBadge(role) {
        const map = {
            admin:      ['Admin',      'bg-red-100 text-red-700'],
            instructor: ['Giảng viên', 'bg-blue-100 text-blue-700'],
            student:    ['Sinh viên',  'bg-green-100 text-green-700'],
        };
        const [label, cls] = map[role] || ['', ''];
        return `<span class="px-2 py-1 rounded-full text-xs font-medium ${cls}">${label}</span>`;
    },

    // Lấy ảnh theo tên môn học - tìm từ khóa trong tên
    getCourseImage(title, categoryName) {
        if (!title) return COURSE_IMAGES['default'];
        const t = title.toLowerCase();
        // Tìm chính xác theo từ khóa
        for (const [key, url] of Object.entries(COURSE_IMAGES)) {
            if (key === 'default') continue;
            if (t.includes(key)) return url;
        }
        // Tìm theo danh mục
        if (categoryName) {
            const c = categoryName.toLowerCase();
            for (const [key, url] of Object.entries(COURSE_IMAGES)) {
                if (key === 'default') continue;
                if (c.includes(key) || key.includes(c.split(' ')[0])) return url;
            }
        }
        return COURSE_IMAGES['default'];
    },

    // Tương thích ngược với code cũ
    getCategoryImage(categoryName, title) {
        return this.getCourseImage(title, categoryName);
    },
};
