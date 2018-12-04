CREATE TABLE MaxBlackTests(
  userID INT UNSIGNED NOT NULL,
  paperID TINYINT UNSIGNED,
  filmTypeID SMALLINT UNSIGNED,
  enlargerID TINYINT UNSIGNED DEFAULT NULL,
  enlargerLensID TINYINT UNSIGNED DEFAULT NULL,
  heatHeight SMALLINT UNSIGNED DEFAULT NULL,
  aperture DECIMAL(4,1) NOT NULL,
  size ENUM('4x5','4x6','5x7','8x10','11x14','Other') NOT NULL,
  exposureTime SMALLINT UNSIGNED NOT NULL,
  notes TEXT,
  PRIMARY KEY (userID, paperID, filmTypeID),
  CONSTRAINT mbt_users FOREIGN KEY (userID) REFERENCES Users (userID),
  CONSTRAINT mbt_papers FOREIGN KEY (paperID) REFERENCES Papers (paperID),
  CONSTRAINT mbt_filmTypes FOREIGN KEY (filmTypeID) REFERENCES FilmTypes (filmTypeID),
  CONSTRAINT mbt_enlargers FOREIGN KEY (userID, enlargerID) REFERENCES Enlargers (userID, enlargerID),
  CONSTRAINT mbt_enlargerLenses FOREIGN KEY (userID, enlargerLensID) REFERENCES EnlargerLenses (userID, enlargerLensID)
) ENGINE='InnoDB';
