ALTER TABLE FilmTests
ADD COLUMN graph ENUM('Yes', 'No') DEFAULT 'No' AFTER expLog;
