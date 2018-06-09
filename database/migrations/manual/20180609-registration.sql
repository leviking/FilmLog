CREATE TABLE UsersUnverified(
    userUnverifiedID INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    username varchar(64) NOT NULL,
    email varchar(255) NOT NULL,
    password varbinary(128) NOT NULL,
    registrationCode varchar(255) NOT NULL,
    UNIQUE KEY `email_uq` (`email`),
    UNIQUE KEY `username_uq` (`username`)
) ENGINE='InnoDB';

ALTER TABLE Users MODIFY COLUMN email VARCHAR(255) DEFAULT NULL;
