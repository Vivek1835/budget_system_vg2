-- SmartBudget database.
-- Run this ONCE when you set up. It deletes old tables, so do not run it again later.
-- Run it with:  sudo mariadb < sql/schema.sql

CREATE DATABASE IF NOT EXISTS smartbudget CHARACTER SET utf8mb4;
USE smartbudget;

DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS budgets;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categories (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE transactions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  category_id INT NOT NULL,
  type ENUM('income', 'expense') NOT NULL,
  amount DECIMAL(10, 2) NOT NULL,
  description VARCHAR(200),
  date DATE NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- One budget per user (UNIQUE), so saving a new budget replaces the old one.
CREATE TABLE budgets (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT UNIQUE NOT NULL,
  monthly_limit DECIMAL(10, 2) NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

INSERT INTO categories (name) VALUES
  ('Mat'), ('Transport'), ('Klær'), ('Fritid'), ('Annet'), ('Lønn');
