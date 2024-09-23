-- V1__create_notes_table.sql
-- Migration to create the 'notes' table

CREATE TABLE IF NOT EXISTS `notes` (
    `note_id` INT(11) AUTO_INCREMENT PRIMARY KEY,
    `note_title` VARCHAR(255) NOT NULL,
    `note_text` TEXT NOT NULL,
    `is_public` BOOLEAN NOT NULL DEFAULT FALSE,
    `author_id` INT(11) NOT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_author_id` (`author_id`),
    CONSTRAINT `fk_notes_author_id`
        FOREIGN KEY (`author_id`)
        REFERENCES `users`(`user_id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
