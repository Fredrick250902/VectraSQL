CREATE DATABASE IF NOT EXISTS invoice_db;
USE invoice_db;

CREATE TABLE IF NOT EXISTS invoices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    invoice_no VARCHAR(255),
    invoice_date DATE,
    total_amt DECIMAL(10, 2),
    vendor VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);