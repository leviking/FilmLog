ALTER TABLE Users
  ADD COLUMN createdOn TIMESTAMP DEFAULT 0 AFTER password,
  ADD COLUMN lastLogin TIMESTAMP DEFAULT 0 AFTER createdOn;
