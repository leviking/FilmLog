CREATE TABLE EnlargerLenses(
    enlargerLensID TINYINT UNSIGNED NOT NULL,
    userID INT UNSIGNED NOT NULL,
    name VARCHAR(64) NOT NULL,
    PRIMARY KEY (enlargerLensID, userID),
    CONSTRAINT EnlargerLenses_Users_fk FOREIGN KEY (userID) REFERENCES Users (userID) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE='InnoDB';

ALTER TABLE ContactSheets ADD COLUMN enlargerLensID TINYINT UNSIGNED DEFAULT NULL AFTER paperFilterID;
ALTER TABLE ContactSheets
ADD CONSTRAINT ContactSheets_EnlargerLenses_fk FOREIGN KEY (userID, enlargerLensID)
REFERENCES EnlargerLenses (userID, enlargerLensID)
ON DELETE CASCADE ON UPDATE CASCADE;


ALTER TABLE Prints ADD COLUMN enlargerLensID TINYINT UNSIGNED DEFAULT NULL AFTER paperFilterID;
ALTER TABLE Prints
ADD CONSTRAINT Prints_EnlargerLenses_fk FOREIGN KEY (userID, enlargerLensID) 
REFERENCES EnlargerLenses (userID, enlargerLensID)
ON DELETE CASCADE ON UPDATE CASCADE;

