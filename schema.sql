CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE posts (
	id INTEGER PRIMARY KEY,
	title TEXT,
	description TEXT,
	user_id INTEGER REFERENCES users
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    post_id INTEGER REFERENCES posts,
    user_id REFERENCES users,
    comment TEXT
);

CREATE TABLE classes (
    id INTEGER PRIMARY KEY,
    title TEXT,
    value TEXT
);

CREATE TABLE post_classes (
    id INTEGER PRIMARY KEY,
    post_id INTEGER REFERENCES posts,
    title TEXT,
    value TEXT
);
