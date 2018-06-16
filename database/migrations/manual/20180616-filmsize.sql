DROP TABLE IF EXISTS FilmSizes;

CREATE TABLE FilmSizes (
    filmSizeID TINYINT UNSIGNED NOT NULL PRIMARY KEY,
    size VARCHAR(32),
    type ENUM('Miniature', 'Small', 'Medium', 'Large', 'Ultra-Large') NOT NULL,
    format ENUM('Roll', 'Sheet')
) ENGINE='InnoDB';

INSERT INTO FilmSizes VALUES (1, '35mm 12', 'Small', 'Roll');
INSERT INTO FilmSizes VALUES (2, '35mm 24', 'Small', 'Roll');
INSERT INTO FilmSizes VALUES (3, '35mm 36', 'Small', 'Roll');
INSERT INTO FilmSizes VALUES (4, '35mm Hand Roll', 'Small', 'Roll');
INSERT INTO FilmSizes VALUES (5, '120', 'Medium', 'Roll');
INSERT INTO FilmSizes VALUES (6, '220', 'Medium', 'Roll');
INSERT INTO FilmSizes VALUES (7, '4x5', 'Large', 'Sheet');
INSERT INTO FilmSizes VALUES (8, '5x7', 'Large', 'Sheet');
INSERT INTO FilmSizes VALUES (9, '8x10', 'Large', 'Sheet');
INSERT INTO FilmSizes VALUES (10,'11x14', 'Ultra-Large', 'Sheet');

-- ALTER TABLE FilmStock ADD COLUMN filmSizeID TINYINT UNSIGNED NOT NULL AFTER filmSize;

UPDATE FilmStock SET filmSizeID = 2 WHERE filmSize = '35mm 24';
UPDATE FilmStock SET filmSizeID = 3 WHERE filmSize = '35mm 36';
UPDATE FilmStock SET filmSizeID = 4 WHERE filmSize = '35mm Hand Roll';
UPDATE FilmStock SET filmSizeID = 5 WHERE filmSize = '120';
UPDATE FilmStock SET filmSizeID = 6 WHERE filmSize = '220';
UPDATE FilmStock SET filmSizeID = 7 WHERE filmSize = '4x5';
UPDATE FilmStock SET filmSizeID = 9 WHERE filmSize = '8x10';

SET FOREIGN_KEY_CHECKS=0;
ALTER TABLE FilmStock DROP FOREIGN KEY FilmSTock_filmTypeID_fk;
ALTER TABLE FilmStock DROP FOREIGN KEY FilmStock_userID;
ALTER TABLE FilmStock DROP PRIMARY KEY;
ALTER TABLE FilmStock ADD PRIMARY KEY (userID, filmTypeID, filmSizeID);

ALTER TABLE FilmStock 
    ADD CONSTRAINT FilmStock_userID FOREIGN KEY (userID) REFERENCES Users (userID) ON DELETE CASCADE ON UPDATE CASCADE,
    ADD CONSTRAINT FilmStock_filmTypeID_fk FOREIGN KEY (filmTypeID) REFERENCES FilmTypes (filmTypeID) ON DELETE RESTRICT ON UPDATE CASCADE,
    ADD CONSTRAINT FilmStock_filmSizeID_fk FOREIGN KEY (filmSizeID) REFERENCES FilmSizes (filmSizeID) ON DELETE RESTRICT ON UPDATE CASCADE;
SET FOREIGN_KEY_CHECKS=1;
ALTER TABLE FilmStock DROP COLUMN filmSize;


ALTER TABLE Films ADD COLUMN filmSizeID TINYINT UNSIGNED NOT NULL AFTER filmTypeID;

UPDATE Films SET filmSizeID = 3 WHERE cameraID IN 
(SELECT cameraID FROM Cameras WHERE filmSize = '35mm');

UPDATE Films SET filmSizeID = 5 WHERE cameraID IN 
(SELECT cameraID FROM Cameras WHERE filmSize = '120');

UPDATE Films SET filmSizeID = 6 WHERE cameraID IN 
(SELECT cameraID FROM Cameras WHERE filmSize = '220');

UPDATE Films SET filmSizeID = 7 WHERE cameraID IN 
(SELECT cameraID FROM Cameras WHERE filmSize = '4x5');

UPDATE Films SET filmSizeID = 9 WHERE cameraID IN 
(SELECT cameraID FROM Cameras WHERE filmSize = '8x10');

ALTER TABLE Films
    ADD CONSTRAINT Films_filmSizeID_fk FOREIGN KEY (filmSizeID) REFERENCES FilmSizes (filmSizeID) ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE Exposures ADD COLUMN filmSizeID TINYINT UNSIGNED DEFAULT NULL AFTER filmTypeID;
UPDATE Exposures SET filmSizeID = 7 WHERE filmID IN
(SELECT filmID FROM Films WHERE filmSizeID = 7);
ALTER TABLE Exposures 
    ADD CONSTRAINT Exposures_filmSizeID_fk FOREIGN KEY (filmSizeID) REFERENCES FilmSizes (filmSizeID) ON DELETE RESTRICT ON UPDATE CASCADE;



CREATE TABLE UserPreferences (
    userID INT UNSIGNED NOT NULL PRIMARY KEY,
    autoUpdateFilmStock ENUM('Yes', 'No') DEFAULT 'Yes',
    CONSTRAINT userprefs_userID_fk FOREIGN KEY (userID) REFERENCES Users (userID) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE='InnoDB';

DELIMITER //
CREATE TRIGGER CreateDefaultUserPreferences
    AFTER INSERT ON Users
        FOR EACH ROW
        BEGIN
            INSERT INTO UserPreferences (userID) VALUES (NEW.userID);
        END;
//
DELIMITER ;
