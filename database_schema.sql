CREATE DATABASE pennyperfect;

CREATE TABLE IF NOT EXISTS users (
    id SERIAL NOT NULL,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL,
    pfpic VARCHAR(255) NULL,
    bio TEXT NULL,
    hashpw VARCHAR(255) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (username, email)
);

CREATE TABLE IF NOT EXISTS expense (
    id SERIAL NOT NULL,
    name VARCHAR(100) NOT NULL,
    amount FLOAT NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    PRIMARY KEY (id)
);

Create TABLE IF NOT EXISTS loan (
    loan_id SERIAL NOT NULL,
    name VARCHAR(100) NOT NULL,
    amount FLOAT NOT NULL,
    interest_rate DECIMAL(10,2) NOT NULL,
    term_months DATE NOT NULL,
    user_id INTEGER NOT NULL,
    PRIMARY KEY (id)
);