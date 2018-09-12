ALTER TABLE Prints
ADD COLUMN enlargerID TINYINT UNSIGNED AFTER enlargerLensID,
ADD CONSTRAINT Prints_Enlargers_fk FOREIGN KEY (userID, enlargerID) REFERENCES Enlargers (userID, enlargerID);

ALTER TABLE ContactSheets
ADD COLUMN enlargerID TINYINT UNSIGNED AFTER enlargerLensID,
ADD CONSTRAINT ContactSheets_Enlargers_fk FOREIGN KEY (userID, enlargerID) REFERENCES Enlargers (userID, enlargerID);

