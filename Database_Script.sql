-- =====================================================================
-- DATABASE SCRIPT
-- HE THONG HOC TRUC TUYEN THONG MINH (Smart E-Learning)
-- Sinh ra tu Django models thuc te (backend/apps/*/models.py)
-- DBMS: PostgreSQL (tuong thich SQLite khi phat trien local qua Django ORM)
-- =====================================================================

-- =========================
-- 1. USERS (apps.users)
-- =========================
CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    password        VARCHAR(128) NOT NULL,
    last_login      TIMESTAMP NULL,
    is_superuser    BOOLEAN NOT NULL DEFAULT FALSE,
    username        VARCHAR(150) UNIQUE NOT NULL,
    first_name      VARCHAR(150) NOT NULL DEFAULT '',
    last_name       VARCHAR(150) NOT NULL DEFAULT '',
    is_staff        BOOLEAN NOT NULL DEFAULT FALSE,
    date_joined     TIMESTAMP NOT NULL DEFAULT NOW(),
    email           VARCHAR(254) UNIQUE NOT NULL,
    full_name       VARCHAR(255) DEFAULT '',
    phone           VARCHAR(15) DEFAULT '',
    avatar          VARCHAR(255) NULL,
    role            VARCHAR(20) NOT NULL DEFAULT 'student' CHECK (role IN ('admin','instructor','student')),
    bio             TEXT DEFAULT '',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    otp_code        VARCHAR(6) DEFAULT '',
    otp_expiry      TIMESTAMP NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

-- =========================
-- 2. CATEGORIES (apps.courses)
-- =========================
CREATE TABLE categories (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    slug            VARCHAR(50) UNIQUE NOT NULL,
    description     TEXT DEFAULT '',
    icon            VARCHAR(50) DEFAULT '',
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

-- =========================
-- 3. COURSES
-- =========================
CREATE TABLE courses (
    id              SERIAL PRIMARY KEY,
    instructor_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id     INTEGER NULL REFERENCES categories(id) ON DELETE SET NULL,
    title           VARCHAR(255) NOT NULL,
    slug            VARCHAR(50) UNIQUE,
    description     TEXT NOT NULL,
    thumbnail       VARCHAR(500) NULL,
    price           NUMERIC(10,2) NOT NULL DEFAULT 0,
    level           VARCHAR(20) NOT NULL DEFAULT 'beginner' CHECK (level IN ('beginner','intermediate','advanced')),
    status          VARCHAR(20) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','published','archived')),
    duration_hours  INTEGER NOT NULL DEFAULT 0,
    requirements    TEXT DEFAULT '',
    objectives      TEXT DEFAULT '',
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_courses_instructor ON courses(instructor_id);
CREATE INDEX idx_courses_category ON courses(category_id);

-- =========================
-- 4. CHAPTERS
-- =========================
CREATE TABLE chapters (
    id              SERIAL PRIMARY KEY,
    course_id       INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    title           VARCHAR(255) NOT NULL,
    "order"         INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_chapters_course ON chapters(course_id);

-- =========================
-- 5. LESSONS (apps.lessons)
-- =========================
CREATE TABLE lessons (
    id              SERIAL PRIMARY KEY,
    chapter_id      INTEGER NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    title           VARCHAR(255) NOT NULL,
    content_type    VARCHAR(20) NOT NULL DEFAULT 'video' CHECK (content_type IN ('video','pdf','text','slide')),
    video_url       VARCHAR(200) DEFAULT '',
    pdf_file        VARCHAR(255) NULL,
    slide_url       VARCHAR(200) DEFAULT '',
    content         TEXT DEFAULT '',
    duration        INTEGER NOT NULL DEFAULT 0,
    "order"         INTEGER NOT NULL DEFAULT 0,
    is_preview      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_lessons_chapter ON lessons(chapter_id);

CREATE TABLE lesson_progress (
    id                  SERIAL PRIMARY KEY,
    student_id          INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    lesson_id           INTEGER NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    watch_percentage    INTEGER NOT NULL DEFAULT 0,
    is_completed        BOOLEAN NOT NULL DEFAULT FALSE,
    last_watched        TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (student_id, lesson_id)
);

-- =========================
-- 6. ENROLLMENTS / PAYMENT / CERTIFICATE (apps.enrollments)
-- =========================
CREATE TABLE enrollments (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id       INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    progress        INTEGER NOT NULL DEFAULT 0,
    is_completed    BOOLEAN NOT NULL DEFAULT FALSE,
    enrolled_at     TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMP NULL,
    UNIQUE (student_id, course_id)
);
CREATE INDEX idx_enrollments_student ON enrollments(student_id);
CREATE INDEX idx_enrollments_course ON enrollments(course_id);

CREATE TABLE payments (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id       INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    amount          NUMERIC(10,2) NOT NULL DEFAULT 0,
    method          VARCHAR(20) NOT NULL DEFAULT 'free' CHECK (method IN ('momo','vnpay','zalopay','bank_transfer','free')),
    status          VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','completed','failed','refunded')),
    transaction_id  VARCHAR(100) DEFAULT '',
    note            TEXT DEFAULT '',
    paid_at         TIMESTAMP NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE certificates (
    id                  SERIAL PRIMARY KEY,
    student_id          INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id           INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    certificate_code    VARCHAR(50) UNIQUE NOT NULL,
    issued_at           TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (student_id, course_id)
);

-- =========================
-- 7. ASSIGNMENTS (apps.assignments)
-- =========================
CREATE TABLE assignments (
    id              SERIAL PRIMARY KEY,
    course_id       INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    title           VARCHAR(255) NOT NULL,
    description     TEXT NOT NULL,
    deadline        TIMESTAMP NOT NULL,
    max_score       INTEGER NOT NULL DEFAULT 100,
    attachment      VARCHAR(255) NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE submissions (
    id              SERIAL PRIMARY KEY,
    assignment_id   INTEGER NOT NULL REFERENCES assignments(id) ON DELETE CASCADE,
    student_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    file            VARCHAR(255) NOT NULL,
    note            TEXT DEFAULT '',
    score           DOUBLE PRECISION NULL,
    feedback        TEXT DEFAULT '',
    status          VARCHAR(20) NOT NULL DEFAULT 'submitted' CHECK (status IN ('submitted','graded','late')),
    submitted_at    TIMESTAMP NOT NULL DEFAULT NOW(),
    graded_at       TIMESTAMP NULL,
    UNIQUE (assignment_id, student_id)
);

-- =========================
-- 8. EXAMS (apps.exams)
-- =========================
CREATE TABLE exams (
    id                  SERIAL PRIMARY KEY,
    course_id           INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    title               VARCHAR(255) NOT NULL,
    description         TEXT DEFAULT '',
    duration_minutes    INTEGER NOT NULL DEFAULT 30,
    total_questions     INTEGER NOT NULL DEFAULT 10,
    pass_score          INTEGER NOT NULL DEFAULT 50,
    is_random           BOOLEAN NOT NULL DEFAULT TRUE,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE questions (
    id              SERIAL PRIMARY KEY,
    exam_id         INTEGER NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
    content         TEXT NOT NULL,
    question_type   VARCHAR(20) NOT NULL DEFAULT 'multiple_choice'
                        CHECK (question_type IN ('multiple_choice','true_false','fill_blank','essay')),
    option_a        VARCHAR(500) DEFAULT '',
    option_b        VARCHAR(500) DEFAULT '',
    option_c        VARCHAR(500) DEFAULT '',
    option_d        VARCHAR(500) DEFAULT '',
    correct_answer  VARCHAR(500) NOT NULL,
    points          INTEGER NOT NULL DEFAULT 1,
    "order"         INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX idx_questions_exam ON questions(exam_id);

CREATE TABLE exam_results (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    exam_id         INTEGER NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
    score           DOUBLE PRECISION NOT NULL DEFAULT 0,
    total_points    INTEGER NOT NULL DEFAULT 0,
    earned_points   INTEGER NOT NULL DEFAULT 0,
    is_passed       BOOLEAN NOT NULL DEFAULT FALSE,
    answers         JSONB NOT NULL DEFAULT '{}',
    started_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    submitted_at    TIMESTAMP NULL,
    time_spent      INTEGER NOT NULL DEFAULT 0
);

-- =========================
-- 9. REVIEWS (apps.reviews)
-- =========================
CREATE TABLE reviews (
    id                  SERIAL PRIMARY KEY,
    course_id           INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    student_id          INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    rating              INTEGER NOT NULL DEFAULT 5,
    comment             TEXT DEFAULT '',
    instructor_reply    TEXT NULL,
    replied_at          TIMESTAMP NULL,
    created_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (course_id, student_id)
);

-- =========================
-- 10. FORUM (apps.forum)
-- =========================
CREATE TABLE forum_posts (
    id              SERIAL PRIMARY KEY,
    course_id       INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    author_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title           VARCHAR(255) NOT NULL,
    content         TEXT NOT NULL,
    is_pinned       BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE forum_replies (
    id              SERIAL PRIMARY KEY,
    post_id         INTEGER NOT NULL REFERENCES forum_posts(id) ON DELETE CASCADE,
    author_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content         TEXT NOT NULL,
    is_solution     BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

-- =========================
-- 11. NOTIFICATIONS (apps.notifications)
-- =========================
CREATE TABLE notifications (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title           VARCHAR(255) NOT NULL,
    message         TEXT NOT NULL,
    notif_type      VARCHAR(30) NOT NULL DEFAULT 'system'
                        CHECK (notif_type IN ('new_lesson','new_assignment','assignment_graded','exam_result','new_reply','system')),
    is_read         BOOLEAN NOT NULL DEFAULT FALSE,
    link            VARCHAR(255) DEFAULT '',
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_notifications_user ON notifications(user_id);

-- =====================================================================
-- SEED DATA MAU (tuong ung management command seed_data / seed_courses_full)
-- =====================================================================

-- Tai khoan mau (mat khau da duoc hash boi Django, day chi la vi du minh hoa)
INSERT INTO categories (name, slug, description) VALUES
('Lap trinh', 'lap-trinh', 'Cac khoa hoc lap trinh, phat trien phan mem'),
('Thiet ke', 'thiet-ke', 'Thiet ke do hoa, UI/UX'),
('Marketing', 'marketing', 'Marketing va kinh doanh online'),
('Data Science', 'data-science', 'Khoa hoc du lieu, AI, Machine Learning'),
('Ngoai ngu', 'ngoai-ngu', 'Cac khoa hoc ngoai ngu');

-- Ghi chu: du lieu chi tiet cho users, courses, lessons, exams... duoc sinh tu dong
-- boi cac Django management command:
--   python manage.py seed_data
--   python manage.py seed_courses_full
-- (xem chi tiet trong backend/apps/*/management/commands/)
