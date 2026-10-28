-- ============================================================
-- SDLC Manager — Database Schema
-- Version: 1.0
-- Ref: 03_design_erd.md
-- ============================================================

CREATE DATABASE IF NOT EXISTS sdlc_manager
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE sdlc_manager;
CREATE TABLE IF NOT EXISTS users (
  id          INT PRIMARY KEY AUTO_INCREMENT,
  username    VARCHAR(50) NOT NULL UNIQUE,
  password    VARCHAR(255) NOT NULL,                -- bcrypt hash
  role        ENUM('admin','user') DEFAULT 'user',
  is_active   TINYINT(1) DEFAULT 1,
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------- تعديل projects: ربط بالمستخدم ----------
ALTER TABLE projects
  ADD COLUMN user_id INT NULL AFTER id,
  ADD CONSTRAINT fk_projects_user
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE ON UPDATE CASCADE;

CREATE INDEX idx_projects_user ON projects(user_id);

-- ---------- 2. phases ----------
CREATE TABLE IF NOT EXISTS phases (
  id          INT PRIMARY KEY AUTO_INCREMENT,
  project_id  INT NOT NULL,                          -- FR-04
  name        VARCHAR(100) NOT NULL,                 -- FR-05
  status      ENUM('pending','in_progress','completed') DEFAULT 'pending',  -- FR-06
  order_index INT DEFAULT 0,                         -- FR-05
  FOREIGN KEY (project_id) REFERENCES projects(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE                                -- NFR-03
) ENGINE=InnoDB;

CREATE INDEX idx_phases_project ON phases(project_id);

-- ---------- 3. requirements ----------
CREATE TABLE IF NOT EXISTS requirements (
  id          INT PRIMARY KEY AUTO_INCREMENT,
  project_id  INT NOT NULL,                          -- FR-07
  title       VARCHAR(200) NOT NULL,                 -- FR-07
  description TEXT,                                  -- FR-07
  status      ENUM('open','done') DEFAULT 'open',    -- FR-01
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES projects(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE                                -- NFR-03
) ENGINE=InnoDB;

CREATE INDEX idx_requirements_project ON requirements(project_id);

-- ---------- 4. audit_log ----------
CREATE TABLE IF NOT EXISTS audit_log (
  id          INT PRIMARY KEY AUTO_INCREMENT,
  action      VARCHAR(50) NOT NULL,                  -- FR-11
  entity_type VARCHAR(50) NOT NULL,                  -- FR-11
  entity_id   INT,                                    -- FR-11
  details     TEXT,                                   -- FR-11
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP    -- FR-11
) ENGINE=InnoDB;

CREATE INDEX idx_audit_created ON audit_log(created_at DESC);