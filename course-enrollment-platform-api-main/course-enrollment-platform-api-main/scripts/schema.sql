CREATE TYPE user_role AS ENUM ('student', 'admin');

CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL CHECK (length(trim(name)) > 0),
    email           VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    role            user_role    NOT NULL,
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE
);

CREATE TABLE courses (
    id        SERIAL PRIMARY KEY,
    title     VARCHAR(200) NOT NULL CHECK (length(trim(title)) > 0),
    code      VARCHAR(50)  NOT NULL UNIQUE,
    capacity  INTEGER      NOT NULL CHECK (capacity > 0),
    is_active BOOLEAN      NOT NULL DEFAULT TRUE
);

CREATE TABLE enrollments (
    id         SERIAL PRIMARY KEY,
    user_id    INT NOT NULL REFERENCES users(id)   ON DELETE CASCADE,
    course_id  INT NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, course_id)
);

CREATE INDEX ix_enrollments_user_id   ON enrollments(user_id);
CREATE INDEX ix_enrollments_course_id ON enrollments(course_id);
