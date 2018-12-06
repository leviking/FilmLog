ALTER TABLE Developers
  ADD COLUMN type ENUM('Black & White', 'C-41', 'E-6', 'ECN2') NOT NULL DEFAULT 'Black & White' AFTER mixedOn,
  ADD COLUMN kind ENUM('One-Shot', 'Multi-Use', 'Replenishment') NOT NULL DEFAULT 'One-Shot' AFTER type,
  DROP COLUMN replenishment;
