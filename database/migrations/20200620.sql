ALTER TABLE Holders
ADD COLUMN status ENUM ('Active', 'Retired') DEFAULT 'Active' NOT NULL AFTER size;
