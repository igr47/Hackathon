-- =========================================================
-- Car Wash & Auto Detailing — Database Initialization
-- Run with: sudo mariadb < init_db.sql
-- =========================================================

-- 1. Database
CREATE DATABASE IF NOT EXISTS carwash_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- 2. App user
CREATE USER IF NOT EXISTS 'carwash_user'@'localhost' IDENTIFIED BY 'carwash_pass';
CREATE USER IF NOT EXISTS 'carwash_user'@'127.0.0.1' IDENTIFIED BY 'carwash_pass';
GRANT ALL PRIVILEGES ON carwash_db.* TO 'carwash_user'@'localhost';
GRANT ALL PRIVILEGES ON carwash_db.* TO 'carwash_user'@'127.0.0.1';
FLUSH PRIVILEGES;

USE carwash_db;

-- =========================================================
-- 3. Tables (matching SQLAlchemy models)
-- =========================================================

-- services
CREATE TABLE IF NOT EXISTS services (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  description TEXT NULL,
  price DECIMAL(10,2) NOT NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- customers
CREATE TABLE IF NOT EXISTS customers (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  phone VARCHAR(30) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_customers_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- jobs
CREATE TABLE IF NOT EXISTS jobs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  job_code VARCHAR(50) NOT NULL UNIQUE,
  service_code VARCHAR(50) NOT NULL UNIQUE,

  customer_id INT NULL,
  customer_name VARCHAR(120) NOT NULL,
  customer_phone VARCHAR(30) NOT NULL,

  plate_number VARCHAR(30) NOT NULL,
  vehicle_model VARCHAR(120) NULL,

  service_id INT NULL,
  service_name VARCHAR(100) NOT NULL,
  price DECIMAL(10,2) NOT NULL,

  operator VARCHAR(80) NULL,
  status ENUM('RECEIVED','WASHING','QUALITY CHECK','READY','PAID','COLLECTED')
    NOT NULL DEFAULT 'RECEIVED',
  payment_status VARCHAR(50) NOT NULL DEFAULT 'Pending',

  rating INT NOT NULL DEFAULT 0,
  notes TEXT NULL,

  time_in DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  time_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    ON UPDATE CURRENT_TIMESTAMP,
  time_out DATETIME NULL,

  INDEX idx_jobs_job_code (job_code),
  INDEX idx_jobs_service_code (service_code),
  INDEX idx_jobs_plate (plate_number),
  INDEX idx_jobs_phone (customer_phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- job_status_log
CREATE TABLE IF NOT EXISTS job_status_log (
  id INT AUTO_INCREMENT PRIMARY KEY,
  job_id INT NOT NULL,
  status ENUM('RECEIVED','WASHING','QUALITY CHECK','READY','PAID','COLLECTED')
    NOT NULL,
  changed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_status_log_job (job_id),
  CONSTRAINT fk_status_log_job
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================================
-- 4. Seed services
-- =========================================================
INSERT INTO services (name, description, price) VALUES
  ('Body Wash',                'Exterior body wash only',                 500.00),
  ('Full Wash + Interior',     'Full exterior and interior cleaning',    1500.00),
  ('Underwash & Engine',       'Undercarriage and engine bay cleaning',  2000.00),
  ('Executive Buff & Detail',  'Full executive detail with buffing',     4500.00),
  ('Express Wash',             'Quick exterior wash',                      10.00),
  ('Standard Clean',           'Standard exterior + interior',             20.00),
  ('Deluxe Detail',            'Deluxe full detail + wax',                 35.00),
  ('Auto Detailing',           'Complete auto detailing package',          85.00),
  ('Paint Care',               'Paint correction and protection',         120.00),
  ('Ceramic Protection',       'Ceramic coating protection',              250.00)
ON DUPLICATE KEY UPDATE price = VALUES(price);
